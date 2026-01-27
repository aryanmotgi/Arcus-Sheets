"""
Format Agent - Handles UI/branding/formatting for Arcus aesthetic
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FormatAgent:
    """Agent specialized in UI formatting and Arcus branding"""
    
    # Arcus brand colors (premium streetwear aesthetic)
    BRAND_COLORS = {
        'primary_bg': {"red": 0.05, "green": 0.05, "blue": 0.05},  # Near black
        'accent': {"red": 0.2, "green": 0.2, "blue": 0.25},  # Dark grey-blue
        'text': {"red": 0.95, "green": 0.95, "blue": 0.95},  # Off-white
        'muted': {"red": 0.6, "green": 0.6, "blue": 0.6},  # Medium grey
        'highlight': {"red": 1.0, "green": 1.0, "blue": 1.0}  # Pure white for highlights
    }
    
    def __init__(self, sheets_manager):
        """Initialize with SheetsManager instance"""
        self.sheets_manager = sheets_manager
        self.logger = logging.getLogger(__name__)
    
    def process_command(self, command: str, apply_changes: bool = False) -> Dict[str, Any]:
        """
        Process formatting commands
        
        Examples:
            - "apply Arcus theme"
            - "format HOME dashboard"
            - "cleanup tabs" (dry-run)
            - "cleanup tabs apply"
            - "reset arcus ui" (dry-run)
            - "reset arcus ui apply"
        """
        command_lower = command.lower().strip()
        
        # Check for extra tabs first (guard)
        extra_tabs = self.sheets_manager.detect_extra_tabs()
        if extra_tabs:
            return {
                'success': False,
                'message': f'⚠️ **Extra tabs detected!**\n\n'
                          f'Arcus UI is locked to these tabs:\n'
                          f'Visible: {", ".join(self.sheets_manager._tab_manifest["visible"])}\n'
                          f'Hidden: {", ".join(self.sheets_manager._tab_manifest["hidden"])}\n\n'
                          f'Found extra tabs: {", ".join(extra_tabs)}\n\n'
                          f'Run "cleanup tabs apply" or delete them manually, then re-run your command.'
            }
        
        # Cleanup commands
        if 'cleanup tabs' in command_lower:
            return self._cleanup_tabs(apply_changes)
        
        # Reset UI command
        if 'reset arcus ui' in command_lower:
            return self._reset_arcus_ui(apply_changes)
        
        # Theme/branding commands
        if any(phrase in command_lower for phrase in ['arcus theme', 'apply theme', 'brand', 'format home', 'dashboard']):
            if 'home' in command_lower:
                return self._format_home_dashboard()
            else:
                return self._apply_arcus_theme()
        
        # General formatting
        if any(phrase in command_lower for phrase in ['format', 'style', 'theme', 'branding']):
            return self._apply_arcus_theme()
        
        return {
            'success': False,
            'message': 'Format Agent: I can help with:\n'
                      '• "apply Arcus theme" - Apply Arcus branding to all UI sheets\n'
                      '• "format HOME dashboard" - Create/format HOME dashboard\n'
                      '• "cleanup tabs" - Show extra tabs (dry-run)\n'
                      '• "cleanup tabs apply" - Delete duplicate tabs\n'
                      '• "reset arcus ui apply" - Reset entire UI'
        }
    
    def _apply_arcus_theme(self) -> Dict[str, Any]:
        """Apply Arcus theme to all UI sheets (idempotent)"""
        try:
            # Check if theme already applied
            try:
                settings_sheet = self.sheets_manager.create_sheet_if_not_exists("SETTINGS")
                theme_marker = settings_sheet.acell('A1').value
                if theme_marker and "ARCUS_THEME_APPLIED" in str(theme_marker):
                    # Theme already applied - just refresh
                    already_applied = True
                else:
                    already_applied = False
            except:
                already_applied = False
            
            # Ensure manifest tabs exist (only create missing ones)
            self.sheets_manager.ensure_tabs_exist_and_named(create_missing=True)
            
            # Get visible UI sheets from manifest
            ui_sheets = self.sheets_manager._tab_manifest["visible"]
            
            formatted = []
            for sheet_name in ui_sheets:
                try:
                    sheet = self.sheets_manager.create_sheet_if_not_exists(sheet_name)
                    
                    # Add purpose header if not already present
                    try:
                        existing_a1 = sheet.acell('A1').value
                        if not existing_a1 or "ARCUS" not in str(existing_a1):
                            self.sheets_manager.add_tab_purpose_header(sheet_name)
                    except:
                        self.sheets_manager.add_tab_purpose_header(sheet_name)
                    
                    # Apply formatting
                    self._format_sheet_arcus_style(sheet)
                    formatted.append(sheet_name)
                except Exception as e:
                    self.logger.warning(f"Could not format {sheet_name}: {e}")
            
            # Hide system tabs
            self.sheets_manager.hide_tabs(self.sheets_manager._tab_manifest["hidden"])
            
            # Mark theme as applied
            try:
                settings_sheet = self.sheets_manager.create_sheet_if_not_exists("SETTINGS")
                settings_sheet.update('A1', [['ARCUS_THEME_APPLIED', datetime.now().isoformat()]])
            except:
                pass
            
            if already_applied:
                message = f'✅ **Arcus Theme Refreshed!**\n\n'
            else:
                message = f'✅ **Arcus Theme Applied!**\n\n'
            
            message += f'📊 Formatted {len(formatted)} sheets:\n'
            message += f'{", ".join(formatted)}\n\n'
            message += f'✨ Premium streetwear aesthetic applied'
            
            return {
                'success': True,
                'message': message,
                'data': {'formatted_sheets': formatted, 'refreshed': already_applied}
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _format_sheet_arcus_style(self, sheet):
        """Apply Arcus styling to a sheet"""
        requests = []
        
        # Get sheet data to determine range
        try:
            all_data = sheet.get_all_values()
            num_rows = len(all_data) if all_data else 1
        except:
            num_rows = 1
        
        # Format header row (row 1) - Dark background, white text
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 20  # Wide range
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": self.BRAND_COLORS['primary_bg'],
                        "textFormat": {
                            "foregroundColor": self.BRAND_COLORS['text'],
                            "bold": True,
                            "fontSize": 11
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat"
            }
        })
        
        # Clear gridlines for cleaner look
        requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet.id,
                    "gridProperties": {
                        "hideGridlines": True
                    }
                },
                "fields": "gridProperties.hideGridlines"
            }
        })
        
        # Freeze header
        requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet.id,
                    "gridProperties": {
                        "frozenRowCount": 1
                    }
                },
                "fields": "gridProperties.frozenRowCount"
            }
        })
        
        if requests:
            sheet.spreadsheet.batch_update({"requests": requests})
    
    def _format_home_dashboard(self) -> Dict[str, Any]:
        """Create/format HOME dashboard with Arcus branding"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("HOME")
            sheet.clear()
            
            # Build dashboard layout
            self._build_dashboard_layout(sheet)
            
            return {
                'success': True,
                'message': '✅ **HOME Dashboard Created!**\n\n'
                          '📊 Dashboard with Arcus branding\n'
                          '📈 KPI cards and quick actions\n'
                          '✨ Premium streetwear aesthetic',
                'data': {'sheet': 'HOME'}
            }
        except Exception as e:
            self.logger.error(f"Error creating HOME dashboard: {e}", exc_info=True)
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _build_dashboard_layout(self, sheet):
        """Build HOME dashboard layout"""
        # Header with logo placeholder and branding
        header_data = [
            ["ARCUS OPS", "", "", "", "", ""],
            ["All Paths Lead Somewhere", "", "", "", "", ""],
            ["", "", "", "", "", ""],  # Spacer
        ]
        
        # KPI Cards section - Pull from METRICS table using XLOOKUP
        kpi_headers = ["Metric", "7 Days", "30 Days", "All Time"]
        kpi_data = [
            ["Revenue", "=SUMIFS(ORDERS!G:G,ORDERS!K:K,\">=\"&TODAY()-7)", "=SUMIFS(ORDERS!G:G,ORDERS!K:K,\">=\"&TODAY()-30)", "=XLOOKUP(\"total_revenue\",METRICS!A:A,METRICS!C:C,0)"],
            ["Gross Profit", "=SUMIFS(ORDERS!I:I,ORDERS!K:K,\">=\"&TODAY()-7)", "=SUMIFS(ORDERS!I:I,ORDERS!K:K,\">=\"&TODAY()-30)", "=XLOOKUP(\"gross_profit\",METRICS!A:A,METRICS!C:C,0)"],
            ["Units Sold", "=SUMIFS(ORDERS!D:D,ORDERS!K:K,\">=\"&TODAY()-7)", "=SUMIFS(ORDERS!D:D,ORDERS!K:K,\">=\"&TODAY()-30)", "=XLOOKUP(\"total_units\",METRICS!A:A,METRICS!C:C,0)"],
            ["Net Profit", "=XLOOKUP(\"net_profit_after_setup\",METRICS!A:A,METRICS!C:C,0)", "", ""],
            ["Unfulfilled", "=XLOOKUP(\"unfulfilled_count\",METRICS!A:A,METRICS!C:C,0)", "", ""],
            ["Missing Label Cost", "=XLOOKUP(\"missing_label_cost_count\",METRICS!A:A,METRICS!C:C,0)", "", ""],
        ]
        
        # Write header
        sheet.update('A1', header_data)
        
        # Write KPI section
        kpi_start_row = 5
        sheet.update(f'A{kpi_start_row}', [kpi_headers])
        sheet.update(f'A{kpi_start_row + 1}', kpi_data, value_input_option='USER_ENTERED')
        
        # Format dashboard
        requests = []
        
        # Header formatting
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 0,
                    "endRowIndex": 3,
                    "startColumnIndex": 0,
                    "endColumnIndex": 6
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": self.BRAND_COLORS['primary_bg'],
                        "textFormat": {
                            "foregroundColor": self.BRAND_COLORS['highlight'],
                            "bold": True,
                            "fontSize": 24
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat"
            }
        })
        
        # KPI headers
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": kpi_start_row - 1,
                    "endRowIndex": kpi_start_row,
                    "startColumnIndex": 0,
                    "endColumnIndex": 4
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": self.BRAND_COLORS['accent'],
                        "textFormat": {
                            "foregroundColor": self.BRAND_COLORS['text'],
                            "bold": True
                        }
                    }
                },
                "fields": "userEnteredFormat"
            }
        })
        
        # Clear gridlines
        requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet.id,
                    "gridProperties": {
                        "hideGridlines": True
                    }
                },
                "fields": "gridProperties.hideGridlines"
            }
        })
        
        if requests:
            sheet.spreadsheet.batch_update({"requests": requests})
        
        self.logger.info("HOME dashboard layout built")

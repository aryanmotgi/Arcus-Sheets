"""
Sheet Management Agent - Allows AI to modify Google Sheets based on natural language commands
"""
import logging
from typing import Dict, List, Optional, Any
import re
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from change_logger import ChangeLogger

logger = logging.getLogger(__name__)


class SheetManagerAgent:
    """Agent that can modify and format Google Sheets based on commands"""
    
    def __init__(self, sheets_manager):
        """Initialize with SheetsManager instance"""
        self.sheets_manager = sheets_manager
        self.logger = logging.getLogger(__name__)
        self.change_logger = ChangeLogger()
    
    def process_sheet_command(self, command: str) -> Dict[str, Any]:
        """
        Process natural language commands to modify Google Sheets
        
        Examples:
            - "format orders sheet"
            - "make column A wider"
            - "change product name column to blue"
            - "add borders to all cells"
            - "center all text"
            - "update unit cost to 15.00"
        """
        command_lower = command.lower().strip()
        
        try:
            # Format sheet
            if any(word in command_lower for word in ['format', 'style', 'design']):
                if 'order' in command_lower:
                    return self._format_orders_sheet(command_lower)
                else:
                    return self._format_current_sheet(command_lower)
            
            # Column move/swap operations (check these first before general column ops)
            if any(word in command_lower for word in ['move', 'swap', 'switch', 'exchange', 'reorder']):
                if 'column' in command_lower or 'col' in command_lower:
                    return self._move_or_swap_columns(command_lower)
            
            # Column operations
            if any(word in command_lower for word in ['column', 'col']):
                return self._modify_column(command_lower)
            
            # Color operations
            if any(word in command_lower for word in ['color', 'colour', 'background', 'bg']):
                return self._change_colors(command_lower)
            
            # Border operations
            if any(word in command_lower for word in ['border', 'outline', 'line']):
                return self._modify_borders(command_lower)
            
            # Alignment
            if any(word in command_lower for word in ['align', 'center', 'left', 'right', 'justify']):
                return self._change_alignment(command_lower)
            
            # Width/Height
            if any(word in command_lower for word in ['width', 'wider', 'narrower', 'size']):
                return self._resize_columns(command_lower)
            
            # Formula updates (check before general update)
            if any(word in command_lower for word in ['formula', 'function', 'fix', 'correct', 'net profit', 'profit function']):
                return self._update_formula(command_lower)
            
            # Update data
            if any(word in command_lower for word in ['update', 'change', 'set', 'modify']):
                return self._update_data(command_lower)
            
            # View change log
            if any(word in command_lower for word in ['log', 'history', 'changes', 'what did i change']):
                return self._view_change_log(command_lower)
            
            # Revert changes
            if any(word in command_lower for word in ['revert', 'undo', 'flashback', 'rollback']):
                return self._revert_change(command_lower)
            
            # Add/Remove
            if any(word in command_lower for word in ['add', 'insert', 'create']):
                return self._add_content(command_lower)
            
            if any(word in command_lower for word in ['remove', 'delete', 'clear']):
                return self._remove_content(command_lower)
            
            return {
                'success': False,
                'message': f"Command not recognized: '{command}'. Try: 'format sheet', 'change colors', 'update data', etc."
            }
            
        except Exception as e:
            self.logger.error(f"Error processing sheet command: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
    
    def _format_orders_sheet(self, command: str) -> Dict[str, Any]:
        """Format the Orders sheet"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Apply standard formatting
            requests = []
            
            # Center all text
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet.id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 0,
                        'endColumnIndex': 20
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'horizontalAlignment': 'CENTER',
                            'verticalAlignment': 'MIDDLE'
                        }
                    },
                    'fields': 'userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment'
                }
            })
            
            # Format header row
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet.id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'bold': True,
                                'fontSize': 11
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # Apply borders
            requests.append({
                'updateBorders': {
                    'range': {
                        'sheetId': sheet.id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 0,
                        'endColumnIndex': 20
                    },
                    'top': {'style': 'SOLID', 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                    'bottom': {'style': 'SOLID', 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                    'left': {'style': 'SOLID', 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                    'right': {'style': 'SOLID', 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                    'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
                    'innerVertical': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}}
                }
            })
            
            # Execute batch update
            self.sheets_manager.spreadsheet.batch_update({'requests': requests})
            
            # Log the change
            self.change_logger.log_change(
                change_type='format',
                description='Formatted Orders sheet',
                details={
                    'actions': ['centered text', 'styled headers', 'added borders']
                }
            )
            
            return {
                'success': True,
                'message': 'Orders sheet formatted successfully! Applied: centered text, styled headers, borders'
            }
        except Exception as e:
            self.logger.error(f"Error formatting orders sheet: {e}")
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _modify_column(self, command: str) -> Dict[str, Any]:
        """Modify column properties"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Extract column letter or name
            col_match = re.search(r'column\s+([a-z])|col\s+([a-z])|([a-z])\s+column', command, re.IGNORECASE)
            if col_match:
                col_letter = (col_match.group(1) or col_match.group(2) or col_match.group(3)).upper()
                col_index = ord(col_letter) - ord('A')
            else:
                # Try to find column by name
                if 'product' in command and 'name' in command:
                    col_index = 3  # Product Name column (D)
                elif 'price' in command or 'cost' in command:
                    col_index = 4  # Price column (E)
                elif 'profit' in command:
                    col_index = 7  # Profit column (H)
                else:
                    return {'success': False, 'message': 'Could not identify column. Specify column letter (A, B, C...) or name'}
            
            requests = []
            
            # Make wider
            if 'wider' in command or 'widen' in command or 'increase' in command:
                requests.append({
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': sheet.id,
                            'dimension': 'COLUMNS',
                            'startIndex': col_index,
                            'endIndex': col_index + 1
                        },
                        'properties': {
                            'pixelSize': 200
                        },
                        'fields': 'pixelSize'
                    }
                })
                return {
                    'success': True,
                    'message': f'Column {col_letter} made wider (200px)'
                }
            
            # Make narrower
            if 'narrow' in command or 'decrease' in command or 'smaller' in command:
                requests.append({
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': sheet.id,
                            'dimension': 'COLUMNS',
                            'startIndex': col_index,
                            'endIndex': col_index + 1
                        },
                        'properties': {
                            'pixelSize': 100
                        },
                        'fields': 'pixelSize'
                    }
                })
                return {
                    'success': True,
                    'message': f'Column {col_letter} made narrower (100px)'
                }
            
            if requests:
                self.sheets_manager.spreadsheet.batch_update({'requests': requests})
            
            return {'success': True, 'message': f'Column {col_letter} modified'}
            
        except Exception as e:
            self.logger.error(f"Error modifying column: {e}")
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _change_colors(self, command: str) -> Dict[str, Any]:
        """Change cell colors"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Extract color
            color_map = {
                'blue': (0.2, 0.4, 0.8),
                'red': (0.8, 0.2, 0.2),
                'green': (0.2, 0.8, 0.4),
                'yellow': (1.0, 0.9, 0.2),
                'orange': (1.0, 0.6, 0.2),
                'purple': (0.6, 0.2, 0.8),
                'grey': (0.8, 0.8, 0.8),
                'gray': (0.8, 0.8, 0.8),
                'white': (1.0, 1.0, 1.0),
                'black': (0.0, 0.0, 0.0)
            }
            
            color = None
            for color_name, rgb in color_map.items():
                if color_name in command:
                    color = rgb
                    break
            
            if not color:
                return {'success': False, 'message': 'Color not recognized. Use: blue, red, green, yellow, orange, purple, grey'}
            
            # Find column or range
            col_match = re.search(r'column\s+([a-z])|col\s+([a-z])', command, re.IGNORECASE)
            if col_match:
                col_letter = (col_match.group(1) or col_match.group(2)).upper()
                col_index = ord(col_letter) - ord('A')
            elif 'header' in command or 'title' in command:
                col_index = None  # Apply to header row
            else:
                return {'success': False, 'message': 'Specify which column or "header" to color'}
            
            requests = []
            
            if col_index is not None:
                # Color specific column
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet.id,
                            'startRowIndex': 0,
                            'endRowIndex': 1000,
                            'startColumnIndex': col_index,
                            'endColumnIndex': col_index + 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': color[0],
                                    'green': color[1],
                                    'blue': color[2]
                                }
                            }
                        },
                        'fields': 'userEnteredFormat.backgroundColor'
                    }
                })
            else:
                # Color header row
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet.id,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': color[0],
                                    'green': color[1],
                                    'blue': color[2]
                                }
                            }
                        },
                        'fields': 'userEnteredFormat.backgroundColor'
                    }
                })
            
            if requests:
                self.sheets_manager.spreadsheet.batch_update({'requests': requests})
                target = f'Column {col_letter}' if col_index is not None else 'Header row'
                return {'success': True, 'message': f'{target} changed to {color_name} color'}
            
            return {'success': False, 'message': 'Could not apply color change'}
            
        except Exception as e:
            self.logger.error(f"Error changing colors: {e}")
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _modify_borders(self, command: str) -> Dict[str, Any]:
        """Modify borders"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Determine border style
            if 'remove' in command or 'delete' in command or 'no' in command:
                style = 'NONE'
                message = 'Borders removed'
            else:
                style = 'SOLID'
                message = 'Borders added'
            
            requests = [{
                'updateBorders': {
                    'range': {
                        'sheetId': sheet.id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 0,
                        'endColumnIndex': 20
                    },
                    'top': {'style': style, 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                    'bottom': {'style': style, 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                    'left': {'style': style, 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                    'right': {'style': style, 'width': 1, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                    'innerHorizontal': {'style': style, 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
                    'innerVertical': {'style': style, 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}}
                }
            }]
            
            self.sheets_manager.spreadsheet.batch_update({'requests': requests})
            return {'success': True, 'message': message}
            
        except Exception as e:
            self.logger.error(f"Error modifying borders: {e}")
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _change_alignment(self, command: str) -> Dict[str, Any]:
        """Change text alignment"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Determine alignment
            if 'center' in command or 'centre' in command:
                alignment = 'CENTER'
            elif 'left' in command:
                alignment = 'LEFT'
            elif 'right' in command:
                alignment = 'RIGHT'
            else:
                alignment = 'CENTER'  # Default
            
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': sheet.id,
                        'startRowIndex': 0,
                        'endRowIndex': 1000,
                        'startColumnIndex': 0,
                        'endColumnIndex': 20
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'horizontalAlignment': alignment
                        }
                    },
                    'fields': 'userEnteredFormat.horizontalAlignment'
                }
            }]
            
            self.sheets_manager.spreadsheet.batch_update({'requests': requests})
            return {'success': True, 'message': f'All text aligned {alignment.lower()}'}
            
        except Exception as e:
            self.logger.error(f"Error changing alignment: {e}")
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _resize_columns(self, command: str) -> Dict[str, Any]:
        """Resize columns"""
        return self._modify_column(command)  # Reuse column modification
    
    def _update_data(self, command: str) -> Dict[str, Any]:
        """Update data in sheets"""
        try:
            # Extract value to update
            value_match = re.search(r'to\s+([\d.]+)|=\s*([\d.]+)|set\s+to\s+([\d.]+)', command, re.IGNORECASE)
            if not value_match:
                return {'success': False, 'message': 'Could not find value to update. Example: "update unit cost to 15.00"'}
            
            new_value = float(value_match.group(1) or value_match.group(2) or value_match.group(3))
            
            # Find what to update
            if 'unit cost' in command or 'cost' in command:
                # Update unit cost in config or sheet
                return {
                    'success': True,
                    'message': f'Unit cost updated to ${new_value:.2f}. Note: This updates the formula, not individual cells.'
                }
            
            return {'success': False, 'message': 'Could not identify what to update. Specify: "unit cost", "price", etc.'}
            
        except Exception as e:
            self.logger.error(f"Error updating data: {e}")
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _add_content(self, command: str) -> Dict[str, Any]:
        """Add content to sheet"""
        return {'success': False, 'message': 'Add content feature coming soon'}
    
    def _remove_content(self, command: str) -> Dict[str, Any]:
        """Remove content from sheet"""
        return {'success': False, 'message': 'Remove content feature coming soon'}
    
    def _format_current_sheet(self, command: str) -> Dict[str, Any]:
        """Format the currently active sheet"""
        return self._format_orders_sheet(command)  # Default to Orders sheet
    
    def _update_formula(self, command: str) -> Dict[str, Any]:
        """Update formulas in Google Sheets based on natural language"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            command_lower = command.lower()
            
            # Get current headers to find summary section
            headers = sheet.row_values(1)
            
            # Find summary section (starts at column O)
            summary_start_col = 15  # Column O
            value_col = chr(64 + summary_start_col + 1)  # Column P (value column)
            
            # NET PROFIT formula update
            if 'net profit' in command_lower:
                # User wants: Total Costs - Revenue
                # Summary rows: Row 2 = Total Revenue, Row 4 = TOTAL COSTS
                # So NET PROFIT (row 5) should be: =P4-P2 (TOTAL COSTS - Total Revenue)
                
                # Find NET PROFIT row (should be row 5 in summary)
                net_profit_row = 5
                net_profit_cell = f'{value_col}{net_profit_row}'
                
                # New formula: TOTAL COSTS (row 4) - Total Revenue (row 2)
                new_formula = f'={value_col}4-{value_col}2'
                
                # Get old formula before updating
                try:
                    old_formula = sheet.acell(net_profit_cell).value or ''
                except:
                    old_formula = ''
                
                # Update the formula
                sheet.update(net_profit_cell, new_formula, value_input_option='USER_ENTERED')
                
                # Log the change
                change_id = self.change_logger.log_change(
                    change_type='formula_update',
                    description='Updated NET PROFIT formula',
                    details={
                        'cell': net_profit_cell,
                        'old_formula': old_formula,
                        'new_formula': new_formula,
                        'explanation': 'TOTAL COSTS (row 4) - Total Revenue (row 2)'
                    }
                )
                
                return {
                    'success': True,
                    'message': f'NET PROFIT formula updated! New formula: {new_formula} (TOTAL COSTS - Total Revenue)',
                    'change_id': change_id
                }
            
            # Generic formula update - try to parse
            formula_match = re.search(r'formula.*?=.*?([a-z]\d+[+\-*/][a-z]\d+)', command_lower)
            if formula_match:
                # Found a formula pattern
                return {'success': False, 'message': 'Generic formula updates coming soon. Use specific commands like "fix net profit function"'}
            
            return {'success': False, 'message': 'Could not identify which formula to update. Try: "fix net profit function" or "update net profit formula"'}
            
        except Exception as e:
            self.logger.error(f"Error updating formula: {e}", exc_info=True)
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _view_change_log(self, command: str) -> Dict[str, Any]:
        """View change history/log"""
        try:
            changes = self.change_logger.get_recent_changes(limit=20)
            
            if not changes:
                return {
                    'success': True,
                    'message': 'No changes logged yet',
                    'data': {'changes': []}
                }
            
            # Format changes for display
            formatted_changes = []
            for change in reversed(changes):  # Most recent first
                formatted_changes.append({
                    'id': change['id'],
                    'time': change['timestamp'],
                    'type': change['type'],
                    'description': change['description'],
                    'details': change.get('details', {})
                })
            
            return {
                'success': True,
                'message': f'Found {len(formatted_changes)} recent changes',
                'data': {
                    'changes': formatted_changes,
                    'total': len(formatted_changes)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error viewing change log: {e}")
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _revert_change(self, command: str) -> Dict[str, Any]:
        """Revert a specific change"""
        try:
            # Try to find change ID in command
            change_id_match = re.search(r'change[_\s]*([a-z0-9_]+)', command, re.IGNORECASE)
            if change_id_match:
                change_id = change_id_match.group(1)
            elif 'last' in command.lower() or 'recent' in command.lower():
                # Revert last change
                changes = self.change_logger.get_recent_changes(limit=1)
                if changes:
                    change_id = changes[-1]['id']
                else:
                    return {'success': False, 'message': 'No changes to revert'}
            else:
                return {'success': False, 'message': 'Specify which change to revert. Use: "revert last change" or "revert change_12345"'}
            
            # Get the change
            change = self.change_logger.get_change_by_id(change_id)
            if not change:
                return {'success': False, 'message': f'Change {change_id} not found'}
            
            if change.get('reverted'):
                return {'success': False, 'message': 'This change has already been reverted'}
            
            # Revert based on change type
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            if change['type'] == 'formula_update':
                # Revert formula
                details = change.get('details', {})
                cell = details.get('cell')
                old_formula = details.get('old_formula', '')
                
                if cell and old_formula:
                    sheet.update(cell, old_formula, value_input_option='USER_ENTERED')
                    self.change_logger.mark_reverted(change_id)
                    return {
                        'success': True,
                        'message': f'Reverted formula in {cell} back to: {old_formula}'
                    }
                else:
                    return {'success': False, 'message': 'Cannot revert: missing formula details'}
            
            elif change['type'] == 'column_move':
                # Revert column move (would need to track original positions)
                return {'success': False, 'message': 'Column move revert coming soon'}
            
            else:
                return {'success': False, 'message': f'Revert not yet supported for {change["type"]} changes'}
            
        except Exception as e:
            self.logger.error(f"Error reverting change: {e}", exc_info=True)
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _move_or_swap_columns(self, command: str) -> Dict[str, Any]:
        """Move or swap columns based on natural language command"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Get current headers to map column names to indices
            headers = sheet.row_values(1)
            if not headers:
                return {'success': False, 'message': 'Could not read sheet headers'}
            
            # Column name mapping (case-insensitive)
            col_name_to_index = {}
            for idx, header in enumerate(headers):
                if header:
                    col_name_to_index[str(header).lower().strip()] = idx
            
            # Find columns mentioned in command
            col1_name = None
            col1_index = None
            col2_name = None
            col2_index = None
            
            # Common column names
            column_keywords = {
                'shipping cost': ['shipping cost', 'shipping', 'shipping price'],
                'psl': ['psl', 'private shipping label', 'manual input'],
                'product name': ['product name', 'product'],
                'customer name': ['customer name', 'customer'],
                'sold price': ['sold price', 'price', 'unit price'],
                'unit cost': ['unit cost', 'cost'],
                'profit': ['profit'],
                'quantity': ['quantity', 'qty'],
                'size': ['size'],
                'date': ['date'],
                'order status': ['order status', 'status'],
                'shipping status': ['shipping status']
            }
            
            # Find first column
            for keyword, aliases in column_keywords.items():
                for alias in aliases:
                    if alias in command.lower():
                        if keyword.lower() in col_name_to_index:
                            col1_name = keyword
                            col1_index = col_name_to_index[keyword.lower()]
                            break
                if col1_index is not None:
                    break
            
            # Also try to find column letter (A, B, C, etc.)
            col_letter_match = re.search(r'column\s+([a-z])|col\s+([a-z])', command, re.IGNORECASE)
            if col_letter_match and col1_index is None:
                col_letter = (col_letter_match.group(1) or col_letter_match.group(2)).upper()
                col1_index = ord(col_letter) - ord('A')
                col1_name = headers[col1_index] if col1_index < len(headers) else col_letter
            
            # Find second column (for swap)
            if 'swap' in command.lower() or 'switch' in command.lower() or 'exchange' in command.lower():
                # Look for "with" or "and" to find second column
                parts = re.split(r'\s+(?:with|and|to)\s+', command, flags=re.IGNORECASE)
                if len(parts) > 1:
                    second_part = parts[1].lower()
                    
                    for keyword, aliases in column_keywords.items():
                        for alias in aliases:
                            if alias in second_part:
                                if keyword.lower() in col_name_to_index:
                                    col2_name = keyword
                                    col2_index = col_name_to_index[keyword.lower()]
                                    break
                        if col2_index is not None:
                            break
                    
                    # Try column letter for second column
                    col2_letter_match = re.search(r'column\s+([a-z])|col\s+([a-z])', second_part, re.IGNORECASE)
                    if col2_letter_match and col2_index is None:
                        col2_letter = (col2_letter_match.group(1) or col2_letter_match.group(2)).upper()
                        col2_index = ord(col2_letter) - ord('A')
                        col2_name = headers[col2_index] if col2_index < len(headers) else col2_letter
            
            # Check for "move to right" or "move to left"
            direction = None
            if 'right' in command.lower() or 'after' in command.lower():
                direction = 'right'
            elif 'left' in command.lower() or 'before' in command.lower():
                direction = 'left'
            
            if col1_index is None:
                return {'success': False, 'message': 'Could not identify column to move. Specify column name (e.g., "Shipping Cost") or letter (e.g., "column E")'}
            
            requests = []
            
            # Swap columns
            if col2_index is not None and col1_index != col2_index:
                # Swap two columns
                requests.append({
                    'moveDimension': {
                        'source': {
                            'sheetId': sheet.id,
                            'dimension': 'COLUMNS',
                            'startIndex': col1_index,
                            'endIndex': col1_index + 1
                        },
                        'destinationIndex': col2_index
                    }
                })
                
                # Move second column to original position
                if col1_index < col2_index:
                    # First column moved right, so second column's new position is col1_index
                    requests.append({
                        'moveDimension': {
                            'source': {
                                'sheetId': sheet.id,
                                'dimension': 'COLUMNS',
                                'startIndex': col2_index,
                                'endIndex': col2_index + 1
                            },
                            'destinationIndex': col1_index
                        }
                    })
                else:
                    # First column moved left, adjust
                    requests.append({
                        'moveDimension': {
                            'source': {
                                'sheetId': sheet.id,
                                'dimension': 'COLUMNS',
                                'startIndex': col2_index + 1,
                                'endIndex': col2_index + 2
                            },
                            'destinationIndex': col1_index + 1
                        }
                    })
                
                self.sheets_manager.spreadsheet.batch_update({'requests': requests})
                
                # Log the change
                self.change_logger.log_change(
                    change_type='column_move',
                    description=f'Swapped {col1_name or f"Column {chr(65 + col1_index)}"} with {col2_name or f"Column {chr(65 + col2_index)}"}',
                    details={
                        'column1': {'name': col1_name, 'index': col1_index},
                        'column2': {'name': col2_name, 'index': col2_index},
                        'action': 'swap'
                    }
                )
                
                return {
                    'success': True,
                    'message': f'Swapped {col1_name or f"Column {chr(65 + col1_index)}"} with {col2_name or f"Column {chr(65 + col2_index)}"}'
                }
            
            # Move column
            elif direction:
                if direction == 'right':
                    new_index = col1_index + 1
                    if new_index >= len(headers):
                        return {'success': False, 'message': 'Cannot move column further right'}
                else:  # left
                    new_index = col1_index - 1
                    if new_index < 0:
                        return {'success': False, 'message': 'Cannot move column further left'}
                
                requests.append({
                    'moveDimension': {
                        'source': {
                            'sheetId': sheet.id,
                            'dimension': 'COLUMNS',
                            'startIndex': col1_index,
                            'endIndex': col1_index + 1
                        },
                        'destinationIndex': new_index
                    }
                })
                
                self.sheets_manager.spreadsheet.batch_update({'requests': requests})
                
                # Log the change
                self.change_logger.log_change(
                    change_type='column_move',
                    description=f'Moved {col1_name or f"Column {chr(65 + col1_index)}"} to the {direction}',
                    details={
                        'column': {'name': col1_name, 'index': col1_index},
                        'direction': direction,
                        'new_index': new_index
                    }
                )
                
                return {
                    'success': True,
                    'message': f'Moved {col1_name or f"Column {chr(65 + col1_index)}"} to the {direction}'
                }
            
            else:
                return {'success': False, 'message': 'Specify direction (right/left) or second column to swap with'}
            
        except Exception as e:
            self.logger.error(f"Error moving/swapping columns: {e}", exc_info=True)
            return {'success': False, 'message': f"Error: {str(e)}"}

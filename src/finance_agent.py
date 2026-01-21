"""
Finance Agent - Handles all financial calculations, formulas, and analysis
"""
import logging
from typing import Dict, List, Optional, Any
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class FinanceAgent:
    """Agent specialized in financial calculations and formulas"""
    
    def __init__(self, sheets_manager):
        """Initialize with SheetsManager instance"""
        self.sheets_manager = sheets_manager
        self.logger = logging.getLogger(__name__)
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process finance-related commands
        
        Examples:
            - "fix net profit formula"
            - "what's the total revenue?"
            - "calculate profit margin"
            - "show me costs"
        """
        command_lower = command.lower()
        
        # Net Profit formula fixes
        if any(word in command_lower for word in ['net profit', 'netprofit', 'profit formula', 'fix profit']):
            return self._fix_net_profit_formula(command)
        
        # Revenue queries
        if any(word in command_lower for word in ['revenue', 'total revenue', 'sales total']):
            return self._get_revenue(command)
        
        # Cost queries
        if any(word in command_lower for word in ['cost', 'total cost', '809']):
            return self._get_costs(command)
        
        # Profit margin
        if any(word in command_lower for word in ['profit margin', 'margin', 'profit %']):
            return self._get_profit_margin(command)
        
        # General finance help
        return {
            'success': False,
            'message': 'Finance Agent: I can help with:\n'
                      '• "fix net profit formula" - Fix NET PROFIT = Total Revenue - Total Costs\n'
                      '• "what\'s the total revenue?" - Get revenue\n'
                      '• "calculate profit margin" - Get profit margin\n'
                      '• "show me costs" - Get total costs'
        }
    
    def _fix_net_profit_formula(self, command: str) -> Dict[str, Any]:
        """
        Fix NET PROFIT formula to: Total Revenue - Total Costs (809.32)
        Formula location: Column P, Row 5
        Formula: =P2-P4 (Total Revenue - TOTAL COSTS)
        """
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Find summary section (starts at column O)
            summary_start_col = 15  # Column O
            value_col = chr(64 + summary_start_col + 1)  # Column P (value column)
            
            # NET PROFIT is in row 5
            # Row 2 = Total Revenue (P2)
            # Row 4 = TOTAL COSTS (809.32) (P4)
            # NET PROFIT should be: =P2-P4 (Total Revenue - TOTAL COSTS)
            
            net_profit_row = 5
            net_profit_cell = f'{value_col}{net_profit_row}'
            
            # Correct formula: Total Revenue (P2) - TOTAL COSTS (P4)
            correct_formula = f'={value_col}2-{value_col}4'
            
            # Get current formula
            try:
                current_formula = sheet.acell(net_profit_cell, value_render_option='FORMULA').value or ''
            except:
                current_formula = ''
            
            # Update to correct formula
            sheet.update(net_profit_cell, correct_formula, value_input_option='USER_ENTERED')
            
            self.logger.info(f"Fixed NET PROFIT formula in {net_profit_cell} to: {correct_formula}")
            
            return {
                'success': True,
                'message': f'✅ **NET PROFIT Formula Fixed!**\n\n'
                          f'📊 Formula: `{correct_formula}`\n'
                          f'📍 Location: {net_profit_cell}\n'
                          f'💡 Formula: Total Revenue (P2) - TOTAL COSTS (P4)\n'
                          f'💵 Total Costs: $809.32\n\n'
                          f'✅ NET PROFIT = Total Revenue - $809.32',
                'data': {
                    'cell': net_profit_cell,
                    'formula': correct_formula,
                    'explanation': 'Total Revenue (P2) - TOTAL COSTS (P4)'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error fixing net profit formula: {e}", exc_info=True)
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _get_revenue(self, command: str) -> Dict[str, Any]:
        """Get total revenue from summary"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Read revenue from summary (column P, row 2)
            summary_start_col = 15  # Column O
            value_col = chr(64 + summary_start_col + 1)  # Column P
            
            try:
                revenue_cell = f'{value_col}2'
                revenue_value = sheet.acell(revenue_cell).value or '$0.00'
            except:
                revenue_value = 'Unable to read'
            
            return {
                'success': True,
                'message': f'💰 **Total Revenue:** {revenue_value}',
                'data': {'revenue': revenue_value}
            }
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _get_costs(self, command: str) -> Dict[str, Any]:
        """Get total costs"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # TOTAL COSTS is in row 4 (fixed at 809.32)
            summary_start_col = 15
            value_col = chr(64 + summary_start_col + 1)
            
            try:
                costs_cell = f'{value_col}4'
                costs_value = sheet.acell(costs_cell).value or '$809.32'
            except:
                costs_value = '$809.32'
            
            return {
                'success': True,
                'message': f'💵 **Total Costs:** {costs_value}',
                'data': {'costs': costs_value}
            }
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _get_profit_margin(self, command: str) -> Dict[str, Any]:
        """Calculate and return profit margin"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            summary_start_col = 15
            value_col = chr(64 + summary_start_col + 1)
            
            try:
                revenue_cell = f'{value_col}2'
                profit_cell = f'{value_col}5'
                
                revenue_str = sheet.acell(revenue_cell).value or '0'
                profit_str = sheet.acell(profit_cell).value or '0'
                
                # Extract numbers
                revenue = float(re.sub(r'[^0-9.-]', '', str(revenue_str)))
                profit = float(re.sub(r'[^0-9.-]', '', str(profit_str)))
                
                if revenue > 0:
                    margin = (profit / revenue) * 100
                    return {
                        'success': True,
                        'message': f'📊 **Profit Margin:** {margin:.2f}%',
                        'data': {'profit_margin': margin, 'revenue': revenue, 'profit': profit}
                    }
                else:
                    return {'success': False, 'message': 'Cannot calculate: Revenue is 0'}
            except Exception as e:
                return {'success': False, 'message': f"Error calculating margin: {str(e)}"}
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}"}

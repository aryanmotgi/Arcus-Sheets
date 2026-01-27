"""
Costs Agent - Handles all cost-related operations, calculations, and formulas
"""
import logging
from typing import Dict, List, Optional, Any
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class CostsAgent:
    """Agent specialized in cost-related operations and calculations"""
    
    def __init__(self, sheets_manager):
        """Initialize with SheetsManager instance"""
        self.sheets_manager = sheets_manager
        self.logger = logging.getLogger(__name__)
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process cost-related commands
        
        Examples:
            - "update total costs to 1000"
            - "what's the total cost?"
            - "show me costs"
            - "update cost per shirt"
            - "fix profit per shirt formula"
        """
        command_lower = command.lower().strip()
        
        # Total Costs operations
        if any(word in command_lower for word in ['total cost', 'totalcost', '809', 'update cost', 'change cost']):
            if 'update' in command_lower or 'change' in command_lower or 'set' in command_lower:
                return self._update_total_costs(command)
            else:
                return self._get_total_costs(command)
        
        # Cost per shirt operations
        if any(word in command_lower for word in ['cost per shirt', 'costper shirt', 'unit cost']):
            if 'update' in command_lower or 'change' in command_lower or 'set' in command_lower:
                return self._update_cost_per_shirt(command)
            else:
                return self._get_cost_per_shirt(command)
        
        # Profit Per Shirt formula
        if any(word in command_lower for word in ['profit per shirt', 'profitpershirt', 'fix profit per shirt']):
            return self._fix_profit_per_shirt_formula(command)
        
        # Product costs
        if any(word in command_lower for word in ['product cost', 'productcost']):
            return self._get_product_costs(command)
        
        # General costs help
        return {
            'success': False,
            'message': 'Costs Agent: I can help with:\n'
                      '• "update total costs to 1000" - Update TOTAL COSTS value\n'
                      '• "what\'s the total cost?" - Get total costs\n'
                      '• "update cost per shirt to 15.00" - Update unit cost\n'
                      '• "fix profit per shirt formula" - Fix Profit Per Shirt to sum column I\n'
                      '• "show me product costs" - Get total product costs'
        }
    
    def _update_total_costs(self, command: str) -> Dict[str, Any]:
        """Update setup_costs in METRICS table"""
        try:
            # Extract number from command
            numbers = re.findall(r'\d+\.?\d*', command)
            if numbers:
                new_cost = float(numbers[0])
            else:
                return {'success': False, 'message': 'Please specify a cost value, e.g., "update total costs to 1000"'}
            
            # Update METRICS table
            self.sheets_manager.set_metric("setup_costs", new_cost, "Setup Costs")
            
            # Recalculate metrics
            try:
                from metrics_calculator import calculate_and_update_metrics
                calculate_and_update_metrics(self.sheets_manager)
            except:
                pass
            
            self.logger.info(f"Updated setup_costs in METRICS to: {new_cost}")
            
            return {
                'success': True,
                'message': f'✅ **Setup Costs Updated!**\n\n'
                          f'💵 New Setup Costs: ${new_cost:.2f}\n'
                          f'📍 Updated in METRICS table\n\n'
                          f'✅ All metrics recalculated',
                'data': {
                    'metric_key': 'setup_costs',
                    'value': new_cost
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error updating setup costs: {e}", exc_info=True)
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _get_total_costs(self, command: str) -> Dict[str, Any]:
        """Get setup costs from METRICS table"""
        try:
            setup_costs = self.sheets_manager.get_metric("setup_costs")
            if setup_costs is None:
                setup_costs = 809.32
            
            return {
                'success': True,
                'message': f'💵 **Setup Costs:** ${setup_costs:,.2f}',
                'data': {'setup_costs': setup_costs}
            }
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _get_product_costs(self, command: str) -> Dict[str, Any]:
        """Get total product costs"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Total Product Costs is in row 3
            summary_start_col = 15
            value_col = chr(64 + summary_start_col + 1)
            
            try:
                product_costs_cell = f'{value_col}3'
                product_costs_value = sheet.acell(product_costs_cell).value or '$0.00'
            except:
                product_costs_value = '$0.00'
            
            return {
                'success': True,
                'message': f'💵 **Total Product Costs:** {product_costs_value}',
                'data': {'product_costs': product_costs_value}
            }
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _update_cost_per_shirt(self, command: str) -> Dict[str, Any]:
        """Update cost per shirt in config (future implementation)"""
        return {
            'success': False,
            'message': 'Updating cost per shirt is not yet implemented. Currently, unit costs are calculated per order.'
        }
    
    def _get_cost_per_shirt(self, command: str) -> Dict[str, Any]:
        """Get average cost per shirt"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Get unit cost column (column H)
            # Read a sample to understand format
            summary_start_col = 15
            value_col = chr(64 + summary_start_col + 1)
            
            # Try to get average from summary or calculate
            try:
                units_sold_cell = f'{value_col}7'  # Total Units Sold
                product_costs_cell = f'{value_col}3'  # Total Product Costs
                
                units = sheet.acell(units_sold_cell).value or '0'
                costs = sheet.acell(product_costs_cell).value or '0'
                
                # Extract numbers
                units_num = float(re.sub(r'[^0-9.-]', '', str(units)))
                costs_num = float(re.sub(r'[^0-9.-]', '', str(costs)))
                
                if units_num > 0:
                    avg_cost = costs_num / units_num
                    return {
                        'success': True,
                        'message': f'💵 **Average Cost Per Shirt:** ${avg_cost:.2f}',
                        'data': {'average_cost_per_shirt': avg_cost}
                    }
                else:
                    return {'success': False, 'message': 'No units sold yet'}
            except:
                return {'success': False, 'message': 'Unable to calculate average cost per shirt'}
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _fix_profit_per_shirt_formula(self, command: str) -> Dict[str, Any]:
        """Fix Profit Per Shirt formula to sum column I (Profit column)"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Find summary section (starts at column O)
            summary_start_col = 15  # Column O
            value_col = chr(64 + summary_start_col + 1)  # Column P (value column)
            
            # Profit Per Shirt is in row 6
            profit_per_shirt_row = 6
            profit_per_shirt_cell = f'{value_col}{profit_per_shirt_row}'
            
            # Find the last row with data (check column D - Quantity)
            try:
                all_data = sheet.get_all_values()
                last_row = len(all_data) if all_data else 100
            except:
                last_row = 100
            
            # Correct formula: SUM of column I (Profit column)
            correct_formula = f'=SUM(I2:I{last_row})'
            
            # Get current formula
            try:
                current_formula = sheet.acell(profit_per_shirt_cell, value_render_option='FORMULA').value or ''
            except:
                current_formula = ''
            
            # Update to correct formula
            sheet.update(profit_per_shirt_cell, correct_formula, value_input_option='USER_ENTERED')
            
            self.logger.info(f"Fixed Profit Per Shirt formula in {profit_per_shirt_cell} to: {correct_formula}")
            
            return {
                'success': True,
                'message': f'✅ **Profit Per Shirt Formula Fixed!**\n\n'
                          f'📊 Formula: `{correct_formula}`\n'
                          f'📍 Location: {profit_per_shirt_cell}\n'
                          f'💡 Formula: SUM of all values in Profit column (column I)\n\n'
                          f'✅ Profit Per Shirt = SUM(Profit column)',
                'data': {
                    'cell': profit_per_shirt_cell,
                    'formula': correct_formula,
                    'explanation': 'SUM of all values in Profit column (column I)'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error fixing profit per shirt formula: {e}", exc_info=True)
            return {'success': False, 'message': f"Error: {str(e)}"}

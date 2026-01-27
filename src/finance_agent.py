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
        Update NET PROFIT in METRICS table
        Note: NET PROFIT is now calculated automatically via metrics_calculator
        This method recalculates and updates METRICS
        """
        try:
            from metrics_calculator import calculate_and_update_metrics
            
            # Recalculate all metrics
            metrics = calculate_and_update_metrics(self.sheets_manager)
            
            net_profit = metrics.get("net_profit_after_setup", 0.0)
            setup_costs = metrics.get("setup_costs", 809.32)
            
            return {
                'success': True,
                'message': f'✅ **NET PROFIT Updated in METRICS!**\n\n'
                          f'📊 Net Profit After Setup: ${net_profit:,.2f}\n'
                          f'💵 Setup Costs: ${setup_costs:,.2f}\n'
                          f'💡 Formula: Contribution Profit - Setup Costs\n\n'
                          f'✅ All metrics recalculated and updated',
                'data': {
                    'net_profit_after_setup': net_profit,
                    'setup_costs': setup_costs,
                    'all_metrics': metrics
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error updating net profit: {e}", exc_info=True)
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _get_revenue(self, command: str) -> Dict[str, Any]:
        """Get total revenue from METRICS table"""
        try:
            revenue = self.sheets_manager.get_metric("total_revenue")
            if revenue is None:
                revenue = 0.0
            
            return {
                'success': True,
                'message': f'💰 **Total Revenue:** ${revenue:,.2f}',
                'data': {'revenue': revenue}
            }
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _get_costs(self, command: str) -> Dict[str, Any]:
        """Get total costs from METRICS table"""
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
    
    def _get_profit_margin(self, command: str) -> Dict[str, Any]:
        """Calculate and return profit margin from METRICS"""
        try:
            revenue = self.sheets_manager.get_metric("total_revenue")
            net_profit = self.sheets_manager.get_metric("net_profit_after_setup")
            
            if revenue is None:
                revenue = 0.0
            if net_profit is None:
                net_profit = 0.0
            
            if revenue > 0:
                margin = (net_profit / revenue) * 100
                return {
                    'success': True,
                    'message': f'📊 **Profit Margin:** {margin:.2f}%',
                    'data': {'profit_margin': margin, 'revenue': revenue, 'net_profit': net_profit}
                }
            else:
                return {'success': False, 'message': 'Cannot calculate: Revenue is 0'}
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}"}

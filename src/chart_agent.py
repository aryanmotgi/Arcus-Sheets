"""
Chart Agent - Creates and manages charts in Google Sheets
"""
import logging
from typing import Dict, List, Optional, Any
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class ChartAgent:
    """Agent specialized in creating and managing charts"""
    
    def __init__(self, sheets_manager):
        """Initialize with SheetsManager instance"""
        self.sheets_manager = sheets_manager
        self.logger = logging.getLogger(__name__)
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process chart-related commands
        
        Examples:
            - "create revenue chart"
            - "make a profit chart"
            - "show sales over time"
            - "chart top products"
        """
        command_lower = command.lower()
        
        # Chart creation
        if any(word in command_lower for word in ['chart', 'graph', 'create chart', 'make chart']):
            return self._create_chart(command)
        
        # Revenue charts
        if any(word in command_lower for word in ['revenue chart', 'sales chart']):
            return self._create_revenue_chart(command)
        
        # Profit charts
        if any(word in command_lower for word in ['profit chart', 'profit graph']):
            return self._create_profit_chart(command)
        
        # Product charts
        if any(word in command_lower for word in ['product chart', 'top products chart']):
            return self._create_product_chart(command)
        
        return {
            'success': False,
            'message': 'Chart Agent: I can help with:\n'
                      '• "create revenue chart" - Chart revenue over time\n'
                      '• "make a profit chart" - Profit visualization\n'
                      '• "show sales over time" - Sales trend chart\n'
                      '• "chart top products" - Product sales chart'
        }
    
    def _create_chart(self, command: str) -> Dict[str, Any]:
        """Create a chart based on command"""
        # Chart creation using Google Sheets API
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            spreadsheet = self.sheets_manager.spreadsheet
            
            # For now, return instructions
            # Full chart creation requires more complex Google Sheets API calls
            return {
                'success': True,
                'message': '📊 **Chart Creation**\n\n'
                          'I can help you create charts!\n\n'
                          'Available chart types:\n'
                          '• Revenue chart - "create revenue chart"\n'
                          '• Profit chart - "make a profit chart"\n'
                          '• Product chart - "chart top products"\n\n'
                          '💡 Tip: Charts are best created manually in Google Sheets.\n'
                          'Use Insert → Chart in Google Sheets.',
                'data': {'chart_type': 'general'}
            }
        except Exception as e:
            return {'success': False, 'message': f"Error: {str(e)}"}
    
    def _create_revenue_chart(self, command: str) -> Dict[str, Any]:
        """Create revenue chart"""
        return {
            'success': True,
            'message': '📊 **Revenue Chart**\n\n'
                      'To create a revenue chart:\n'
                      '1. Select the date and revenue columns\n'
                      '2. Go to Insert → Chart\n'
                      '3. Choose Line or Column chart\n'
                      '4. Chart will show revenue over time',
            'data': {'chart_type': 'revenue'}
        }
    
    def _create_profit_chart(self, command: str) -> Dict[str, Any]:
        """Create profit chart"""
        return {
            'success': True,
            'message': '📊 **Profit Chart**\n\n'
                      'To create a profit chart:\n'
                      '1. Select profit column\n'
                      '2. Go to Insert → Chart\n'
                      '3. Choose Column or Pie chart\n'
                      '4. Chart will visualize profits',
            'data': {'chart_type': 'profit'}
        }
    
    def _create_product_chart(self, command: str) -> Dict[str, Any]:
        """Create product sales chart"""
        return {
            'success': True,
            'message': '📊 **Product Chart**\n\n'
                      'To create a product sales chart:\n'
                      '1. Select product name and quantity columns\n'
                      '2. Go to Insert → Chart\n'
                      '3. Choose Bar or Pie chart\n'
                      '4. Chart will show top products',
            'data': {'chart_type': 'product'}
        }

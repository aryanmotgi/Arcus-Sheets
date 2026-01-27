"""
Chart Agent - Creates and manages charts in Google Sheets
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ChartAgent:
    """Agent specialized in chart creation and visualization"""
    
    def __init__(self, sheets_manager):
        """Initialize with SheetsManager instance"""
        self.sheets_manager = sheets_manager
        self.logger = logging.getLogger(__name__)
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process chart-related commands
        
        Examples:
            - "generate charts"
            - "refresh charts"
            - "show revenue chart"
            - "create profit chart"
        """
        command_lower = command.lower().strip()
        
        # Generate/create charts
        if any(phrase in command_lower for phrase in ['generate chart', 'create chart', 'make chart', 'build chart']):
            return self._generate_all_charts()
        
        # Refresh charts
        if 'refresh chart' in command_lower:
            return self._refresh_charts()
        
        # Specific chart requests
        if 'revenue chart' in command_lower or 'revenue over time' in command_lower:
            return self._create_revenue_chart()
        
        if 'profit chart' in command_lower or 'profit over time' in command_lower:
            return self._create_profit_chart()
        
        if 'product chart' in command_lower or 'products chart' in command_lower:
            return self._create_products_chart()
        
        # General chart help
        return {
            'success': False,
            'message': 'Chart Agent: I can help with:\n'
                      '• "generate charts" - Create all charts\n'
                      '• "refresh charts" - Update existing charts\n'
                      '• "show revenue chart" - Create revenue over time chart\n'
                      '• "show profit chart" - Create profit chart'
        }
    
    def _generate_all_charts(self) -> Dict[str, Any]:
        """Generate all charts on CHARTS sheet"""
        try:
            # Create CHARTS sheet
            charts_sheet = self.sheets_manager.create_sheet_if_not_exists("CHARTS")
            
            # Clear existing charts (we'll recreate them)
            charts_sheet.clear()
            
            # Add header
            charts_sheet.update('A1', [["ARCUS ANALYTICS - CHARTS"]])
            
            # Create charts
            charts_created = []
            
            try:
                self._create_revenue_chart()
                charts_created.append("Revenue Over Time")
            except Exception as e:
                self.logger.error(f"Error creating revenue chart: {e}")
            
            try:
                self._create_profit_chart()
                charts_created.append("Profit Over Time")
            except Exception as e:
                self.logger.error(f"Error creating profit chart: {e}")
            
            try:
                self._create_products_chart()
                charts_created.append("Products by Units")
            except Exception as e:
                self.logger.error(f"Error creating products chart: {e}")
            
            return {
                'success': True,
                'message': f'✅ **Charts Generated!**\n\n'
                          f'📊 Created {len(charts_created)} charts:\n'
                          f'{chr(10).join(f"  • {c}" for c in charts_created)}\n\n'
                          f'📍 View them in the CHARTS sheet',
                'data': {'charts_created': charts_created}
            }
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}", exc_info=True)
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _create_revenue_chart(self) -> Dict[str, Any]:
        """Create revenue over time line chart"""
        try:
            charts_sheet = self.sheets_manager.create_sheet_if_not_exists("CHARTS")
            orders_sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            
            # Get sheet IDs
            charts_sheet_id = charts_sheet.id
            orders_sheet_id = orders_sheet.id
            
            # Find Date and Total Revenue columns in ORDERS
            orders_data = orders_sheet.get_all_values()
            if not orders_data or len(orders_data) < 2:
                return {'success': False, 'message': 'No order data available for chart'}
            
            headers = orders_data[0]
            try:
                date_col_idx = headers.index("Date")
                revenue_col_idx = headers.index("Total Revenue") if "Total Revenue" in headers else headers.index("Sold Price")
            except ValueError:
                return {'success': False, 'message': 'Required columns not found in ORDERS sheet'}
            
            # Create chart request
            chart_request = {
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": "Revenue Over Time",
                            "basicChart": {
                                "chartType": "LINE",
                                "legendPosition": "BOTTOM_LEGEND",
                                "axis": [
                                    {
                                        "position": "BOTTOM_AXIS",
                                        "title": "Date"
                                    },
                                    {
                                        "position": "LEFT_AXIS",
                                        "title": "Revenue ($)"
                                    }
                                ],
                                "domains": [
                                    {
                                        "domain": {
                                            "sourceRange": {
                                                "sources": [{
                                                    "sheetId": orders_sheet_id,
                                                    "startRowIndex": 0,
                                                    "endRowIndex": len(orders_data),
                                                    "startColumnIndex": date_col_idx,
                                                    "endColumnIndex": date_col_idx + 1
                                                }]
                                            }
                                        }
                                    }
                                ],
                                "series": [
                                    {
                                        "series": {
                                            "sourceRange": {
                                                "sources": [{
                                                    "sheetId": orders_sheet_id,
                                                    "startRowIndex": 0,
                                                    "endRowIndex": len(orders_data),
                                                    "startColumnIndex": revenue_col_idx,
                                                    "endColumnIndex": revenue_col_idx + 1
                                                }]
                                            }
                                        },
                                        "targetAxis": "LEFT_AXIS"
                                    }
                                ],
                                "headerCount": 1
                            }
                        },
                        "position": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "sheetId": charts_sheet_id,
                                    "rowIndex": 2,
                                    "columnIndex": 0
                                },
                                "offsetXPixels": 0,
                                "offsetYPixels": 0,
                                "widthPixels": 600,
                                "heightPixels": 400
                            }
                        }
                    }
                }
            }
            
            charts_sheet.spreadsheet.batch_update({"requests": [chart_request]})
            
            return {'success': True, 'message': '✅ Revenue chart created!'}
        except Exception as e:
            self.logger.error(f"Error creating revenue chart: {e}", exc_info=True)
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _create_profit_chart(self) -> Dict[str, Any]:
        """Create profit over time line chart"""
        try:
            charts_sheet = self.sheets_manager.create_sheet_if_not_exists("CHARTS")
            orders_sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            
            charts_sheet_id = charts_sheet.id
            orders_sheet_id = orders_sheet.id
            
            orders_data = orders_sheet.get_all_values()
            if not orders_data or len(orders_data) < 2:
                return {'success': False, 'message': 'No order data available'}
            
            headers = orders_data[0]
            try:
                date_col_idx = headers.index("Date")
                profit_col_idx = headers.index("Profit")
            except ValueError:
                return {'success': False, 'message': 'Required columns not found'}
            
            chart_request = {
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": "Profit Over Time",
                            "basicChart": {
                                "chartType": "LINE",
                                "legendPosition": "BOTTOM_LEGEND",
                                "axis": [
                                    {"position": "BOTTOM_AXIS", "title": "Date"},
                                    {"position": "LEFT_AXIS", "title": "Profit ($)"}
                                ],
                                "domains": [{
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": orders_sheet_id,
                                                "startRowIndex": 0,
                                                "endRowIndex": len(orders_data),
                                                "startColumnIndex": date_col_idx,
                                                "endColumnIndex": date_col_idx + 1
                                            }]
                                        }
                                    }
                                }],
                                "series": [{
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": orders_sheet_id,
                                                "startRowIndex": 0,
                                                "endRowIndex": len(orders_data),
                                                "startColumnIndex": profit_col_idx,
                                                "endColumnIndex": profit_col_idx + 1
                                            }]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS"
                                }],
                                "headerCount": 1
                            }
                        },
                        "position": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "sheetId": charts_sheet_id,
                                    "rowIndex": 2,
                                    "columnIndex": 7  # Place to the right of revenue chart
                                },
                                "offsetXPixels": 0,
                                "offsetYPixels": 0,
                                "widthPixels": 600,
                                "heightPixels": 400
                            }
                        }
                    }
                }
            }
            
            charts_sheet.spreadsheet.batch_update({"requests": [chart_request]})
            
            return {'success': True, 'message': '✅ Profit chart created!'}
        except Exception as e:
            self.logger.error(f"Error creating profit chart: {e}", exc_info=True)
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _create_products_chart(self) -> Dict[str, Any]:
        """Create products by units sold bar chart"""
        try:
            charts_sheet = self.sheets_manager.create_sheet_if_not_exists("CHARTS")
            orders_sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            
            charts_sheet_id = charts_sheet.id
            orders_sheet_id = orders_sheet.id
            
            orders_data = orders_sheet.get_all_values()
            if not orders_data or len(orders_data) < 2:
                return {'success': False, 'message': 'No order data available'}
            
            headers = orders_data[0]
            try:
                product_col_idx = headers.index("Product Name")
                quantity_col_idx = headers.index("Quantity")
            except ValueError:
                return {'success': False, 'message': 'Required columns not found'}
            
            chart_request = {
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": "Units Sold by Product",
                            "basicChart": {
                                "chartType": "COLUMN",
                                "legendPosition": "BOTTOM_LEGEND",
                                "axis": [
                                    {"position": "BOTTOM_AXIS", "title": "Product"},
                                    {"position": "LEFT_AXIS", "title": "Units Sold"}
                                ],
                                "domains": [{
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": orders_sheet_id,
                                                "startRowIndex": 0,
                                                "endRowIndex": len(orders_data),
                                                "startColumnIndex": product_col_idx,
                                                "endColumnIndex": product_col_idx + 1
                                            }]
                                        }
                                    }
                                }],
                                "series": [{
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": orders_sheet_id,
                                                "startRowIndex": 0,
                                                "endRowIndex": len(orders_data),
                                                "startColumnIndex": quantity_col_idx,
                                                "endColumnIndex": quantity_col_idx + 1
                                            }]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS"
                                }],
                                "headerCount": 1
                            }
                        },
                        "position": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "sheetId": charts_sheet_id,
                                    "rowIndex": 15,  # Place below other charts
                                    "columnIndex": 0
                                },
                                "offsetXPixels": 0,
                                "offsetYPixels": 0,
                                "widthPixels": 600,
                                "heightPixels": 400
                            }
                        }
                    }
                }
            }
            
            charts_sheet.spreadsheet.batch_update({"requests": [chart_request]})
            
            return {'success': True, 'message': '✅ Products chart created!'}
        except Exception as e:
            self.logger.error(f"Error creating products chart: {e}", exc_info=True)
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _refresh_charts(self) -> Dict[str, Any]:
        """Refresh all charts (recreate them)"""
        return self._generate_all_charts()

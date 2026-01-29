"""
Simple Orders Sync - ORDERS tab only implementation

Two commands:
1. init_orders_apply() - Creates/clears ORDERS tab with headers, formulas, formatting
2. sync_orders() - Fetches Shopify orders and writes to ORDERS tab
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

# Headers for ORDERS tab (A:P)
ORDERS_HEADERS = [
    'Order #',           # A
    'Date',              # B
    'Customer',          # C
    'Email',             # D
    'Product',           # E
    'Variant/Size',      # F
    'Qty',               # G
    'Unit Price',        # H
    'Revenue',           # I (formula)
    'Unit Cost',         # J
    'Shipping Label Cost', # K (user input)
    'Profit',            # L (formula)
    'PSL',               # M (user input)
    'Notes',             # N (user input)
    'Shopify Payout',    # O
    'Fulfillment Status' # P
]

# Default unit cost (can be overridden by config)
DEFAULT_UNIT_COST = 12.26

# Number of rows to fill formulas
FORMULA_ROWS = 2000


class SimpleOrdersSync:
    """Simple sync agent that only works with ORDERS tab"""
    
    def __init__(self, sheets_manager, shopify_client, config=None):
        """Initialize with SheetsManager and ShopifyClient"""
        self.sheets_manager = sheets_manager
        self.shopify_client = shopify_client
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def init_orders_apply(self) -> Dict[str, Any]:
        """
        Create/clear ORDERS tab with headers, formulas, and formatting
        """
        self.logger.info("=== INIT ORDERS APPLY ===")
        
        try:
            # Get or create ORDERS sheet
            sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            
            # Clear all content
            sheet.clear()
            self.logger.info("Cleared ORDERS sheet")
            
            # Write headers
            sheet.update('A1', [ORDERS_HEADERS], value_input_option='USER_ENTERED')
            self.logger.info(f"Wrote {len(ORDERS_HEADERS)} headers")
            
            # Apply formatting
            self._apply_header_formatting(sheet)
            self._apply_column_formatting(sheet)
            self._apply_conditional_formatting(sheet)
            self._fill_formulas(sheet)
            self._freeze_and_filter(sheet)
            self._set_column_widths(sheet)
            self._hide_gridlines(sheet)
            
            self.logger.info("=== INIT ORDERS APPLY COMPLETE ===")
            
            return {
                'success': True,
                'message': '✅ **ORDERS tab initialized!**\n\n'
                          f'📊 Headers: {len(ORDERS_HEADERS)} columns (A:P)\n'
                          '📐 Formulas: Revenue (I) and Profit (L) filled to row 2000\n'
                          '🎨 Formatting: Applied (freeze, filter, colors, borders)\n\n'
                          '👉 Now run `sync orders` to populate with Shopify data.'
            }
            
        except Exception as e:
            self.logger.error(f"Error in init_orders_apply: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'❌ Failed to initialize ORDERS: {str(e)}'
            }
    
    def sync_orders(self) -> Dict[str, Any]:
        """
        Fetch Shopify orders and write to ORDERS tab
        """
        self.logger.info("=== SYNC ORDERS ===")
        
        try:
            # Get ORDERS sheet (create if not exists)
            sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            
            # Check if headers exist, if not run init first
            existing_data = sheet.get_all_values()
            if not existing_data or existing_data[0] != ORDERS_HEADERS:
                self.logger.info("Headers missing, running init first...")
                self.init_orders_apply()
                sheet = self.sheets_manager.spreadsheet.worksheet("ORDERS")
            
            # Fetch orders from Shopify
            self.logger.info("Fetching orders from Shopify...")
            orders = self.shopify_client.get_orders(limit=250, status='any')
            self.logger.info(f"Fetched {len(orders)} orders from Shopify")
            
            if not orders:
                return {
                    'success': True,
                    'message': '⚠️ No orders found in Shopify.\n\nMake sure your Shopify store has orders.'
                }
            
            # Get unit cost from config
            unit_cost = self.config.get('profit', {}).get('cost_per_shirt', DEFAULT_UNIT_COST)
            
            # Process orders into rows (one row per line item)
            rows = []
            order_numbers = set()
            skipped_orders = 0
            oldest_date = None
            newest_date = None
            
            for order in orders:
                try:
                    order_number = order.get('order_number', order.get('name', ''))
                    order_numbers.add(order_number)
                    
                    # Parse date
                    created_at = order.get('created_at', '')
                    if created_at:
                        try:
                            order_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            date_str = order_date.strftime('%Y-%m-%d')
                            if oldest_date is None or order_date < oldest_date:
                                oldest_date = order_date
                            if newest_date is None or order_date > newest_date:
                                newest_date = order_date
                        except:
                            date_str = created_at[:10] if len(created_at) >= 10 else created_at
                    else:
                        date_str = ''
                    
                    # Customer info
                    customer = order.get('customer', {}) or {}
                    first_name = customer.get('first_name', '')
                    last_name = customer.get('last_name', '')
                    customer_name = f"{first_name} {last_name}".strip() or 'Guest'
                    customer_email = customer.get('email', '')
                    
                    # Fulfillment status
                    fulfillment_status = order.get('fulfillment_status') or 'unfulfilled'
                    
                    # Total price (Shopify payout)
                    total_price = order.get('total_price', '')
                    
                    # Process line items
                    line_items = order.get('line_items', [])
                    if not line_items:
                        skipped_orders += 1
                        continue
                    
                    for item in line_items:
                        product_title = item.get('title', '')
                        variant_title = item.get('variant_title', '') or ''
                        quantity = item.get('quantity', 1)
                        unit_price = item.get('price', 0)
                        
                        try:
                            unit_price = float(unit_price)
                        except:
                            unit_price = 0
                        
                        # Build row
                        row = [
                            order_number,           # A: Order #
                            date_str,               # B: Date
                            customer_name,          # C: Customer
                            customer_email,         # D: Email
                            product_title,          # E: Product
                            variant_title,          # F: Variant/Size
                            quantity,               # G: Qty
                            unit_price,             # H: Unit Price
                            '',                     # I: Revenue (formula)
                            unit_cost,              # J: Unit Cost
                            '',                     # K: Shipping Label Cost (user input)
                            '',                     # L: Profit (formula)
                            '',                     # M: PSL (user input)
                            '',                     # N: Notes (user input)
                            total_price if len(rows) == 0 or rows[-1][0] != order_number else '',  # O: Shopify Payout (only first line item)
                            fulfillment_status      # P: Fulfillment Status
                        ]
                        rows.append(row)
                        
                except Exception as e:
                    self.logger.warning(f"Error processing order: {e}")
                    skipped_orders += 1
            
            if not rows:
                return {
                    'success': True,
                    'message': '⚠️ No order line items to sync.\n\nAll orders may have been skipped.'
                }
            
            self.logger.info(f"Processed {len(rows)} rows from {len(order_numbers)} orders")
            
            # Clear existing data (rows 2+)
            try:
                num_existing_rows = len(sheet.get_all_values())
                if num_existing_rows > 1:
                    sheet.batch_clear([f'A2:P{num_existing_rows}'])
                    self.logger.info(f"Cleared rows 2-{num_existing_rows}")
            except Exception as e:
                self.logger.warning(f"Could not clear existing data: {e}")
            
            # Write all rows in one batch
            if rows:
                data_range = f'A2:P{len(rows) + 1}'
                sheet.update(data_range, rows, value_input_option='USER_ENTERED')
                self.logger.info(f"Wrote {len(rows)} rows")
            
            # Re-apply formulas for the rows we just wrote
            self._fill_formulas_for_rows(sheet, len(rows))
            
            # Build date range string
            date_range_str = ''
            if oldest_date and newest_date:
                date_range_str = f"{oldest_date.strftime('%Y-%m-%d')} to {newest_date.strftime('%Y-%m-%d')}"
            
            self.logger.info("=== SYNC ORDERS COMPLETE ===")
            
            return {
                'success': True,
                'message': f'✅ **Sync Complete!**\n\n'
                          f'📊 **Summary:**\n'
                          f'  • Orders: {len(order_numbers)}\n'
                          f'  • Rows: {len(rows)} (line items)\n'
                          f'  • Date range: {date_range_str}\n'
                          f'  • Skipped: {skipped_orders}\n\n'
                          f'💡 Fill in columns K (Shipping Label Cost), M (PSL), N (Notes) as needed.',
                'data': {
                    'orders': len(order_numbers),
                    'rows': len(rows),
                    'skipped': skipped_orders,
                    'date_range': date_range_str
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in sync_orders: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'❌ Failed to sync orders: {str(e)}'
            }
    
    # ============================================
    # FORMATTING HELPERS
    # ============================================
    
    def _apply_header_formatting(self, sheet):
        """Apply header row formatting: bold, centered, gray background, thick bottom border"""
        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": len(ORDERS_HEADERS)
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.88, "green": 0.88, "blue": 0.88},  # Light gray #E0E0E0
                            "textFormat": {
                                "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0},
                                "fontSize": 11,
                                "bold": True
                            },
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE",
                            "borders": {
                                "bottom": {"style": "SOLID_MEDIUM", "width": 2, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}}
                            }
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)"
                }
            }
        ]
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
        self.logger.info("Applied header formatting")
    
    def _apply_column_formatting(self, sheet):
        """Apply number formatting: currency for H, I, J, K, L, O; date for B"""
        requests = []
        
        # Currency columns: H, I, J, K, L, O (indices 7, 8, 9, 10, 11, 14)
        currency_cols = [7, 8, 9, 10, 11, 14]
        for col_idx in currency_cols:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": FORMULA_ROWS + 1,
                        "startColumnIndex": col_idx,
                        "endColumnIndex": col_idx + 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat"
                }
            })
        
        # Date column: B (index 1)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 1,
                    "endRowIndex": FORMULA_ROWS + 1,
                    "startColumnIndex": 1,
                    "endColumnIndex": 2
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {"type": "DATE", "pattern": "yyyy-mm-dd"}
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })
        
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
        self.logger.info("Applied column formatting")
    
    def _apply_conditional_formatting(self, sheet):
        """Apply conditional formatting: L<0 red, K blank yellow, P=unfulfilled orange"""
        requests = []
        
        # L (Profit) < 0 => Red background
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": FORMULA_ROWS + 1,
                        "startColumnIndex": 11,  # Column L
                        "endColumnIndex": 12
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "NUMBER_LESS",
                            "values": [{"userEnteredValue": "0"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 0.96, "green": 0.80, "blue": 0.80}  # Light red
                        }
                    }
                },
                "index": 0
            }
        })
        
        # K (Shipping Label Cost) blank => Yellow background
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": FORMULA_ROWS + 1,
                        "startColumnIndex": 10,  # Column K
                        "endColumnIndex": 11
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "BLANK"
                        },
                        "format": {
                            "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.80}  # Light yellow
                        }
                    }
                },
                "index": 1
            }
        })
        
        # P = "unfulfilled" => Orange background
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": FORMULA_ROWS + 1,
                        "startColumnIndex": 15,  # Column P
                        "endColumnIndex": 16
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "unfulfilled"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 1.0, "green": 0.85, "blue": 0.70}  # Light orange
                        }
                    }
                },
                "index": 2
            }
        })
        
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
        self.logger.info("Applied conditional formatting")
    
    def _fill_formulas(self, sheet):
        """Fill formulas for Revenue (I) and Profit (L) down to row 2000"""
        # Build formula arrays
        revenue_formulas = []
        profit_formulas = []
        
        for row in range(2, FORMULA_ROWS + 2):
            revenue_formulas.append([f'=IFERROR(G{row}*H{row},"")'])
            profit_formulas.append([f'=IFERROR(I{row}-(J{row}*G{row})-K{row},"")'])
        
        # Write formulas in batch
        sheet.update(f'I2:I{FORMULA_ROWS + 1}', revenue_formulas, value_input_option='USER_ENTERED')
        sheet.update(f'L2:L{FORMULA_ROWS + 1}', profit_formulas, value_input_option='USER_ENTERED')
        
        self.logger.info(f"Filled formulas for rows 2-{FORMULA_ROWS + 1}")
    
    def _fill_formulas_for_rows(self, sheet, num_rows):
        """Fill formulas only for the rows that have data"""
        if num_rows == 0:
            return
        
        end_row = num_rows + 1
        
        # Build formula arrays
        revenue_formulas = []
        profit_formulas = []
        
        for row in range(2, end_row + 1):
            revenue_formulas.append([f'=IFERROR(G{row}*H{row},"")'])
            profit_formulas.append([f'=IFERROR(I{row}-(J{row}*G{row})-K{row},"")'])
        
        # Write formulas in batch
        sheet.update(f'I2:I{end_row}', revenue_formulas, value_input_option='USER_ENTERED')
        sheet.update(f'L2:L{end_row}', profit_formulas, value_input_option='USER_ENTERED')
        
        self.logger.info(f"Filled formulas for rows 2-{end_row}")
    
    def _freeze_and_filter(self, sheet):
        """Freeze row 1 and add filter"""
        requests = [
            # Freeze row 1
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet.id,
                        "gridProperties": {"frozenRowCount": 1}
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            },
            # Add filter
            {
                "setBasicFilter": {
                    "filter": {
                        "range": {
                            "sheetId": sheet.id,
                            "startRowIndex": 0,
                            "endRowIndex": FORMULA_ROWS + 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": len(ORDERS_HEADERS)
                        }
                    }
                }
            }
        ]
        
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
        self.logger.info("Applied freeze and filter")
    
    def _set_column_widths(self, sheet):
        """Set reasonable column widths"""
        # Column widths: A=80, B=100, C=120, D=180, E=200, F=100, G=50, H=80, I=80, J=80, K=120, L=80, M=80, N=150, O=100, P=100
        widths = [80, 100, 120, 180, 200, 100, 50, 80, 80, 80, 120, 80, 80, 150, 100, 100]
        
        requests = []
        for col_idx, width in enumerate(widths):
            requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": col_idx,
                        "endIndex": col_idx + 1
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize"
                }
            })
        
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
        self.logger.info("Set column widths")
    
    def _hide_gridlines(self, sheet):
        """Hide gridlines on the sheet"""
        requests = [
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet.id,
                        "gridProperties": {"hideGridlines": True}
                    },
                    "fields": "gridProperties.hideGridlines"
                }
            }
        ]
        
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
        self.logger.info("Hidden gridlines")


# ============================================
# STANDALONE FUNCTIONS (for direct import)
# ============================================

def init_orders_apply(sheets_manager, shopify_client=None, config=None) -> Dict[str, Any]:
    """Standalone function to initialize ORDERS tab"""
    agent = SimpleOrdersSync(sheets_manager, shopify_client, config)
    return agent.init_orders_apply()


def sync_orders(sheets_manager, shopify_client, config=None) -> Dict[str, Any]:
    """Standalone function to sync orders"""
    agent = SimpleOrdersSync(sheets_manager, shopify_client, config)
    return agent.sync_orders()

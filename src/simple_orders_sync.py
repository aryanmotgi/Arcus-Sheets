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

# New Headers (A:L)
ORDERS_HEADERS = [
    'Customer Name',      # A
    'Product',            # B
    'Size',               # C
    'Qty',                # D
    'Price',              # E
    'Revenue',            # F (formula)
    'Unit Cost',          # G
    'Shipping Label Cost',# H (user input)
    'Profit',             # I (formula)
    'Profit Margin %',    # J (formula)
    'Shopify Payout',     # K
    'Fulfillment Status'  # L
]

# Default unit cost
DEFAULT_UNIT_COST = 12.26

# Number of rows to fill formulas
FORMULA_ROWS = 2000


class SimpleOrdersSync:
    """Simple sync agent that only works with ORDERS tab"""
    
    def __init__(self, sheets_manager, shopify_client, config=None):
        self.sheets_manager = sheets_manager
        self.shopify_client = shopify_client
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def init_orders_apply(self) -> Dict[str, Any]:
        """Create/clear ORDERS tab with headers, formulas, and formatting"""
        self.logger.info("=== INIT ORDERS APPLY ===")
        
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            sheet.clear()
            self.logger.info("Cleared ORDERS sheet")
            
            # Write headers
            sheet.update('A1', [ORDERS_HEADERS], value_input_option='USER_ENTERED')
            
            # Apply all formatting
            self._apply_header_formatting(sheet)
            self._apply_column_formatting(sheet)
            self._apply_conditional_formatting(sheet)
            self._fill_formulas(sheet)
            self._freeze_and_filter(sheet)
            self._set_column_widths(sheet)
            self._hide_gridlines(sheet)
            
            return {
                'success': True,
                'message': '✅ **ORDERS tab initialized!**\n\n'
                          f'📊 Headers: {len(ORDERS_HEADERS)} columns (A:L)\n'
                          '📐 Formulas: Revenue, Profit, Margin filled\n'
                          '🎨 Formatting: New Arcus theme applied'
            }
            
        except Exception as e:
            self.logger.error(f"Error in init_orders_apply: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed to initialize ORDERS: {str(e)}'}
    
    def sync_orders(self) -> Dict[str, Any]:
        """Fetch Shopify orders and write to ORDERS tab"""
        self.logger.info("=== SYNC ORDERS ===")
        
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            
            # Check headers
            existing_data = sheet.get_all_values()
            if not existing_data or existing_data[0] != ORDERS_HEADERS:
                self.logger.info("Headers mismatch, running init first...")
                self.init_orders_apply()
                sheet = self.sheets_manager.spreadsheet.worksheet("ORDERS")
            
            # Fetch orders
            orders = self.shopify_client.get_orders(limit=250, status='any')
            if not orders:
                return {'success': True, 'message': '⚠️ No orders found in Shopify.'}
            
            unit_cost = self.config.get('profit', {}).get('cost_per_shirt', DEFAULT_UNIT_COST)
            
            rows = []
            orders_count = 0
            skipped_orders = 0
            
            for order in orders:
                try:
                    orders_count += 1
                    order_number = order.get('order_number', '')  # Used for tracking but not written
                    
                    # Customer
                    customer = order.get('customer', {}) or {}
                    customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or 'Guest'
                    
                    # Totals & Status
                    fulfillment_status = (order.get('fulfillment_status') or 'unfulfilled').capitalize()
                    total_price = order.get('total_price', '')
                    
                    line_items = order.get('line_items', [])
                    if not line_items:
                        skipped_orders += 1
                        continue
                    
                    # One row per line item
                    for i, item in enumerate(line_items):
                        product_title = item.get('title', '')
                        variant_title = item.get('variant_title', '') or ''
                        quantity = int(item.get('quantity', 1))
                        price = float(item.get('price', 0))
                        
                        # Only show total payout on the first line item of the order
                        payout_display = total_price if i == 0 else ''
                        
                        row = [
                            customer_name,      # A: Customer Name
                            product_title,      # B: Product
                            variant_title,      # C: Size
                            quantity,           # D: Qty
                            price,              # E: Price
                            '',                 # F: Revenue (formula)
                            unit_cost,          # G: Unit Cost
                            '',                 # H: Shipping Label Cost (user)
                            '',                 # I: Profit (formula)
                            '',                 # J: Margin (formula)
                            payout_display,     # K: Shopify Payout
                            fulfillment_status  # L: Fulfillment Status
                        ]
                        rows.append(row)
                        
                except Exception as e:
                    self.logger.warning(f"Error processing order: {e}")
                    skipped_orders += 1
            
            if not rows:
                return {'success': True, 'message': '⚠️ No line items processed.'}
            
            # Clear existing data (rows 2+)
            try:
                num_existing_rows = len(sheet.get_all_values())
                if num_existing_rows > 1:
                    sheet.batch_clear([f'A2:L{num_existing_rows}'])
            except:
                pass
            
            # Write new data
            sheet.update(f'A2:L{len(rows) + 1}', rows, value_input_option='USER_ENTERED')
            
            # Re-apply formulas
            self._fill_formulas_for_rows(sheet, len(rows))
            
            return {
                'success': True,
                'message': f'✅ **Sync Complete!**\n\n'
                          f'📦 Orders Processed: {orders_count}\n'
                          f'📝 Rows Written: {len(rows)}\n'
                          f'⚡ formatting applied automatically.',
                'data': {'orders': orders_count, 'rows': len(rows)}
            }
            
        except Exception as e:
            self.logger.error(f"Error in sync_orders: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed to sync: {str(e)}'}

    # ============================================
    # FORMATTING HELPERS
    # ============================================
    
    def _apply_header_formatting(self, sheet):
        """Bold, centered, gray bg, borders"""
        requests = [{
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 0, "endRowIndex": 1,
                    "startColumnIndex": 0, "endColumnIndex": len(ORDERS_HEADERS)
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.88, "green": 0.88, "blue": 0.88},
                        "textFormat": {"bold": True, "fontSize": 11},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "borders": {
                            "top": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                            "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                            "left": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                            "right": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}}
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)"
            }
        }]
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
    
    def _apply_column_formatting(self, sheet):
        """Currency, Dates, Borders"""
        requests = []
        
        # Apply borders to ALL data cells
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 1, "endRowIndex": FORMULA_ROWS + 1,
                    "startColumnIndex": 0, "endColumnIndex": len(ORDERS_HEADERS)
                },
                "cell": {
                    "userEnteredFormat": {
                        "borders": {
                            "top": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
                            "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
                            "left": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
                            "right": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(borders,horizontalAlignment)"
            }
        })
        
        # Currency columns: Price(E), Revenue(F), Cost(G), Ship(H), Profit(I), Payout(K)
        # 0-based: 4, 5, 6, 7, 8, 10
        for col in [4, 5, 6, 7, 8, 10]:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 1, "endRowIndex": FORMULA_ROWS + 1,
                        "startColumnIndex": col, "endColumnIndex": col + 1
                    },
                    "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}},
                    "fields": "userEnteredFormat.numberFormat"
                }
            })
            
        # Percentage: J (9)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 1, "endRowIndex": FORMULA_ROWS + 1,
                    "startColumnIndex": 9, "endColumnIndex": 10
                },
                "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}},
                "fields": "userEnteredFormat.numberFormat"
            }
        })
        
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
    
    def _apply_conditional_formatting(self, sheet):
        requests = []
        
        # 1. Product = "Arcus Tee" -> Light Gray
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 0, "endColumnIndex": 12}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "Arcus Tee"}]},
                        "format": {"backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95}}
                    }
                }, "index": 0
            }
        })
        
        # 2. Product = "All Paths Tee" -> Light Purple
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 0, "endColumnIndex": 12}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "All Paths Tee"}]},
                        "format": {"backgroundColor": {"red": 0.95, "green": 0.9, "blue": 1.0}} # Light purple
                    }
                }, "index": 1
            }
        })
        
        # 3. Profit > 0 -> Green (Col I, index 8)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 8, "endColumnIndex": 9}],
                    "booleanRule": {
                        "condition": {"type": "NUMBER_GREATER", "values": [{"userEnteredValue": "0"}]},
                        "format": {
                            "backgroundColor": {"red": 0.85, "green": 0.95, "blue": 0.85},
                            "textFormat": {"foregroundColor": {"red": 0, "green": 0.4, "blue": 0}}
                        }
                    }
                }, "index": 2
            }
        })
        
        # 4. Profit < 0 -> Red (Col I, index 8)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 8, "endColumnIndex": 9}],
                    "booleanRule": {
                        "condition": {"type": "NUMBER_LESS", "values": [{"userEnteredValue": "0"}]},
                        "format": {
                            "backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.9},
                            "textFormat": {"foregroundColor": {"red": 0.8, "green": 0, "blue": 0}}
                        }
                    }
                }, "index": 3
            }
        })
        
        # 5. Fulfillment = "Fulfilled" -> Green (Col L, index 11)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 11, "endColumnIndex": 12}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Fulfilled"}]},
                        "format": {"backgroundColor": {"red": 0.8, "green": 1.0, "blue": 0.8}}
                    }
                }, "index": 4
            }
        })
        
        # 6. Fulfillment = "Unfulfilled" -> Orange (Col L, index 11)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 11, "endColumnIndex": 12}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Unfulfilled"}]},
                        "format": {"backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.8}}
                    }
                }, "index": 5
            }
        })
        
        # 7. Size column highlight (Col C, index 2) - subtle blue
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 2, "endColumnIndex": 3}],
                    "booleanRule": {
                        "condition": {"type": "NOT_BLANK"},
                        "format": {"textFormat": {"bold": True, "foregroundColor": {"red": 0.2, "green": 0.2, "blue": 0.6}}}
                    }
                }, "index": 6
            }
        })
        
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
    
    def _fill_formulas(self, sheet):
        """Fill formulas for Revenue, Profit, Margin"""
        # Rev = Qty(D)*Price(E) -> F
        # Profit = Rev(F) - (Cost(G)*Qty(D)) - Ship(H) -> I
        # Margin = Profit(I) / Rev(F) -> J
        
        formulas_rev = []
        formulas_prof = []
        formulas_marg = []
        
        for r in range(2, FORMULA_ROWS + 2):
            formulas_rev.append([f'=IFERROR(D{r}*E{r},"")'])
            formulas_prof.append([f'=IFERROR(F{r}-(G{r}*D{r})-H{r},"")'])
            formulas_marg.append([f'=IFERROR(I{r}/F{r},"")'])
        
        sheet.update(f'F2:F{FORMULA_ROWS+1}', formulas_rev, value_input_option='USER_ENTERED')
        sheet.update(f'I2:I{FORMULA_ROWS+1}', formulas_prof, value_input_option='USER_ENTERED')
        sheet.update(f'J2:J{FORMULA_ROWS+1}', formulas_marg, value_input_option='USER_ENTERED')
    
    def _fill_formulas_for_rows(self, sheet, num_rows):
        """Fill formulas for partial rows (optimization)"""
        if num_rows == 0: return
        
        formulas_rev = []
        formulas_prof = []
        formulas_marg = []
        
        for r in range(2, num_rows + 2):
            formulas_rev.append([f'=IFERROR(D{r}*E{r},"")'])
            formulas_prof.append([f'=IFERROR(F{r}-(G{r}*D{r})-H{r},"")'])
            formulas_marg.append([f'=IFERROR(I{r}/F{r},"")'])
            
        sheet.update(f'F2:F{num_rows+1}', formulas_rev, value_input_option='USER_ENTERED')
        sheet.update(f'I2:I{num_rows+1}', formulas_prof, value_input_option='USER_ENTERED')
        sheet.update(f'J2:J{num_rows+1}', formulas_marg, value_input_option='USER_ENTERED')

    def _freeze_and_filter(self, sheet):
        requests = [
            {"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}},
            {"setBasicFilter": {"filter": {"range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 0, "endColumnIndex": len(ORDERS_HEADERS)}}}}
        ]
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
    
    def _set_column_widths(self, sheet):
        # A:Name(150), B:Prod(200), C:Size(80), D:Qty(50), E:Price(80), F:Rev(80), G:Cost(80), H:Ship(100), I:Prof(80), J:Marg(80), K:Pay(100), L:Stat(100)
        widths = [150, 200, 80, 50, 80, 80, 80, 100, 80, 80, 100, 100]
        requests = []
        for i, w in enumerate(widths):
            requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1}, "properties": {"pixelSize": w}, "fields": "pixelSize"}})
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
    
    def _hide_gridlines(self, sheet):
        requests = [{"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}}]
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})

def init_orders_apply(sheets_manager, shopify_client=None, config=None) -> Dict[str, Any]:
    agent = SimpleOrdersSync(sheets_manager, shopify_client, config)
    return agent.init_orders_apply()

def sync_orders(sheets_manager, shopify_client, config=None) -> Dict[str, Any]:
    agent = SimpleOrdersSync(sheets_manager, shopify_client, config)
    return agent.sync_orders()

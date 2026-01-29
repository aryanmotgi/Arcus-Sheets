"""
Simple Orders Sync - ORDERS tab only implementation

Two commands:
1. init_orders_apply() - Creates/clears ORDERS tab with headers, formulas, formatting
2. sync_orders() - Fetches Shopify orders and writes to ORDERS tab
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

# New Headers (A:S) - 19 columns
ORDERS_HEADERS = [
    'Order #',            # A (Hidden ID helper)
    'Customer Name',      # B
    'Product',            # C
    'Size',               # D
    'Qty',                # E
    
    # Price Block
    'Shopify Price',      # F (Read-only)
    'Override Price',     # G (User)
    'Effective Price',    # H (Formula)
    
    'Revenue',            # I (Formula)
    
    # Shipping Charge Block
    'Shopify Ship Charge',# J (Read-only)
    'Override Ship Charge',# K (User)
    'Effective Ship Charge',# L (Formula)
    
    'Unit Cost',          # M
    
    # Label Cost Block
    'Auto Label Cost',    # N (Read-only/Placeholder)
    'Override Label Cost',# O (User)
    'Effective Label Cost',# P (Formula)
    
    # Financials
    'Total Collected',    # Q (Formula: Rev + EffShip)
    'Total Costs',        # R (Formula: COGS + EffLabel)
    'Profit',             # S (Formula)
    'Profit Margin %',    # T (Formula) wait, let's recount.
    
    # Let's map indices carefully.
    # 0: Order # (hidden tracking)
    # 1: Customer
    # 2: Product
    # 3: Size
    # 4: Qty
    # 5: Shop Price
    # 6: Over Price
    # 7: Eff Price
    # 8: Revenue
    # 9: Shop Ship
    # 10: Over Ship
    # 11: Eff Ship
    # 12: Unit Cost
    # 13: Auto Label
    # 14: Over Label
    # 15: Eff Label
    # 16: Total Collected
    # 17: Total Costs
    # 18: Profit
    # 19: Margin
    
    # Wait, user asked for:
    # "Shopify Payout" and "Fulfillment Status"?
    # Ah, I missed those in my previous mental list. Let me check requirements.
    # "Customer, Product, Size, Qty, Price..., Revenue..., Shipping..., Unit Cost, Label..., Profit, Margin, Payout, Fulfillment"
    # I should add Payout and Fulfillment at the end.
    
    'Shopify Payout',     # U
    'Fulfillment Status'  # V
]

# Recount: 22 Columns (A-V)
# Indices 0-21

DEFAULT_UNIT_COST = 12.26
FORMULA_ROWS = 2000
VALID_PRODUCTS = ["Arcus Tee", "All Paths Tee"]
VALID_SIZES = ["XS", "S", "M", "L", "XL", "XXL"]

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
            
            # Apply all formatting and validation
            self._apply_visuals(sheet) # Combined formatting
            self._apply_data_validation(sheet)
            self._fill_formulas(sheet)
            self._freeze_and_filter(sheet)
            self._set_column_widths(sheet)
            self._hide_gridlines(sheet)
            
            return {
                'success': True,
                'message': '✅ **ORDERS tab initialized!**\n\n'
                          f'📊 Columns: {len(ORDERS_HEADERS)} (A:V)\n'
                          '🛡️ Features: Persistent Overrides, Sync Protection\n'
                          '🎨 Formatting: Gray (Read-only), Yellow (Input)'
            }
            
        except Exception as e:
            self.logger.error(f"Error in init_orders_apply: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed to initialize ORDERS: {str(e)}'}
    
    def sync_orders(self) -> Dict[str, Any]:
        """Fetch Shopify orders and write to ORDERS tab (Preserving Overrides)"""
        self.logger.info("=== SYNC ORDERS ===")
        
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            
            # 1. READ EXISTING DATA (To preserve overrides)
            existing_values = sheet.get_all_values()
            
            # If empty or wrong headers, re-init
            if not existing_values or existing_values[0] != ORDERS_HEADERS:
                self.logger.info("Headers mismatch/new sheet, running init...")
                self.init_orders_apply()
                existing_values = [ORDERS_HEADERS] # Reset
                sheet = self.sheets_manager.spreadsheet.worksheet("ORDERS")
            
            # Build Overrides Map
            # Key: Order# + Product + Size (Composite Key to handle multi-line items)
            # Actually, Order# + LineItemIndex is safest, but we don't store index.
            # Order# + Product + Size + Variant is usually unique enough.
            # We will use: f"{Order#}|{Product}|{Size}"
            overrides_map = {} 
            
            if len(existing_values) > 1:
                # Indices for Overrides: 
                # Override Price (G) -> 6
                # Override Ship (K) -> 10
                # Override Label (O) -> 14
                
                for row in existing_values[1:]: # Skip header
                    if len(row) < 15: continue
                    order_num = row[0] # A
                    prod = row[2]      # C
                    size = row[3]      # D
                    
                    key = f"{order_num}|{prod}|{size}"
                    overrides_map[key] = {
                        'price': row[6],
                        'ship': row[10],
                        'label': row[14]
                    }
            
            # 2. FETCH SHOPIFY DATA
            orders = self.shopify_client.get_orders(limit=250, status='any')
            if not orders:
                return {'success': True, 'message': '⚠️ No orders found.'}
            
            unit_cost = self.config.get('profit', {}).get('cost_per_shirt', DEFAULT_UNIT_COST)
            
            rows = []
            orders_count = 0
            skipped_orders = 0
            
            for order in orders:
                try:
                    orders_count += 1
                    order_number = str(order.get('order_number', ''))
                    
                    # Customer
                    customer = order.get('customer', {}) or {}
                    customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or 'Guest'
                    
                    # Status & Pricing
                    fulfillment_status = (order.get('fulfillment_status') or 'unfulfilled').capitalize()
                    total_price = order.get('total_price', '') # Payout (not per item)
                    
                    # Shipping Charge (Shopify) - usually order level, needs allocation? 
                    # User asked for "Shopify Shipping Charge". 
                    # We'll put total shipping on the FIRST line item, 0 on others (similar to payout)
                    shipping_lines = order.get('shipping_lines', [])
                    shipping_charge = 0.0
                    for sl in shipping_lines:
                        try:
                            shipping_charge += float(sl.get('price', 0))
                        except: pass
                    
                    line_items = order.get('line_items', [])
                    if not line_items:
                        skipped_orders += 1
                        continue
                    
                    for i, item in enumerate(line_items):
                        raw_title = item.get('title', '')
                        raw_variant = item.get('variant_title', '') or ''
                        qty = int(item.get('quantity', 1))
                        price = float(item.get('price', 0))
                        
                        # Normalization
                        product_title, title_size = self._normalize_product_and_size(raw_title, raw_variant)
                        
                        # Allocation of Order-Level fields to First Row
                        payout_display = total_price if i == 0 else ''
                        ship_display = shipping_charge if i == 0 else 0.0
                        
                        # CHECK FOR OVERRIDES
                        key = f"{order_number}|{product_title}|{title_size}"
                        saved = overrides_map.get(key, {})
                        
                        override_price = saved.get('price', '')
                        override_ship = saved.get('ship', '')
                        override_label = saved.get('label', '')
                        
                        row = [
                            order_number,       # A (0)
                            customer_name,      # B (1)
                            product_title,      # C (2)
                            title_size,         # D (3)
                            qty,                # E (4)
                            
                            price,              # F (5) Shop Price
                            override_price,     # G (6) User Price
                            '',                 # H (7) Eff Price (Formula)
                            
                            '',                 # I (8) Revenue (Formula)
                            
                            ship_display,       # J (9) Shop Ship
                            override_ship,      # K (10) User Ship
                            '',                 # L (11) Eff Ship (Formula)
                            
                            unit_cost,          # M (12) Unit Cost
                            
                            '',                 # N (13) Auto Label (Blank for now)
                            override_label,     # O (14) User Label
                            '',                 # P (15) Eff Label (Formula)
                            
                            '',                 # Q (16) Tot Collected (Formula)
                            '',                 # R (17) Tot Costs (Formula)
                            '',                 # S (18) Profit (Formula)
                            '',                 # T (19) Margin (Formula)
                            
                            payout_display,     # U (20) Payout
                            fulfillment_status  # V (21) Status
                        ]
                        rows.append(row)
                        
                except Exception as e:
                    self.logger.warning(f"Error processing order: {e}")
                    skipped_orders += 1
            
            # 3. WRITE BACK
            # Clear & Update
            if len(sheet.get_all_values()) > 1:
                sheet.batch_clear([f'A2:V{len(sheet.get_all_values())}'])
            
            if rows:
                sheet.update(f'A2:V{len(rows) + 1}', rows, value_input_option='USER_ENTERED')
                
            # 4. RE-APPLY FORMULAS
            self._fill_formulas_for_rows(sheet, len(rows))
            
            return {
                'success': True,
                'message': f'✅ **Sync Complete (v3 Preserved Overrides)**\n'
                          f'📦 Orders: {orders_count}\n'
                          f'📝 Rows: {len(rows)}'
            }
            
        except Exception as e:
            self.logger.error(f"Error in sync_orders: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed to sync: {str(e)}'}

    def _normalize_product_and_size(self, title: str, variant: str):
        combined_text = (title + " " + variant).lower()
        clean_product = title 
        if "arcus" in combined_text: clean_product = "Arcus Tee"
        elif "all paths" in combined_text: clean_product = "All Paths Tee"
            
        clean_size = ""
        if "xxl" in combined_text: clean_size = "XXL"
        elif "xl" in combined_text or "extra large" in combined_text: clean_size = "XL"
        elif "large" in combined_text or " lg " in combined_text or combined_text.endswith(" lg"): clean_size = "L"
        elif "medium" in combined_text or " med " in combined_text or combined_text.endswith(" med"): clean_size = "M"
        elif "small" in combined_text or " sm " in combined_text or combined_text.endswith(" sm"): clean_size = "S"
        elif "xs" in combined_text or "extra small" in combined_text: clean_size = "XS"
        
        if not clean_size and variant.upper() in VALID_SIZES: clean_size = variant.upper()
        if not clean_size:
            v_upper = variant.upper().strip()
            if v_upper in ["S", "M", "L", "XL"]: clean_size = v_upper

        return clean_product, clean_size

    # ============================================
    # VISUALS & FORMULAS
    # ============================================
    
    def _apply_visuals(self, sheet):
        requests = []
        
        # Header Formatting
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": len(ORDERS_HEADERS)},
                "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True, "fontSize": 10}, "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE"}},
                "fields": "userEnteredFormat"
            }
        })
        
        # Columns Coloring
        # Read Only (Gray): F(5), J(9), N(13)
        # Input (Yellow): G(6), K(10), O(14)
        # Effective (White/Bold): H(7), L(11), P(15)
        
        # Read Only
        for c in [5, 9, 13]:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": c, "endColumnIndex": c+1}, "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95}}}, "fields": "userEnteredFormat.backgroundColor"}})
            
        # Inputs
        for c in [6, 10, 14]:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": c, "endColumnIndex": c+1}, "cell": {"userEnteredFormat": {"backgroundColor": {"red": 1.0, "green": 0.98, "blue": 0.85}}}, "fields": "userEnteredFormat.backgroundColor"}})
        
        # Borders (All)
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 0, "endColumnIndex": len(ORDERS_HEADERS)},
                "cell": {"userEnteredFormat": {"borders": {"top": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}, "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}, "left": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}, "right": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}}, "horizontalAlignment": "CENTER"}},
                "fields": "userEnteredFormat(borders,horizontalAlignment)"
            }
        })
        
        # Conditionals (Profit, Status, Arcus, Label)
        # Profit (Col S, Index 18) > 0 Green, < 0 Red
        # Label Missing (Col O, Index 14) Blank Yellow -- Actually check Effective Label (Col P, Index 15)?? 
        # User said "Shipping label cost blank (Effective Label Cost blank) yellow" -> P
        
        ranges_prof = [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 18, "endColumnIndex": 19}]
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges_prof, "booleanRule": {"condition": {"type": "NUMBER_GREATER", "values": [{"userEnteredValue": "0"}]}, "format": {"backgroundColor": {"red": 0.85, "green": 0.95, "blue": 0.85}, "textFormat": {"foregroundColor": {"red": 0, "green": 0.4, "blue": 0}}}}}, "index": 0}})
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges_prof, "booleanRule": {"condition": {"type": "NUMBER_LESS", "values": [{"userEnteredValue": "0"}]}, "format": {"backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.9}, "textFormat": {"foregroundColor": {"red": 0.8, "green": 0, "blue": 0}}}}}, "index": 1}})
        
        # Effective Label Blank -> Yellow (P, Index 15)
        ranges_lbl = [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 15, "endColumnIndex": 16}]
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges_lbl, "booleanRule": {"condition": {"type": "BLANK"}, "format": {"backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8}}}}, "index": 2}})
        
        # Fulfillment (Col V, Index 21)
        ranges_stat = [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 21, "endColumnIndex": 22}]
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges_stat, "booleanRule": {"condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Fulfilled"}]}, "format": {"backgroundColor": {"red": 0.8, "green": 1.0, "blue": 0.8}}}}, "index": 3}})
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges_stat, "booleanRule": {"condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Unfulfilled"}]}, "format": {"backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.8}}}}, "index": 4}})
        
        # Product Rows (Arcus/AllPaths) - Affects whole row (0-22)
        ranges_all = [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 0, "endColumnIndex": 22}]
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges_all, "booleanRule": {"condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "Arcus Tee"}]}, "format": {"backgroundColor": {"red": 0.96, "green": 0.96, "blue": 0.96}}}}, "index": 5}})
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges_all, "booleanRule": {"condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "All Paths Tee"}]}, "format": {"backgroundColor": {"red": 0.96, "green": 0.94, "blue": 1.0}}}}, "index": 6}})
        
        # Currency Format
        # F-H (5-7), I(8), J-L(9-11), M-P(12-15), Q-S(16-18), U(20)
        curr_cols = [5,6,7, 8, 9,10,11, 12,13,14,15, 16,17,18, 20]
        for c in curr_cols:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": c, "endColumnIndex": c+1}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # Percent Format T(19)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 19, "endColumnIndex": 20}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        sheet.spreadsheet.batch_update({"requests": requests})
        
    def _fill_formulas(self, sheet):
        self._fill_formulas_for_rows(sheet, FORMULA_ROWS)
        
    def _fill_formulas_for_rows(self, sheet, num_rows):
        if num_rows == 0: return
        # Eff Price (H) = IF(G, G, F)
        # Revenue (I) = E*H
        # Eff Ship (L) = IF(K, K, J)
        # Eff Label (P) = IF(O, O, N)
        # Total Collected (Q) = I + L
        # Total Costs (R) = (M*E) + P
        # Profit (S) = Q - R
        # Margin (T) = S / Q
        
        f_eff_price = []
        f_revenue = []
        f_eff_ship = []
        f_eff_label = []
        f_coll = []
        f_cost = []
        f_prof = []
        f_marg = []
        
        for r in range(2, num_rows + 2):
            f_eff_price.append([f'=IF(G{r}<>"", G{r}, F{r})'])
            f_revenue.append([f'=IFERROR(E{r}*H{r}, "")'])
            f_eff_ship.append([f'=IF(K{r}<>"", K{r}, J{r})'])
            f_eff_label.append([f'=IF(O{r}<>"", O{r}, N{r})'])
            f_coll.append([f'=IFERROR(I{r}+L{r}, "")'])
            f_cost.append([f'=IFERROR((M{r}*E{r})+P{r}, "")'])
            f_prof.append([f'=IFERROR(Q{r}-R{r}, "")'])
            f_marg.append([f'=IFERROR(S{r}/Q{r}, "")'])
            
        sheet.update(f'H2:H{num_rows+1}', f_eff_price, value_input_option='USER_ENTERED')
        sheet.update(f'I2:I{num_rows+1}', f_revenue, value_input_option='USER_ENTERED')
        sheet.update(f'L2:L{num_rows+1}', f_eff_ship, value_input_option='USER_ENTERED')
        sheet.update(f'P2:P{num_rows+1}', f_eff_label, value_input_option='USER_ENTERED')
        sheet.update(f'Q2:Q{num_rows+1}', f_coll, value_input_option='USER_ENTERED')
        sheet.update(f'R2:R{num_rows+1}', f_cost, value_input_option='USER_ENTERED')
        sheet.update(f'S2:S{num_rows+1}', f_prof, value_input_option='USER_ENTERED')
        sheet.update(f'T2:T{num_rows+1}', f_marg, value_input_option='USER_ENTERED')

    def _apply_data_validation(self, sheet):
        requests = []
        # Product (Col C, Index 2)
        requests.append({"setDataValidation": {"range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 2, "endColumnIndex": 3}, "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in VALID_PRODUCTS]}, "showCustomUi": True}}})
        # Size (Col D, Index 3)
        requests.append({"setDataValidation": {"range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 3, "endColumnIndex": 4}, "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in VALID_SIZES]}, "showCustomUi": True}}})
        sheet.spreadsheet.batch_update({"requests": requests})

    def _freeze_and_filter(self, sheet):
        requests = [{"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}}, {"setBasicFilter": {"filter": {"range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 0, "endColumnIndex": len(ORDERS_HEADERS)}}}}]
        sheet.spreadsheet.batch_update({"requests": requests})
    
    def _set_column_widths(self, sheet):
        # 0(Order#) Hidden? No, keep small. 
        # A(0)=50, B(1)=150, C(2)=150, D(3)=60, E(4)=40
        # F-H(5-7)=80, I(8)=80, J-L(9-11)=80, M(12)=70, N-P(13-15)=80
        # Q-S(16-18)=80, T(19)=60, U(20)=80, V(21)=100
        widths = [50, 150, 150, 60, 40] + [80]*3 + [80] + [80]*3 + [70] + [80]*3 + [80]*3 + [60, 80, 100]
        requests = []
        for i, w in enumerate(widths):
            requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1}, "properties": {"pixelSize": w}, "fields": "pixelSize"}})
        sheet.spreadsheet.batch_update({"requests": requests})
    
    def _hide_gridlines(self, sheet):
        sheet.spreadsheet.batch_update({"requests": [{"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}}]})

# STANDALONE
def init_orders_apply(sheets_manager, shopify_client=None, config=None) -> Dict[str, Any]:
    agent = SimpleOrdersSync(sheets_manager, shopify_client, config)
    return agent.init_orders_apply()

def sync_orders(sheets_manager, shopify_client, config=None) -> Dict[str, Any]:
    agent = SimpleOrdersSync(sheets_manager, shopify_client, config)
    return agent.sync_orders()

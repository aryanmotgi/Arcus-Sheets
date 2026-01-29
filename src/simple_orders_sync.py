"""
Simple Orders Sync - ORDERS tab only implementation (Strict Layout v4)

Two commands:
1. init_orders_apply() - Creates/clears ORDERS tab with headers, formulas, formatting
2. sync_orders() - Fetches Shopify orders and writes to ORDERS tab
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)

# STRIP LAYOUT - 10 Visible Columns (+ Hidden Order# at start)
# [0] Order # (Hidden, Key)
# [1] A: Customer Name
# [2] B: Product
# [3] C: Size
# [4] D: Qty
# [5] E: Unit Cost (Editable, Persists)
# [6] F: Price Bought (Editable, Persists)
# [7] G: Revenue (Formula)
# [8] H: Shopify Shipping (Editable, Persists)
# [9] I: Pirate Ship Label Cost (Editable, Persists)
# [10] J: Profit (Formula)

ORDERS_HEADERS = [
    'Order #',       # Hidden (Col Index 0)
    'Customer Name', # A (1)
    'Product',       # B (2)
    'Size',          # C (3)
    'Qty',           # D (4)
    'Unit Cost',     # E (5) - Source of Truth
    'Price Bought',  # F (6) - Source of Truth
    'Revenue',       # G (7) - Formula
    'Shopify Shipping', # H (8) - Source of Truth
    'Pirate Ship Label Cost', # I (9) - Source of Truth
    'Profit'         # J (10) - Formula
]

DEFAULT_UNIT_COST = 12.26
FORMULA_ROWS = 2000
VALID_PRODUCTS = ["Arcus Tee", "All Paths Tee"]
VALID_SIZES = ["XS", "S", "M", "L", "XL", "XXL"]

class SimpleOrdersSync:
    
    def __init__(self, sheets_manager, shopify_client, config=None):
        self.sheets_manager = sheets_manager
        self.shopify_client = shopify_client
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def init_orders_apply(self) -> Dict[str, Any]:
        self.logger.info("=== INIT ORDERS APPLY (Strict Layout) ===")
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            sheet.clear()
            
            # Write headers
            sheet.update('A1', [ORDERS_HEADERS], value_input_option='USER_ENTERED')
            
            # Apply Visuals & Validation
            self._apply_visuals(sheet)
            self._apply_data_validation(sheet)
            self._fill_formulas(sheet)
            self._freeze_and_filter(sheet)
            self._set_column_widths(sheet)
            self._hide_gridlines(sheet)
            self._hide_id_column(sheet)
            
            return {'success': True, 'message': '✅ **ORDERS Layout Applied!**\nStrict 10-column layout with persistent edits.'}
        except Exception as e:
            return {'success': False, 'message': f'❌ Init failed: {str(e)}'}
    
    def sync_orders(self) -> Dict[str, Any]:
        self.logger.info("=== SYNC ORDERS (Smart Persistence) ===")
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            
            # 1. READ EXISTING MANUALLY EDITED VALUES
            overrides_map = {}
            existing_values = sheet.get_all_values()
            
            if existing_values and existing_values[0] == ORDERS_HEADERS:
                for row in existing_values[1:]:
                    if len(row) < 10: continue
                    # Key: Order#|Product|Size
                    key = f"{row[0]}|{row[2]}|{row[3]}"
                    
                    # Store editable columns if they have values
                    # Col 5 (Unit Cost), 6 (Price), 8 (Ship), 9 (Label)
                    overrides_map[key] = {
                        'cost': row[5],
                        'price': row[6],
                        'ship': row[8],
                        'label': row[9]
                    }
            
            # 2. FETCH SHOPIFY DATA
            orders = self.shopify_client.get_orders(limit=250, status='any')
            if not orders: return {'success': True, 'message': '⚠️ No orders found.'}
            
            rows = []
            
            for order in orders:
                try:
                    order_num = str(order.get('order_number', ''))
                    customer = order.get('customer', {}) or {}
                    c_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or 'Guest'
                    
                    # Shipping total (allocated to first item)
                    shipping_total = 0.0
                    for sl in order.get('shipping_lines', []):
                        try: shipping_total += float(sl.get('price', 0))
                        except: pass
                    
                    for i, item in enumerate(order.get('line_items', [])):
                        raw_title = item.get('title', '')
                        raw_variant = item.get('variant_title', '') or ''
                        qty = int(item.get('quantity', 1))
                        shop_price = float(item.get('price', 0))
                        
                        prod, size = self._normalize(raw_title, raw_variant)
                        
                        # Allocated values (First item gets shipping)
                        row_ship = shipping_total if i == 0 else 0.0
                        
                        # CHECK FOR PERSISTENT OVERRIDES
                        key = f"{order_num}|{prod}|{size}"
                        saved = overrides_map.get(key, {})
                        
                        # Logic: Use Saved value if exists, else use Shopify/Default
                        final_cost = saved.get('cost') if saved.get('cost') else DEFAULT_UNIT_COST
                        final_price = saved.get('price') if saved.get('price') else shop_price
                        final_ship = saved.get('ship') if saved.get('ship') else row_ship
                        final_label = saved.get('label') if saved.get('label') else ''
                        
                        row = [
                            order_num,      # [0] ID
                            c_name,         # [1] Name
                            prod,           # [2] Prod
                            size,           # [3] Size
                            qty,            # [4] Qty
                            final_cost,     # [5] COST (Persists)
                            final_price,    # [6] PRICE (Persists)
                            '',             # [7] Revenue (Formula)
                            final_ship,     # [8] SHIP (Persists)
                            final_label,    # [9] LABEL (Persists)
                            ''              # [10] Profit (Formula)
                        ]
                        rows.append(row)
                        
                except Exception as e:
                    self.logger.warning(f"Error row: {e}")
            
            # 3. WRITE BACK
            if len(sheet.get_all_values()) > 0:
                sheet.batch_clear([f'A2:K{len(sheet.get_all_values())}']) # Clear A-K (Hidden 0 is before A?? No 0 maps to A. Range A:K covers indices 0-10)
            
            if rows:
                sheet.update(f'A2:K{len(rows)+1}', rows, value_input_option='USER_ENTERED')
                
            self._fill_formulas_for_rows(sheet, len(rows))
            
            return {'success': True, 'message': f'✅ **Sync Complete**\nItems: {len(rows)}\nEdits preserved via Order# Match.'}
            
        except Exception as e:
            return {'success': False, 'message': f'❌ Sync failed: {str(e)}'}

    def _normalize(self, t, v):
        ct = (t + " " + v).lower()
        p = t 
        if "arcus" in ct: p = "Arcus Tee"
        elif "all paths" in ct: p = "All Paths Tee"
        
        s = ""
        if "xxl" in ct: s="XXL"
        elif "xl" in ct or "extra large" in ct: s="XL"
        elif "large" in ct or " lg " in ct or ct.endswith(" lg"): s="L"
        elif "medium" in ct or " med " in ct or ct.endswith(" med"): s="M"
        elif "small" in ct or " sm " in ct or ct.endswith(" sm"): s="S"
        elif "xs" in ct: s="XS"
        
        if not s and v.upper() in VALID_SIZES: s = v.upper()
        if not s:
            vu = v.upper().strip()
            if vu in ["S", "M", "L", "XL"]: s = vu
        return p, s

    def _apply_visuals(self, sheet):
        requests = []
        # Header (A1:K1) -> Index 0-11
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 1, "endColumnIndex": 11}, "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True}, "horizontalAlignment": "CENTER"}}, "fields": "userEnteredFormat"}})
        
        # Borders & Center (All)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 1, "endColumnIndex": 11}, "cell": {"userEnteredFormat": {"borders": {"top": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}, "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}, "left": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}, "right": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}}, "horizontalAlignment": "CENTER"}}, "fields": "userEnteredFormat"}})
        
        # Product Highlight (Darker)
        # Arcus (Dark Gray #505050)
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 1, "endColumnIndex": 11}], "booleanRule": {"condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "Arcus Tee"}]}, "format": {"backgroundColor": {"red": 0.3, "green": 0.3, "blue": 0.3}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}}}}}, "index": 0}})
        # All Paths (Dark Purple #4B0082)
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 1, "endColumnIndex": 11}], "booleanRule": {"condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "All Paths Tee"}]}, "format": {"backgroundColor": {"red": 0.29, "green": 0.0, "blue": 0.51}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}}}}}, "index": 1}})
        
        # Profit Colors (Col J -> Index 10)
        r_prof = [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 10, "endColumnIndex": 11}]
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": r_prof, "booleanRule": {"condition": {"type": "NUMBER_GREATER", "values": [{"userEnteredValue": "0"}]}, "format": {"backgroundColor": {"red": 0.0, "green": 0.5, "blue": 0.0}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True}}}}, "index": 2}})
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": r_prof, "booleanRule": {"condition": {"type": "NUMBER_LESS", "values": [{"userEnteredValue": "0"}]}, "format": {"backgroundColor": {"red": 0.6, "green": 0.0, "blue": 0.0}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True}}}}, "index": 3}})
        
        # Currency Format
        # Cols: Cost(5), Price(6), Rev(7), Ship(8), Label(9), Prof(10)
        for c in [5,6,7,8,9,10]:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": c, "endColumnIndex": c+1}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})

        sheet.spreadsheet.batch_update({"requests": requests})
    
    def _fill_formulas(self, sheet):
        self._fill_formulas_for_rows(sheet, FORMULA_ROWS)
        
    def _fill_formulas_for_rows(self, sheet, num_rows):
        # Revenue(G) = Qty(D)*Price(F)
        # Profit(J) = (Rev(G)+Ship(H)) - (Qty(D)*Cost(E)) - Label(I)
        # Note: Columns are 1-based letters. D=4, E=5, F=6, G=7, H=8, I=9, J=10
        # Wait, indices in array 0-based are correct. Letters:
        # 0:A (ID) (Hidden)
        # 1:B (Name)
        # 2:C (Prod)
        # 3:D (Size)
        # 4:E (Qty) -> WAIT. In array above: Qty is [4].
        # Let's map strict letters from Google Sheets view.
        # User sees: A(Name), B(Prod), C(Size), D(Qty), E(Cost), F(Price), G(Rev), H(Ship), I(Label), J(Prof).
        # My array `rows` has ID at index 0.
        # So actual sheet columns:
        # Col A = ID (Hidden)
        # Col B = Customer (Visible First)
        # Col C = Product
        # Col D = Size
        # Col E = Qty
        # Col F = Cost
        # Col G = Price
        # Col H = Rev
        # Col I = Ship
        # Col J = Label
        # Col K = Profit
        
        # Okay, I need to align my hidden column strategy.
        # I will write ID to Col A and HIDE Col A.
        # Then formulas:
        # Rev (H) = E * G
        # Prof (K) = (H + I) - (E * F) - J
        
        f_rev = []
        f_prof = []
        for r in range(2, num_rows+2):
            f_rev.append([f'=IFERROR(E{r}*G{r}, "")'])
            f_prof.append([f'=IFERROR((H{r}+I{r}) - (E{r}*F{r}) - J{r}, "")'])
            
        sheet.update(f'H2:H{num_rows+1}', f_rev, value_input_option='USER_ENTERED')
        sheet.update(f'K2:K{num_rows+1}', f_prof, value_input_option='USER_ENTERED')

    def _apply_data_validation(self, sheet):
        # Product (C), Size (D)
        requests = []
        requests.append({"setDataValidation": {"range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 2, "endColumnIndex": 3}, "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in VALID_PRODUCTS]}, "showCustomUi": True}}})
        requests.append({"setDataValidation": {"range": {"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 3, "endColumnIndex": 4}, "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in VALID_SIZES]}, "showCustomUi": True}}})
        sheet.spreadsheet.batch_update({"requests": requests})

    def _freeze_and_filter(self, sheet):
        requests = [{"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}}, {"setBasicFilter": {"filter": {"range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 1, "endColumnIndex": 11}}}}]
        sheet.spreadsheet.batch_update({"requests": requests})
    
    def _set_column_widths(self, sheet):
        # A(Hidden), B(150), C(200), D(60), E(50), F(80), G(80), H(80), I(80), J(80), K(80)
        widths = [150, 200, 60, 50, 80, 80, 80, 80, 80, 80]
        requests = []
        for i, w in enumerate(widths):
            # Start index 1 (B)
            requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": i+1, "endIndex": i+2}, "properties": {"pixelSize": w}, "fields": "pixelSize"}})
        sheet.spreadsheet.batch_update({"requests": requests})

    def _hide_id_column(self, sheet):
        sheet.spreadsheet.batch_update({"requests": [{"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"hiddenByUser": True}, "fields": "hiddenByUser"}}]})
        
    def _hide_gridlines(self, sheet):
        sheet.spreadsheet.batch_update({"requests": [{"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}}]})

# STANDALONE
def init_orders_apply(sheets_manager, shopify_client=None, config=None) -> Dict[str, Any]:
    agent = SimpleOrdersSync(sheets_manager, shopify_client, config)
    return agent.init_orders_apply()

def sync_orders(sheets_manager, shopify_client, config=None) -> Dict[str, Any]:
    agent = SimpleOrdersSync(sheets_manager, shopify_client, config)
    return agent.sync_orders()

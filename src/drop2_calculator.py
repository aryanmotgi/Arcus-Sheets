"""
Drop 2 Finance Calculator (Refined Split-Screen Layout)
- Layout: Left side (A/B) for Inputs & Costs, Right side (D/E) for Sales & Risk.
- Total Investment Model: Focuses on sunk costs and payout.
- Dynamic Linkage: Side-by-side dashboard and sections.
- Professional UI: Navy/White headers, Light Gray calcs, Yellow inputs, Green goals.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Drop2Calculator:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.logger = logger
        self.sheet_name = "Drop 2 Finance Predictions"

    def create_prediction_sheet(self) -> Dict[str, Any]:
        self.logger.info("=== REBUILD DROP 2 FINANCE (EXACT SPLIT SPECS) ===")
        
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists(self.sheet_name)
            
            # 1. READ EXISTING VALUES (Persistence)
            existing_values = {}
            try:
                raw_data = sheet.get_all_values()
                if raw_data:
                    for row in raw_data:
                        # Scan both sides for labels (Col A and Col D)
                        for i in [0, 3]: 
                            if len(row) > i+1:
                                label = row[i].strip()
                                val = row[i+1].strip()
                                if label and val:
                                    existing_values[label] = val
            except Exception as e:
                self.logger.warning(f"Persistence read failed: {e}")

            def get_val(label, default):
                saved = existing_values.get(label)
                if saved and not str(saved).startswith("="):
                    return saved
                return default

            # --- INPUT DEFAULTS ---
            v_small = get_val("Small Sets", "15")
            v_med = get_val("Medium Sets", "25")
            v_large = get_val("Large Sets", "20")
            v_pps = get_val("Pieces per Set (input)", "2")
            
            v_sample = get_val("Sample Cost", "234.63")
            v_bulk = get_val("Bulk Order Cost", "1550.00")
            v_pack = get_val("Packaging & Supplies", "50.00")
            v_ship_me = get_val("Shipping to Me", "45.00")
            v_other = get_val("Other Costs", "0.00")
            
            v_c_hoodie = get_val("Hoodie Unit Cost", "12.00")
            v_c_pants = get_val("Pants Unit Cost", "10.00")
            
            v_label = get_val("Shipping Label Cost per Order", "6.44")
            
            v_p_hoodie = get_val("Hoodie Sell Price", "45.00")
            v_p_pants = get_val("Pants Sell Price", "35.00")
            v_p_set = get_val("Set Sell Price (Bundle)", "65.00")

            # --- DATA ARRAY (5 COLUMNS: A, B, C, D, E) ---
            # Dashboard: Rows 1-11
            # Sections: Row 12+
            
            data = [
                ["DROP 2 FINANCE PREDICTIONS", "", "", "", ""],                             # R1
                ["", "", "", "", ""],                                                       # R2
                ["KEY METRICS DASHBOARD (LEFT)", "", "", "KEY METRICS DASHBOARD (RIGHT)", ""], # R3 (Header)
                ["Total Potential Revenue", "=E24", "", "Revenue Per Set (E16)", "=E16"],   # R4
                ["Your Net Profit (The Payout)", "=E25", "", "Profit Per Set", "=E21"],     # R5 (Green)
                ["Sets to Break Even", "=E32", "", "Profit Margin %", "=E26"],              # R6
                ["Giveaway/Damage Buffer", "=E29", "", "Price Floor (Zero Profit)", "=E30"],# R7 (Buffer=Green)
                ["Pure Profit per set", "=E21", "", "Ad-Spend Limit (Keep $1k Profit)", "=E31"], # R8
                ["Inv. per Set (Avg)", "=B32", "", "", ""],                                 # R9
                ["", "", "", "", ""],                                                       # R10
                ["", "", "", "", ""],                                                       # R11
                
                # Split Sections
                ["SECTION A — Drop Quantities", "", "", "SECTION E — Pricing (INPUTS)", ""],# R12
                ["Small Sets", v_small, "", "Hoodie Sell Price", v_p_hoodie],               # R13
                ["Medium Sets", v_med, "", "Pants Sell Price", v_p_pants],                  # R14
                ["Large Sets", v_large, "", "Set Sell Price (Bundle)", v_p_set],            # R15
                ["Total Sets", "=SUM(B13:B15)", "", "Revenue Per Set", "=IF(E15>0, E15, E13+E14)"], # R16 (E16)
                ["Pieces per Set (input)", v_pps, "", "", ""],                              # R17
                ["Total Pieces", "=B16*B17", "", "", ""],                                   # R18
                ["", "", "", "", ""],                                                       # R19
                
                ["SECTION B — Total Investment", "", "", "SECTION F — Profit Breakdown", ""], # R20
                ["Sample Cost", v_sample, "", "Pure Profit per set", "=E16 - B35"],         # R21 (E21)
                ["Bulk Order Cost", v_bulk, "", "Hoodie Profit post-BE", "=IF((E13+E14)>0, (E16*(E13/(E13+E14)))-(B35/2), 0)"], # R22
                ["Packaging & Supplies", v_pack, "", "Pants Profit post-BE", "=IF((E13+E14)>0, (E16*(E14/(E13+E14)))-(B35/2), 0)"],  # R23
                ["Shipping to Me", v_ship_me, "", "Total Potential Revenue", "=E16*B16"],   # R24 (E24)
                ["Other Costs", v_other, "", "Your Net Profit (The Payout)", "=E24 - B26"],# R25 (E25)
                ["Total Investment Spent", "=SUM(B21:B25)", "", "Net Profit Margin %", "=IF(E24>0, E25/E24, 0)"], # R26 (E26)
                ["", "", "", "", ""],                                                       # R27
                
                ["SECTION C — Unit Tracking", "", "", "SECTION H — Risk Scenarios", ""],    # R28
                ["Hoodie Unit Cost", v_c_hoodie, "", "Giveaway/Damage Buffer", "=B16 - E32"],# R29 (E29)
                ["Pants Unit Cost", v_c_pants, "", "Price Floor (Zero Profit)", "=(B26/B16) + B35"], # R30 (E30)
                ["Set Unit Cost", "=B29+B30", "", "Ad-Spend Limit (Keep $1k Profit)", "=E25 - 1000"], # R31 (E31)
                ["Investment per Set (Avg)", "=B26/B16", "", "Sets to Break Even", "=IF(E21>0, CEILING(B26/E21, 1), \"N/A\")"], # R32 (E32)
            ]
            
            sheet.clear()
            sheet.update("A1", data, value_input_option="USER_ENTERED")
            self._format_sheet(sheet)
            
            return {'success': True, 'message': '✅ Split-Screen Dashboard Rebuilt Successfully!'}
            
        except Exception as e:
            self.logger.error(f"Error: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Error: {str(e)}'}

    def _format_sheet(self, sheet):
        requests = []
        
        # 1. Base Setup (White BG, No Grid)
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        # 2. Main Title (R1) - Spanning A:E
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 5}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 20, "bold": True}, "horizontalAlignment": "CENTER"}}, "fields": "userEnteredFormat"}})
        
        # 3. Navy Headers (Bold White Text) #1C2833
        NAVY = {"red": 0.11, "green": 0.16, "blue": 0.20}
        WHITE = {"red": 1, "green": 1, "blue": 1}
        # Header Rows Indices: 2, 11, 19, 27
        header_indices = [2, 11, 19, 27]
        for idx in header_indices:
            # Header on Left side (Cols A-B)
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": idx, "endRowIndex": idx+1, "startColumnIndex": 0, "endColumnIndex": 2},
                    "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 14, "bold": True, "foregroundColor": WHITE}, "backgroundColor": NAVY}},
                    "fields": "userEnteredFormat"
                }
            })
            # Header on Right side (Cols D-E)
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": idx, "endRowIndex": idx+1, "startColumnIndex": 3, "endColumnIndex": 5},
                    "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 14, "bold": True, "foregroundColor": WHITE}, "backgroundColor": NAVY}},
                    "fields": "userEnteredFormat"
                }
            })

        # 4. Big Metric Values in Dashboard (R4-R9)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 3, "endRowIndex": 9, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 15, "bold": True}}}, "fields": "userEnteredFormat.textFormat"}})
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 3, "endRowIndex": 9, "startColumnIndex": 4, "endColumnIndex": 5}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 15, "bold": True}}}, "fields": "userEnteredFormat.textFormat"}})

        # Green Profile Goals (Payout & Buffers)
        BRIGHT_GREEN = {"red": 0.85, "green": 0.95, "blue": 0.85}
        # Payout: Dashboard R5 (A-B)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 4, "endRowIndex": 5, "startColumnIndex": 0, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": BRIGHT_GREEN}}, "fields": "userEnteredFormat.backgroundColor"}})
        # Buffer: Dashboard R7 (A-B) and Section H R56 (D-E)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 6, "endRowIndex": 7, "startColumnIndex": 0, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": BRIGHT_GREEN}}, "fields": "userEnteredFormat.backgroundColor"}})
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 28, "endRowIndex": 29, "startColumnIndex": 3, "endColumnIndex": 5}, "cell": {"userEnteredFormat": {"backgroundColor": BRIGHT_GREEN}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 5. Cell Role Colors (Inputs = Yellow, Calcs = Gray)
        YELLOW = {"red": 1.0, "green": 0.98, "blue": 0.85}
        GRAY = {"red": 0.94, "green": 0.94, "blue": 0.94}
        
        # Explicit Inputs (Yellow)
        input_ranges = [
            (12, 14, 1), # Quantities A
            (16, 16, 1), # PPS
            (20, 24, 1), # Investment B
            (28, 29, 1), # Unit Costs C
            (12, 14, 4), # Pricing E
        ]
        for s, e, col in input_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": s, "endRowIndex": e+1, "startColumnIndex": col, "endColumnIndex": col+1}, "cell": {"userEnteredFormat": {"backgroundColor": YELLOW, "textFormat": {"bold": True}}}, "fields": "userEnteredFormat"}})

        # Explicit Calculations (Gray)
        calc_ranges = [
            (3, 8, 1),  (3, 8, 4),     # Dashboard
            (15, 15, 1), (17, 17, 1),  # A Calcs
            (25, 25, 1),               # B Calcs
            (30, 31, 1),               # C Calcs
            (15, 15, 4), (20, 25, 4),  # F Calcs
            (29, 31, 4),               # H Calcs
        ]
        for s, e, col in calc_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": s, "endRowIndex": e+1, "startColumnIndex": col, "endColumnIndex": col+1}, "cell": {"userEnteredFormat": {"backgroundColor": GRAY}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 6. Formats (Currency, Percent, Number)
        # Currency
        for col in [1, 4]:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 3, "endRowIndex": 32, "startColumnIndex": col, "endColumnIndex": col+1}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})
        
        # Percent: Margin R6 (Index 5), Net Margin R26 (Index 25)
        for rng in [(5, 4), (25, 4)]:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": rng[0], "endRowIndex": rng[0]+1, "startColumnIndex": rng[1], "endColumnIndex": rng[1]+1}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # Whole Number (Sets/Buffers)
        for rng in [(5, 1), (6, 1), (28, 4), (31, 4)]:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": rng[0], "endRowIndex": rng[0]+1, "startColumnIndex": rng[1], "endColumnIndex": rng[1]+1}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "0"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 7. Layout (Column Widths)
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 250}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 120}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3}, "properties": {"pixelSize": 50}, "fields": "pixelSize"}}) # Spacer 50px
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4}, "properties": {"pixelSize": 250}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 4, "endIndex": 5}, "properties": {"pixelSize": 120}, "fields": "pixelSize"}})

        sheet.spreadsheet.batch_update({"requests": requests})

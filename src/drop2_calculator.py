"""
Drop 2 Finance Calculator (Final Side-by-Side Dashboard)
- Layout: Left side (A/B/C) for Inputs & Costs, Right side (D/E) for Sales & Risk.
- Logic: Total Investment model with "Pure Profit" (Price - Shipping).
- UI: Navy Blue headers (#1C2833) with Bold White text.
- Persistence: Preserves user inputs via get_val.
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
        self.logger.info("=== REBUILD DROP 2 FINANCE (FINAL POLISH) ===")
        
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists(self.sheet_name)
            
            # 1. READ EXISTING VALUES (Persistence)
            existing_values = {}
            try:
                raw_data = sheet.get_all_values()
                if raw_data:
                    for row in raw_data:
                        # Scan Col A and Col D for labels
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

            v_sell_through = get_val("Projected Sell-Through %", "100%")
            v_discount = get_val("Discount %", "0%")

            # --- DATA ARRAY (5 COLUMNS: A, B, C, D, E) ---
            # Dashboard: Rows 1-11
            # Sections: Row 12+
            
            data = [
                ["DROP 2 FINANCE PREDICTIONS", "", "", "", ""],                             # R1 (Title)
                ["", "", "", "", ""],                                                       # R2 (Title Merge)
                ["", "", "", "", ""],                                                       # R3 (Spacer)
                ["KEY METRICS (INPUTS & COSTS)", "", "", "KEY METRICS (SALES & RISK)", ""], # R4
                ["Total Potential Revenue", "=E24", "", "Revenue Per Set (E16)", "=E16"],   # R5
                ["Your Net Profit (The Payout)", "=E25", "", "Profit Per Set", "=E21"],     # R6
                ["Sets to Break Even", "=E33", "", "Profit Margin %", "=E26"],              # R7
                ["Giveaway/Damage Buffer", "=E29", "", "Price Floor (Zero Profit)", "=E30"],# R8
                ["Pure Profit per set", "=E21", "", "Marketing Budget (to keep $1k Profit)", "=E31"], # R9
                ["", "", "", "", ""],                                                       # R10
                ["", "", "", "", ""],                                                       # R11
                
                # Split Sections Start
                ["SECTION A — Drop Quantities", "", "", "SECTION E — Pricing (INPUTS)", ""],# R12
                ["Small Sets", v_small, "", "Hoodie Sell Price", v_p_hoodie],               # R13
                ["Medium Sets", v_med, "", "Pants Sell Price", v_p_pants],                  # R14
                ["Large Sets", v_large, "", "Set Sell Price (Bundle)", v_p_set],            # R15
                ["Total Sets", "=SUM(B13:B15)", "", "Revenue Per Set", "=IF(E15>0, E15, E13+E14)"], # R16
                ["Pieces per Set (input)", v_pps, "", "", ""],                              # R17
                ["Total Pieces", "=B16*B17", "", "", ""],                                   # R18
                ["", "", "", "", ""],                                                       # R19
                
                ["SECTION B — Total Investment", "", "", "SECTION F — Profit Breakdown", ""], # R20
                ["Sample Cost", v_sample, "", "Pure Profit per set", "=E16 - B32"],         # R21
                ["Bulk Order Cost", v_bulk, "", "Hoodie Profit post-BE", "=IF((E13+E14)>0, (E16*(E13/(E13+E14)))-(B32/2), 0)"], # R22
                ["Packaging & Supplies", v_pack, "", "Pants Profit post-BE", "=IF((E13+E14)>0, (E16*(E14/(E13+E14)))-(B32/2), 0)"],  # R23
                ["Shipping to Me", v_ship_me, "", "Total Potential Revenue", "=E16*B16"],   # R24
                ["Other Costs", v_other, "", "Your Net Profit (The Payout)", "=(E21*B16) - B26"],# R25
                ["Total Investment Spent", "=SUM(B21:B25)", "", "Net Profit Margin %", "=IF(E24>0, E25/E24, 0)"], # R26
                ["", "", "", "", ""],                                                       # R27
                
                ["SECTION C — Unit Tracking", "", "", "SECTION H — Risk Scenarios", ""],    # R28
                ["Hoodie Unit Cost", "=B31/2", "", "Giveaway/Damage Buffer", "=B16 - E33"],# R29
                ["Pants Unit Cost", "=B31/2", "", "Price Floor (Zero Profit)", "=B33 + B32"], # R30
                ["Manufacturing Unit Cost", "=B26/B16", "", "Marketing Budget (to keep $1k Profit)", "=(B6-1000)"], # R31
                ["Shipping Label Cost per Order", v_label, "", "", ""],                     # R32
                ["Investment per Set (Avg)", "=B31", "", "Sets to Break Even", "=IF(E21>0, CEILING(B26/E21, 1), \"N/A\")"], # R33
                ["", "", "", "", ""],                                                       # R34

                ["SECTION J — Stress Testing", "", "", "SECTION K — Flash Sale Modeling", ""],# R35
                ["Projected Sell-Through %", v_sell_through, "", "Discount %", v_discount], # R36
                ["Sets Sold at this %", "=B16 * B36", "", "New Set Price", "=E15 * (1 - E36)"],# R37
                ["Projected Payout at this %", "=(B37 * E21) - B26", "", "New Pure Profit", "=E37 - B32"],# R38
                ["", "", "", "New Sets to Break Even", "=IF(E38 > 0, CEILING(B26 / E38, 1), \"N/A\")"],# R39
            ]
            
            sheet.clear()
            sheet.update("A1", data, value_input_option="USER_ENTERED")
            self._format_sheet(sheet)
            
            return {'success': True, 'message': '✅ Side-by-Side Dashboard Rebuilt!'}
            
        except Exception as e:
            self.logger.error(f"Error: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Error: {str(e)}'}



    def _format_sheet(self, sheet):
        requests = []
        
        # 1. Base Setup
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        # 2. Main Title (R1-R2)
        # Merge A1:E2
        requests.append({
            "mergeCells": {
                "range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 2, "startColumnIndex": 0, "endColumnIndex": 5},
                "mergeType": "MERGE_ALL"
            }
        })
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 2, "startColumnIndex": 0, "endColumnIndex": 5},
                "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 24, "bold": True}, "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE"}},
                "fields": "userEnteredFormat"
            }
        })
        
        # 3. Navy Headers (Bold White Text) #1C2833
        NAVY = {"red": 0.11, "green": 0.16, "blue": 0.20}
        WHITE = {"red": 1, "green": 1, "blue": 1}
        header_indices = [3, 11, 19, 27, 34] # Added R35
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

        # 4. Big Dashboard Metrics (R5-R9)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 4, "endRowIndex": 9, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 21, "bold": True}}}, "fields": "userEnteredFormat.textFormat"}})
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 4, "endRowIndex": 9, "startColumnIndex": 4, "endColumnIndex": 5}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 21, "bold": True}}}, "fields": "userEnteredFormat.textFormat"}})

        # General Font Size 21 for all values (Col B and E)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 11, "endRowIndex": 40, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 21}}}, "fields": "userEnteredFormat.textFormat"}})
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 11, "endRowIndex": 40, "startColumnIndex": 4, "endColumnIndex": 5}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 21}}}, "fields": "userEnteredFormat.textFormat"}})

        # Green Highlights for Goals
        BRIGHT_GREEN = {"red": 0.85, "green": 0.95, "blue": 0.85} # For Net Profit
        LIGHT_GREEN = {"red": 0.9, "green": 1.0, "blue": 0.9}   # For Buffer
        
        # Payout (Dashboard R6)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 5, "endRowIndex": 6, "startColumnIndex": 0, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": BRIGHT_GREEN}}, "fields": "userEnteredFormat.backgroundColor"}})
        
        # Buffer (Dashboard R8 and Section H R29)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 7, "endRowIndex": 8, "startColumnIndex": 0, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": LIGHT_GREEN}}, "fields": "userEnteredFormat.backgroundColor"}})
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 28, "endRowIndex": 29, "startColumnIndex": 3, "endColumnIndex": 5}, "cell": {"userEnteredFormat": {"backgroundColor": LIGHT_GREEN}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 5. Cell Colors (Inputs = Yellow, Calcs = Gray)
        YELLOW = {"red": 1.0, "green": 0.98, "blue": 0.85}
        GRAY = {"red": 0.94, "green": 0.94, "blue": 0.94}
        
        # Yellow Inputs
        input_ranges = [
            (12, 14, 1), # Section A Quantities
            (16, 16, 1), # Pieces per Set
            (20, 24, 1), # Section B Costs
            (31, 31, 1), # Shipping Label
            (35, 35, 1), # Section J Sell-Through %
            (12, 14, 4), # Section E Prices
            (35, 35, 4), # Section K Discount %
        ]
        for s, e, col in input_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": s, "endRowIndex": e+1, "startColumnIndex": col, "endColumnIndex": col+1}, "cell": {"userEnteredFormat": {"backgroundColor": YELLOW, "textFormat": {"bold": True}}}, "fields": "userEnteredFormat"}})

        # Gray Calculations
        calc_ranges = [
            (4, 8, 1), (4, 8, 4), # Dashboard
            (15, 15, 1), (17, 17, 1), # Section A Totals
            (25, 25, 1), # Total Investment
            (28, 30, 1), (32, 32, 1), # Section C Units & Avg Inv
            (36, 37, 1), # Section J Calcs
            (15, 15, 4), # Section E Revenue Per Set
            (20, 25, 4), # Section F Profit Breakdown
            (29, 30, 4), (32, 32, 4), # Section H Risk
            (36, 38, 4), # Section K Calcs
        ]
        for s, e, col in calc_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": s, "endRowIndex": e+1, "startColumnIndex": col, "endColumnIndex": col+1}, "cell": {"userEnteredFormat": {"backgroundColor": GRAY}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 6. Conditional Formatting: Red for Negative Marketing Budget (E31)
        RED_TEXT = {"red": 0.8, "green": 0, "blue": 0}
        LIGHT_RED_BG = {"red": 1.0, "green": 0.9, "blue": 0.9}
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {"sheetId": sheet.id, "startRowIndex": 8, "endRowIndex": 9, "startColumnIndex": 4, "endColumnIndex": 5},
                        {"sheetId": sheet.id, "startRowIndex": 30, "endRowIndex": 31, "startColumnIndex": 4, "endColumnIndex": 5}
                    ],
                    "booleanRule": {
                        "condition": {"type": "NUMBER_LESS", "values": [{"userEnteredValue": "0"}]},
                        "format": {"backgroundColor": LIGHT_RED_BG, "textFormat": {"foregroundColor": RED_TEXT, "bold": True}}
                    }
                },
                "index": 0
            }
        })

        # 7. Formats
        # Currency: Most columns
        for col in [1, 4]:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 4, "endRowIndex": 40, "startColumnIndex": col, "endColumnIndex": col+1}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # Section A SPECIFIC FIX: No $ (index 13-18, Col 1)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 12, "endRowIndex": 18, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "0"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # Percent: Margin R7, Net Margin R26, J Sell-Through R36, K Discount R36
        for rng in [(6, 4), (25, 4), (35, 1), (35, 4)]:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": rng[0], "endRowIndex": rng[0]+1, "startColumnIndex": rng[1], "endColumnIndex": rng[1]+1}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # Whole Number (Sets/Buffers/J-Sets/K-Sets)
        for rng in [(6, 1), (7, 1), (28, 4), (32, 4), (36, 1), (38, 4)]:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": rng[0], "endRowIndex": rng[0]+1, "startColumnIndex": rng[1], "endColumnIndex": rng[1]+1}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "0"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 7. Layout (Widths)
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 500}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 120}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3}, "properties": {"pixelSize": 50}, "fields": "pixelSize"}}) # Spacer 50px
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4}, "properties": {"pixelSize": 650}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 4, "endIndex": 5}, "properties": {"pixelSize": 120}, "fields": "pixelSize"}})

        sheet.spreadsheet.batch_update({"requests": requests})


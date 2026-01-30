"""
Drop 2 Finance Calculator (Antifragility + Risk Model)
- Total Investment Model: Focuses on sunk costs and payout.
- Risk & Scenarios: Giveaway buffers, price floor, and ad-spend limits.
- High Visibility: Navy headers + Bold White text.
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
        self.logger.info("=== SYNC DROP 2 FINANCE (ANTIFRAGILITY + RISK) ===")
        
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists(self.sheet_name)
            
            # 1. READ EXISTING VALUES (Persistence)
            existing_values = {}
            try:
                raw_data = sheet.get_all_values()
                if raw_data:
                    for row in raw_data:
                        if len(row) >= 2:
                            label = row[0].strip()
                            val = row[1].strip()
                            if label and val:
                                existing_values[label] = val
            except Exception as e:
                self.logger.warning(f"Persistence read failed: {e}")

            def get_val(label, default):
                saved = existing_values.get(label)
                if saved and not str(saved).startswith("="):
                    return saved
                return default

            # --- INPUT DEFAULTS (ANTIFRAGILITY) ---
            v_small = get_val("Small Sets", "14")
            v_med = get_val("Medium Sets", "20")
            v_large = get_val("Large Sets", "16")
            v_pps = get_val("Pieces per Set (input)", "2")
            
            v_sample = get_val("Sample Cost", "234.63")
            v_bulk = get_val("Bulk Order Cost", "1550.00")
            v_pack = get_val("Packaging & Supplies", "50.00")
            v_ship_me = get_val("Shipping to Me", "45.00")
            v_other = get_val("Other Costs", "0.00")
            
            v_label = get_val("Shipping Label Cost per Order", "6.44")
            
            v_p_hoodie = get_val("Hoodie Sell Price", "45.00")
            v_p_pants = get_val("Pants Sell Price", "35.00")
            v_p_set = get_val("Set Sell Price (Bundle)", "65.00")

            # --- DATA ARRAY ---
            data = [
                ["DROP 2 FINANCE PREDICTIONS (ANTIFRAGILITY)", ""],       # R1
                ["", ""],                                                 # R2
                ["KEY METRICS DASHBOARD", ""],                            # R3
                ["Total Potential Revenue", "=B48"],                      # R4
                ["Your Net Profit (The Payout)", "=B49"],                 # R5
                ["Sets to Break Even", "=B53"],                           # R6
                ["Giveaway/Damage Buffer", "=B57"],                       # R7 (Ref to Risk Sec)
                ["Pure Profit per set (post-BE)", "=B45"],                # R8
                ["Price Floor (Zero Profit)", "=B58"],                    # R9
                ["Ad-Spend Limit (Keep $1k Profit)", "=B59"],             # R10
                ["", ""],                                                 # R11
                
                ["SECTION A — Drop Quantities", ""],                      # R12
                ["Small Sets", v_small],                                  # R13
                ["Medium Sets", v_med],                                   # R14
                ["Large Sets", v_large],                                  # R15
                ["Total Sets", "=SUM(B13:B15)"],                          # R16
                ["Pieces per Set (input)", v_pps],                        # R17
                ["Total Pieces", "=B16*B17"],                             # R18
                ["", ""],                                                 # R19
                
                ["SECTION B — Total Investment (Sunk Cost)", ""],         # R20
                ["Sample Cost", v_sample],                                # R21
                ["Bulk Order Cost", v_bulk],                              # R22
                ["Packaging & Supplies", v_pack],                         # R23
                ["Shipping to Me", v_ship_me],                            # R24
                ["Other Costs", v_other],                                 # R25
                ["Total Investment Spent", "=SUM(B21:B25)"],              # R26
                ["", ""],                                                 # R27
                
                ["SECTION C — Logic Definitions", ""],                    # R28
                ["Note", "Production is pre-paid. Profit is revenue-based."], # R29
                ["Hoodie Cost (unit)", "Ignored in Sunk Cost Model"],     # R30
                ["Pants Cost (unit)", "Ignored in Sunk Cost Model"],      # R31
                ["Cost Per Set (Avg)", "=B26/B16"],                       # R32
                ["", ""],                                                 # R33
                
                ["SECTION D — Order Ops", ""],                            # R34
                ["Shipping Label Cost per Order", v_label],               # R35
                ["Variable Cost per Order", "=B35"],                      # R36
                ["", ""],                                                 # R37
                
                ["SECTION E — Pricing (EDIT THESE)", ""],                 # R38
                ["Hoodie Sell Price", v_p_hoodie],                        # R39
                ["Pants Sell Price", v_p_pants],                          # R40
                ["Set Sell Price (Bundle)", v_p_set],                     # R41
                ["Revenue Per Set", "=IF(B41>0, B41, B39+B40)"],          # R42
                ["", ""],                                                 # R43
                
                ["SECTION F — Profit & Cash Flow", ""],                   # R44
                ["Pure Profit per set (post-BE)", "=B42 - B36"],          # R45
                ["Hoodie Split Profit (post-BE)", "=IF((B39+B40)>0, (B42*(B39/(B39+B40)))-(B36/2), 0)"], # R46
                ["Pants Split Profit (post-BE)", "=IF((B39+B40)>0, (B42*(B40/(B39+B40)))-(B36/2), 0)"],  # R47
                ["Total Potential Revenue", "=B42*B16"],                  # R48
                ["Your Net Profit (The Payout)", "=B48 - B26"],           # R49
                ["Net Profit Margin %", "=IF(B48>0, B49/B48, 0)"],        # R50
                ["", ""],                                                 # R51
                
                ["SECTION G — Break-Even Analysis", ""],                  # R52
                ["Sets to Break Even", "=IF(B45>0, CEILING(B26/B45, 1), \"N/A\")"], # R53
                ["Total Potential Margin", "=IF(B48>0, B49/B48, 0)"],     # R54
                ["", ""],                                                 # R55
                
                ["SECTION H — Risk & Scenarios", ""],                     # R56
                ["Giveaway/Damage Buffer", "=B16 - B53"],                 # R57
                ["Price Floor (Zero Profit)", "=(B26 / B16) + B35"],      # R58
                ["Ad-Spend Limit (Keep $1k Profit)", "=B49 - 1000"],      # R59
            ]
            
            sheet.clear()
            sheet.update("A1", data, value_input_option="USER_ENTERED")
            self._format_sheet(sheet)
            
            return {'success': True, 'message': '✅ Risk Model & Navy Formatting Applied!'}
            
        except Exception as e:
            self.logger.error(f"Error: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Error: {str(e)}'}

    def _format_sheet(self, sheet):
        requests = []
        
        # 1. Base Setup
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        # 2. Main Title (R1)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 20, "bold": True}, "horizontalAlignment": "CENTER"}}, "fields": "userEnteredFormat"}})
        
        # 3. Navy Headers (Bold White Text)
        NAVY = {"red": 0.11, "green": 0.16, "blue": 0.20}
        WHITE = {"red": 1, "green": 1, "blue": 1}
        header_rows = [2, 11, 19, 27, 33, 37, 43, 51, 55] # Added Risk Header at 55
        for r in header_rows:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 2},
                    "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 14, "bold": True, "foregroundColor": WHITE}, "backgroundColor": NAVY}},
                    "fields": "userEnteredFormat"
                }
            })

        # 4. Big Metric Values (R4-R10)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 3, "endRowIndex": 10, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 15, "bold": True}}}, "fields": "userEnteredFormat.textFormat"}})

        # Green Highlight for Payout (R5)
        BRIGHT_GREEN = {"red": 0.85, "green": 0.95, "blue": 0.85}
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 4, "endRowIndex": 5, "startColumnIndex": 0, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": BRIGHT_GREEN}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 5. Formats
        # Currency: R4, R5, R8-R10, R21-R26, R32, R35, R36, R39-R42, R45-R49, R58, R59
        curr_indices = [(3, 4), (7, 9), (20, 25), (31, 31), (34, 35), (38, 41), (44, 48), (57, 58)]
        for s, e in curr_indices:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": s, "endRowIndex": e+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # Percent: R7, R50, R54
        pct_indices = [(6, 6), (49, 49), (53, 53)]
        for s, e in pct_indices:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": s, "endRowIndex": e+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # Whole Number: R6, R7, R53, R57
        for r in [5, 6, 52, 56]:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "0"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 6. Colors (Inputs = Yellow, Calcs = Gray)
        YELLOW = {"red": 1.0, "green": 0.98, "blue": 0.85}
        GRAY = {"red": 0.96, "green": 0.96, "blue": 0.96}
        
        input_rows = [(12, 14), (16, 16), (20, 24), (34, 34), (38, 40)]
        for s, e in input_rows:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": s, "endRowIndex": e+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": YELLOW, "textFormat": {"bold": True}}}, "fields": "userEnteredFormat"}})
        
        calc_rows = [(3, 3), (5, 9), (15, 15), (17, 17), (25, 25), (29, 32), (35, 36), (41, 50), (52, 53), (56, 58)]
        for s, e in calc_rows:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": s, "endRowIndex": e+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": GRAY}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 7. Layout
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 300}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 180}, "fields": "pixelSize"}})

        sheet.spreadsheet.batch_update({"requests": requests})

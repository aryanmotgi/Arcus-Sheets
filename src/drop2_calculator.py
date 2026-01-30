"""
Drop 2 Finance Calculator (Dynamic Persistence Version)
- Fully editable: Change any yellow cell and everything updates.
- Safety: Prevents #DIV/0! errors if prices are set to zero.
- Logic: High-fidelity ratio-based profit splitting.
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
        self.logger.info("=== SYNC DROP 2 FINANCE (DYNAMIC EDITABLE VERSION) ===")
        
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

            # --- DATA ARRAY ---
            data = [
                ["DROP 2 FINANCE PREDICTIONS", ""],                       # R1
                ["", ""],                                                 # R2
                ["KEY METRICS DASHBOARD", ""],                            # R3
                ["Revenue Per Set", "=B42"],                              # R4 
                ["Profit Per Set", "=B45"],                               # R5 
                ["Profit Margin %", "=B50"],                              # R6 
                ["Hoodie Profit (unit)", "=B46"],                         # R7 
                ["Pants Profit (unit)", "=B47"],                          # R8 
                ["Sets to Break Even", "=B53"],                           # R9 
                ["Total Potential Profit", "=B49"],                       # R10
                ["", ""],                                                 # R11
                
                ["SECTION A — Drop Quantities", ""],                      # R12
                ["Small Sets", get_val("Small Sets", "15")],               # R13
                ["Medium Sets", get_val("Medium Sets", "25")],             # R14
                ["Large Sets", get_val("Large Sets", "20")],               # R15
                ["Total Sets", "=SUM(B13:B15)"],                          # R16
                ["Pieces per Set (input)", get_val("Pieces per Set (input)", "2")], # R17
                ["Total Pieces", "=B16*B17"],                             # R18
                ["", ""],                                                 # R19
                
                ["SECTION B — Total Costs", ""],                          # R20
                ["Sample Cost", get_val("Sample Cost", "150.00")],         # R21
                ["Bulk Order Cost", get_val("Bulk Order Cost", "1200.00")], # R22
                ["Packaging & Supplies", get_val("Packaging & Supplies", "50.00")], # R23
                ["Shipping to Me", get_val("Shipping to Me", "45.00")],    # R24
                ["Other Costs", get_val("Other Costs", "0.00")],           # R25
                ["Total Drop Cost", "=SUM(B21:B25)"],                     # R26
                ["", ""],                                                 # R27
                
                ["SECTION C — Unit Cost Breakdown", ""],                  # R28
                ["Hoodie Cost (per unit)", get_val("Hoodie Cost (per unit)", "12.00")], # R29
                ["Pants Cost (per unit)", get_val("Pants Cost (per unit)", "10.00")],   # R30
                ["Cost Per Set (Calculated)", "=B29+B30"],                # R31
                ["Cost Per Piece (Avg)", "=IF(B18>0, B26/B18, 0)"],       # R32
                ["", ""],                                                 # R33
                
                ["SECTION D — Shipping Labels", ""],                      # R34
                ["Shipping Label Cost per Order", get_val("Shipping Label Cost per Order", "6.50")], # R35
                ["Shipping Cost Per Set", "=B35"],                        # R36
                ["", ""],                                                 # R37
                
                ["SECTION E — Pricing (EDIT THESE)", ""],                 # R38
                ["Hoodie Sell Price", get_val("Hoodie Sell Price", "45.00")], # R39
                ["Pants Sell Price", get_val("Pants Sell Price", "35.00")],   # R40
                ["Set Sell Price (Bundle)", get_val("Set Sell Price (Bundle)", "75.00")], # R41
                ["Revenue Per Set", "=IF(B41>0, B41, B39+B40)"],          # R42
                ["", ""],                                                 # R43
                
                ["SECTION F — Profit Breakdown", ""],                     # R44
                ["Profit Per Set", "=B42 - B31 - B36"],                   # R45
                ["Hoodie Profit (unit)", "=IF((B39+B40)>0, (B42*(B39/(B39+B40)))-B29-(B36/2), 0)"], # R46
                ["Pants Profit (unit)", "=IF((B39+B40)>0, (B42*(B40/(B39+B40)))-B30-(B36/2), 0)"],  # R47
                ["Total Potential Revenue", "=B42*B16"],                  # R48
                ["Total Potential Profit", "=B45*B16"],                   # R49
                ["Profit Margin %", "=IF(B42>0, B45/B42, 0)"],            # R50
                ["", ""],                                                 # R51
                
                ["SECTION G — Break-Even Analysis", ""],                  # R52
                ["Sets to Break Even", "=IF(B45>0, CEILING(B26/B45, 1), \"N/A\")"], # R53
                ["", ""],                                                 # R54
            ]
            
            sheet.clear()
            sheet.update("A1", data, value_input_option="USER_ENTERED")
            self._format_sheet(sheet)
            
            return {'success': True, 'message': '✅ Drop 2 Finance Rebuilt & Fully Dynamic!'}
            
        except Exception as e:
            self.logger.error(f"Error: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Error: {str(e)}'}

    def _format_sheet(self, sheet):
        requests = []
        
        # 1. Base Setup
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        # 2. Main Title (R1)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 20, "bold": True}, "horizontalAlignment": "CENTER"}}, "fields": "userEnteredFormat"}})
        
        # 3. Navy Headers
        NAVY = {"red": 0.11, "green": 0.16, "blue": 0.20}
        WHITE = {"red": 1, "green": 1, "blue": 1}
        header_rows = [2, 11, 19, 27, 33, 37, 43, 51]
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

        # 5. Currency & Percent Formats
        curr_ranges = [(3, 4), (6, 7), (9, 9), (20, 25), (28, 31), (34, 35), (38, 41), (44, 48)] 
        for start_r, end_r in curr_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})
        
        # Percent R6, R50
        pct_ranges = [(5, 5), (49, 49)]
        for r_start, r_end in pct_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": r_start, "endRowIndex": r_end+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # Whole Number (BE Sets R9, R53)
        for r in [8, 52]:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "0"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 6. Colors (Inputs = Yellow, Calcs = Gray)
        YELLOW = {"red": 1.0, "green": 0.98, "blue": 0.9}
        GRAY = {"red": 0.96, "green": 0.96, "blue": 0.96}
        input_rows = [(12, 14), (16, 16), (20, 24), (28, 29), (34, 34), (38, 40)]
        for s, e in input_rows:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": s, "endRowIndex": e+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": YELLOW, "textFormat": {"bold": True}}}, "fields": "userEnteredFormat"}})
        
        calc_rows = [(3, 9), (15, 15), (17, 17), (25, 25), (30, 31), (35, 35), (41, 41), (44, 49), (52, 52)]
        for s, e in calc_rows:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": s, "endRowIndex": e+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": GRAY}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 7. Borders & Widths
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 300}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 180}, "fields": "pixelSize"}})

        sheet.spreadsheet.batch_update({"requests": requests})

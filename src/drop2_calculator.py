"""
Drop 2 Finance Calculator (Manual Prediction Sheet)

Refined Logic:
- Total Profit = Potential Revenue - Total Drop Cost
- Sets to Break Even = (Total Drop Cost / Set Price) + Free Sets
- Robust Persistence: Preserves "0" and manual overrides.
- New Section: Free & Discounted Units.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Drop2Calculator:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.logger = logger
        self.sheet_name = "Drop 2 Finance Predictions"

    def create_prediction_sheet(self) -> Dict[str, Any]:
        """Creates or updates the Drop 2 Finance Predictions sheet with fixed logic"""
        self.logger.info("=== REFINING DROP 2 FINANCE (LOGIC + FREE UNITS) ===")
        
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
                            if label:
                                existing_values[label] = val
            except Exception as e:
                self.logger.warning(f"Could not read existing values: {e}")

            # Robust get_val: Use existing if present, else default
            def get_val(label, default):
                if label in existing_values:
                    saved = existing_values[label]
                    # Don't persist formulas if the script wants to update the formula
                    if not str(default).startswith("="):
                        return saved
                return default

            # --- INPUTS (PERSISTED) ---
            v_small = get_val("Small Sets", "14")
            v_med = get_val("Medium Sets", "20")
            v_large = get_val("Large Sets", "16")
            v_pps = get_val("Pieces per Set (input)", "2")
            
            v_sample = get_val("Sample Cost", "150.00")
            v_bulk = get_val("Bulk Order Cost", "1200.00")
            v_pack = get_val("Packaging & Supplies", "0.00") # Default to 0 as user requested
            v_ship_me = get_val("Shipping to Me", "0.00")    # Default to 0 as user requested
            v_other = get_val("Other Costs", "0.00")
            
            v_c_hoodie = get_val("Hoodie Cost (per unit)", "12.00")
            v_c_pants = get_val("Pants Cost (per unit)", "10.00")
            
            v_label = get_val("Shipping Label Cost per Order", "6.44")
            
            v_p_hoodie = get_val("Hoodie Sell Price", "45.00")
            v_p_pants = get_val("Pants Sell Price", "35.00")
            v_p_set = get_val("Set Sell Price", "80.00")
            
            # NEW INPUTS: Free & Discounted
            v_free = get_val("Free Sets Given Away", "3")
            v_disc_count = get_val("Discounted Sets Count", "0")
            v_disc_price = get_val("Discounted Set Price", "40.00")

            data = [
                ["DROP 2 FINANCE PREDICTIONS", ""],                       # 1 Title
                ["", ""],                                                 # 2 Spacer
                
                # === KEY METRICS DASHBOARD (Rows 3-10) ===
                ["KEY METRICS DASHBOARD", ""],                            # 3 Header
                ["Revenue Per Set", "=B45"],                              # 4
                ["Total Potential Profit", "=B54"],                       # 5
                ["Profit Margin %", "=B55"],                              # 6
                ["Sets to Break Even", "=B58"],                           # 7
                ["Hoodie Profit (unit)", "=B51"],                         # 8
                ["Pants Profit (unit)", "=B52"],                          # 9
                ["", ""],                                                 # 10 Spacer
                
                # SECTION A: Quantities
                ["SECTION A — Drop Quantities", ""],                      # 11
                ["Small Sets", v_small],                                  # 12
                ["Medium Sets", v_med],                                   # 13
                ["Large Sets", v_large],                                  # 14
                ["Total Sets", "=SUM(B12:B14)"],                          # 15
                ["Pieces per Set (input)", v_pps],                        # 16
                ["Total Pieces", "=B15*B16"],                             # 17
                ["", ""],                                                 # 18
            ]
            
            # SECTION B: Total Costs (THE INVESTMENT)
            data.extend([
                ["SECTION B — Total Costs", ""],                          # 19
                ["Sample Cost", v_sample],                                # 20
                ["Bulk Order Cost", v_bulk],                              # 21
                ["Packaging & Supplies", v_pack],                         # 22
                ["Shipping to Me", v_ship_me],                            # 23
                ["Other Costs", v_other],                                 # 24
                ["Total Drop Cost (Investment)", "=SUM(B20:B24)"],        # 25
                ["", ""],                                                 # 26
            ])
            
            # SECTION C: Unit Cost Breakdown
            data.extend([
                ["SECTION C — Unit Cost Breakdown", ""],                  # 27
                ["Hoodie Cost (per unit)", v_c_hoodie],                   # 28
                ["Pants Cost (per unit)", v_c_pants],                     # 29
                ["Cost Per Set (Manuf.)", "=B28+B29"],                    # 30
                ["Cost Per Piece (Avg)", "=IF(B17>0, B25/B17, 0)"],       # 31
                ["", ""],                                                 # 32
            ])
            
            # SECTION D: Shipping
            data.extend([
                ["SECTION D — Shipping Label Cost", ""],                  # 33
                ["Shipping Label Cost per Order", v_label],               # 34
                ["Shipping Cost Per Set", "=B34"],                        # 35
                ["", ""],                                                 # 36
            ])

            # SECTION E: Free & Discounted Units (NEW)
            data.extend([
                ["SECTION E — Free & Discounted Units", ""],              # 37
                ["Free Sets Given Away", v_free],                         # 38
                ["Discounted Sets Count", v_disc_count],                  # 39
                ["Discounted Set Price", v_disc_price],                   # 40
                ["", ""],                                                 # 41
            ])
            
            # SECTION F: Pricing Inputs
            data.extend([
                ["SECTION F — Pricing Inputs", ""],                       # 42
                ["Hoodie Sell Price", v_p_hoodie],                        # 43
                ["Pants Sell Price", v_p_pants],                          # 44
                ["Set Sell Price", v_p_set],                              # 45
                ["Effective Revenue Per Set", "=IF(B45>0, B45, B43+B44)"],# 46
                ["", ""],                                                 # 47
            ])
            
            # SECTION G: Profit Breakdown
            # Potential Revenue = (TotalSets - Free - Disc)*Price + (Disc * DiscPrice)
            data.extend([
                ["SECTION G — Profit Breakdown", ""],                     # 48
                ["Total Potential Revenue", "=((B15-B38-B39)*B46) + (B39*B40)"], # 49
                
                # Split Profits using Revenue Ratio
                ["Hoodie Profit (unit)", "=IF((B43+B44)>0, (B46 * (B43/(B43+B44))) - B28 - (B35/2), 0)"], # 50
                ["Pants Profit (unit)", "=IF((B43+B44)>0, (B46 * (B44/(B43+B44))) - B29 - (B35/2), 0)"],  # 51
                
                ["Profit Per Set (Unit Avg)", "=B46 - B30 - B35"],        # 52 (For reference)
                ["Total Potential Profit", "=B49 - B25"],                 # 53 (Rev - Investment)
                ["Overall Profit Margin %", "=IF(B49>0, B53/B49, 0)"],    # 54
                ["", ""],                                                 # 55
            ])
            
            # SECTION H: Break-Even Analysis
            # Sets to Break Even = (Total Drop Cost / Set Price) + Free Sets
            data.extend([
                ["SECTION H — Break-Even Analysis", ""],                  # 56
                ["Sets to Break Even", "=ROUNDUP(IF(B46>0, B25/B46, 0), 0) + B38"], # 57
                ["Remaining Sets for Profit", "=B15 - B57"],              # 58
                ["", ""],                                                 # 59 Spacer
            ])

            # Clear & Update
            sheet.clear()
            sheet.update("A1", data, value_input_option="USER_ENTERED")
            
            # FORMATTING
            self._format_sheet(sheet)
            
            return {
                'success': True,
                'message': '✅ **Logic Fixes Applied!**\n'
                          'Break-even and Profit formulas are now correct. User inputs preserved.'
            }
            
        except Exception as e:
            self.logger.error(f"Error updating Drop 2 sheet: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed: {str(e)}'}

    def _format_sheet(self, sheet):
        requests = []
        
        # 1. Clean Slate
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        # 2. Main Title (20pt)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 20, "bold": True}, "horizontalAlignment": "CENTER"}}, "fields": "userEnteredFormat"}})
        
        # 3. Section Headers (Navy + White)
        # Rows: 3, 11, 19, 27, 33, 37, 42, 48, 56 (Indices)
        NAVY = {"red": 0.11, "green": 0.16, "blue": 0.20}
        WHITE = {"red": 1, "green": 1, "blue": 1}
        sections = [2, 10, 18, 26, 32, 36, 41, 47, 55]
        for r in sections:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 14, "bold": True, "foregroundColor": WHITE}, "backgroundColor": NAVY}}, "fields": "userEnteredFormat"}})

        # 4. Yellow Inputs
        YELLOW = {"red": 1.0, "green": 0.98, "blue": 0.9}
        input_indices = [
            (11, 13), (15, 15), # A
            (19, 23),           # B
            (27, 28),           # C
            (33, 33),           # D
            (37, 39),           # E
            (42, 44)            # F
        ]
        for start_r, end_r in input_indices:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": YELLOW, "textFormat": {"bold": True}}}, "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat"}})

        # 5. Gray Calculations
        GRAY = {"red": 0.96, "green": 0.96, "blue": 0.96}
        calc_indices = [
            (3, 8), (14, 14), (16, 16), (24, 24), (29, 30), (34, 34), (45, 45), (48, 53), (56, 57)
        ]
        for start_r, end_r in calc_indices:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": GRAY}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 6. Currency & Percent
        curr_pattern = "$#,##0.00"
        curr_ranges = [
            (3, 4), (6, 8), # Dashboard
            (19, 24), (27, 30), (33, 34), (39, 39), (42, 45), (48, 52) # Detailed
        ]
        for start_r, end_r in curr_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": curr_pattern}}}, "fields": "userEnteredFormat.numberFormat"}})
        
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 5, "endRowIndex": 6, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 7. Column Widths
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 300}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 180}, "fields": "pixelSize"}})

        sheet.spreadsheet.batch_update({"requests": requests})

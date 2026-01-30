"""
Drop 2 Finance Calculator (Manual Prediction Sheet)

Creates a standalone "Drop 2 Finance Predictions" sheet.
Key Features:
- KEY METRICS DASHBOARD (Top)
- Navy Blue Styling + White Text Headers
- Proportional Revenue/Profit Allocation logic
- Strict Persistence of manual inputs
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
        """Creates or updates the Drop 2 Finance Predictions sheet"""
        self.logger.info("=== INIT DROP 2 FINANCE PREDICTIONS (DASHBOARD) ===")
        
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
                self.logger.warning(f"Could not read existing values: {e}")

            # Helper to get value: defaults to 'default' unless existing found
            # ONLY persist if it's not a formula (starts with =)
            def get_val(label, default):
                saved = existing_values.get(label)
                if saved and not str(default).startswith("="):
                    return saved
                return default

            # --- INPUTS (PERSISTED) ---
            # Section A
            v_small = get_val("Small Sets", "14")
            v_med = get_val("Medium Sets", "20")
            v_large = get_val("Large Sets", "16")
            v_pps = get_val("Pieces per Set (input)", "2") # Added tag
            
            # Section B
            v_sample = get_val("Sample Cost", "150.00")
            v_bulk = get_val("Bulk Order Cost", "1200.00")
            v_pack = get_val("Packaging & Supplies", "50.00")
            v_ship_me = get_val("Shipping to Me", "45.00")
            v_other = get_val("Other Costs", "0.00")
            
            # Section C
            v_c_hoodie = get_val("Hoodie Cost (per unit)", "12.00")
            v_c_pants = get_val("Pants Cost (per unit)", "10.00")
            
            # Section D
            v_label = get_val("Shipping Label Cost per Order", "6.44")
            
            # Section E
            v_p_hoodie = get_val("Hoodie Sell Price", "45.00")
            v_p_pants = get_val("Pants Sell Price", "35.00")
            v_p_set = get_val("Set Sell Price", "80.00")
            
            # --- DATA STRUCTURE ---
            # Rows 1-2: Title
            # Rows 3-10: DASHBOARD (Cards)
            # Rows 12+: Details
            
            # Helper for Dashboard Formulas
            # RevPerSet = E38 (approx, need to track cell refs carefully)
            # ProfPerSet = E44
            # BreakEvenSets = E53
            
            # We construct data list linearly.
            # Grid Layout: Col A (Label), Col B (Value)
            # Wait, Dashboard needs to be big cards. 
            # Let's map Dashboard to A3:B6 and A7:B10? Or maybe Columns A-B-C-D?
            # User wants "Layout clean". 2 Columns is safest for mobile/simple view.
            # Let's use clean "Key Metric" rows at top with big font.
            
            data = [
                ["DROP 2 FINANCE PREDICTIONS", ""],                       # 1 Title
                ["", ""],                                                 # 2 Spacer
            ]
            
            # === DASHBOARD (Row 3 start) ===
            # Key Metrics Block
            data.extend([
                ["KEY METRICS DASHBOARD", ""],                            # 3 Header
                
                ["Revenue Per Set", "=B42"],                              # 4
                ["Profit Per Set", "=B45"],                               # 5
                ["Profit Margin %", "=B50"],                              # 6
                ["Hoodie Profit (unit)", "=B46"],                         # 7
                ["Pants Profit (unit)", "=B47"],                          # 8
                
                ["Sets to Break Even", "=B53"],                           # 9
                ["Total Potential Profit", "=B49"],                       # 10
                ["", ""],                                                 # 11 Spacer
            ])
            
            # === DETAILED SECTIONS ===
            
            # SECTION A: Quantities
            data.extend([
                ["SECTION A — Drop Quantities", ""],                      # 12
                ["Small Sets", v_small],                                  # 13
                ["Medium Sets", v_med],                                   # 14
                ["Large Sets", v_large],                                  # 15
                ["Total Sets", "=SUM(B13:B15)"],                          # 16
                ["Pieces per Set (input)", v_pps],                        # 17
                ["Total Pieces", "=B16*B17"],                             # 18
                ["", ""],                                                 # 19
            ])
            
            # SECTION B: Total Costs
            data.extend([
                ["SECTION B — Total Costs", ""],                          # 20
                ["Sample Cost", v_sample],                                # 21
                ["Bulk Order Cost", v_bulk],                              # 22
                ["Packaging & Supplies", v_pack],                         # 23
                ["Shipping to Me", v_ship_me],                            # 24
                ["Other Costs", v_other],                                 # 25
                ["Total Drop Cost", "=SUM(B21:B25)"],                     # 26
                ["", ""],                                                 # 27
            ])
            
            # SECTION C: Unit Cost Breakdown
            data.extend([
                ["SECTION C — Unit Cost Breakdown", ""],                  # 28
                ["Hoodie Cost (per unit)", v_c_hoodie],                   # 29
                ["Pants Cost (per unit)", v_c_pants],                     # 30
                ["Cost Per Set (Calculated)", "=B29+B30"],                # 31
                ["Cost Per Piece (Avg)", "=IF(B18>0, B26/B18, 0)"],       # 32
                ["", ""],                                                 # 33
            ])
            
            # SECTION D: Shipping
            data.extend([
                ["SECTION D — Shipping Label Cost", ""],                  # 34
                ["Shipping Label Cost per Order", v_label],               # 35
                ["Shipping Cost Per Set", "=B35"],                        # 36
                ["", ""],                                                 # 37
            ])
            
            # SECTION E: Pricing
            # Logic: If Set Price is blank/0, use Sum.
            data.extend([
                ["SECTION E — Pricing Inputs", ""],                       # 38
                ["Hoodie Sell Price", v_p_hoodie],                        # 39
                ["Pants Sell Price", v_p_pants],                          # 40
                ["Set Sell Price", v_p_set],                              # 41
                ["Revenue Per Set", "=IF(B41>0, B41, B39+B40)"],          # 42
                ["", ""],                                                 # 43
            ])
            
            # SECTION F: Profit Breakdown
            # Logic: 
            # Profit Set = RevenueSet - CostSet - ShipSet
            # Hoodie Alloc Ratio = HoodiePrice / (HoodiePrice + PantsPrice)
            # Hoodie Alloc Rev = RevenueSet * Ratio
            # Hoodie Profit = AllocRev - HoodieCost - (Ship/2)
            data.extend([
                ["SECTION F — Profit Breakdown", ""],                     # 44
                ["Profit Per Set", "=B42 - B31 - B36"],                   # 45
                
                # Split Logic
                ["Hoodie Profit (per unit)", "=(B42 * (B39/(B39+B40))) - B29 - (B36/2)"], # 46
                ["Pants Profit (per unit)", "=(B42 * (B40/(B39+B40))) - B30 - (B36/2)"],  # 47
                
                ["Total Potential Revenue", "=B42*B16"],                  # 48
                ["Total Potential Profit", "=B45*B16"],                   # 49
                ["Profit Margin %", "=IF(B42>0, B45/B42, 0)"],            # 50
                ["", ""],                                                 # 51
            ])
            
            # SECTION G: Break-Even
            data.extend([
                ["SECTION G — Break-Even Analysis", ""],                  # 52
                ["Sets to Break Even", "=IF(B45>0, CEILING(B26/B45, 1), \"N/A\")"], # 53
                ["", ""],                                                 # 54
            ])
            
            # Clear & Update
            sheet.clear()
            sheet.update("A1", data, value_input_option="USER_ENTERED")
            
            # FORMATTING
            self._format_sheet(sheet)
            
            return {
                'success': True,
                'message': '✅ **Dashboard Updated!**\n'
                          'New visuals, improved logic, and persistence applied.'
            }
            
        except Exception as e:
            self.logger.error(f"Error creating Drop 2 sheet: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed: {str(e)}'}

    def _format_sheet(self, sheet):
        requests = []
        
        # 1. Clean Slate (White BG, No Grid)
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        # 2. Main Title (Row 1) - Big 20pt
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 2},
                "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 20, "bold": True}, "horizontalAlignment": "CENTER", "backgroundColor": {"red": 1, "green": 1, "blue": 1}}},
                "fields": "userEnteredFormat"
            }
        })
        
        # 3. Section Headers (Navy Blue + White Text)
        # Rows: 3, 12, 20, 28, 34, 38, 44, 52 (Indices: 2, 11, 19, 27, 33, 37, 43, 51)
        NAVY = {"red": 0.11, "green": 0.16, "blue": 0.20} # #1C2833
        WHITE = {"red": 1, "green": 1, "blue": 1}
        
        sections = [2, 11, 19, 27, 33, 37, 43, 51]
        for r in sections:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 2},
                    "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 14, "bold": True, "foregroundColor": WHITE}, "backgroundColor": NAVY, "padding": {"top": 5, "bottom": 5, "left": 5}}},
                    "fields": "userEnteredFormat"
                }
            })

        # 4. Dashboard Cards (Rows 4-10) -> Big Font
        dashboard_indices = list(range(3, 10)) # 3 to 9 (Rows 4-10)
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 3, "endRowIndex": 10, "startColumnIndex": 1, "endColumnIndex": 2},
                "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 14, "bold": True}, "horizontalAlignment": "LEFT"}},
                "fields": "userEnteredFormat.textFormat"
            }
        })

        # 5. Conditional Formatting for Profit/Margins
        # Dashboard Profit Rows: 5, 7, 8, 10 (Indices 4, 6, 7, 9)
        # Detail Profit Rows: 45, 46, 47, 49 (Indices 44, 45, 46, 48)
        profit_ranges = [
            {"sheetId": sheet.id, "startRowIndex": 4, "endRowIndex": 5, "startColumnIndex": 1, "endColumnIndex": 2},
            {"sheetId": sheet.id, "startRowIndex": 6, "endRowIndex": 8, "startColumnIndex": 1, "endColumnIndex": 2},
            {"sheetId": sheet.id, "startRowIndex": 9, "endRowIndex": 10, "startColumnIndex": 1, "endColumnIndex": 2},
            {"sheetId": sheet.id, "startRowIndex": 44, "endRowIndex": 47, "startColumnIndex": 1, "endColumnIndex": 2},
            {"sheetId": sheet.id, "startRowIndex": 48, "endRowIndex": 49, "startColumnIndex": 1, "endColumnIndex": 2},
        ]
        # Green > 0, Red < 0
        GREEN_TEXT = {"foregroundColor": {"red": 0.1, "green": 0.6, "blue": 0.1}, "bold": True}
        RED_TEXT = {"foregroundColor": {"red": 0.8, "green": 0.1, "blue": 0.1}, "bold": True}
        
        for rng in profit_ranges:
            requests.append({"addConditionalFormatRule": {"rule": {"ranges": [rng], "booleanRule": {"condition": {"type": "NUMBER_GREATER", "values": [{"userEnteredValue": "0"}]}, "format": {"textFormat": GREEN_TEXT}}}, "index": 0}})
            requests.append({"addConditionalFormatRule": {"rule": {"ranges": [rng], "booleanRule": {"condition": {"type": "NUMBER_LESS", "values": [{"userEnteredValue": "0"}]}, "format": {"textFormat": RED_TEXT}}}, "index": 1}})

        # 6. Currency Format ($)
        curr_ranges = [
            (3, 4), (6, 7), (9, 9), # Dashboard
            (21, 26), (29, 31), (35, 36), (39, 42), (45, 49) # Details
        ]
        for start_r, end_r in curr_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})
        
        # 7. Percentage Format
        # Row 6 (Index 5), Row 50 (Index 49)
        pct_ranges = [(5, 6), (49, 50)]
        for start_r, end_r in pct_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 7b. Break-Even Format (Number, 0 decimals)
        # Dashboard Index 8 (Row 9), Section G Index 52 (Row 53)
        be_ranges = [(8, 9), (52, 53)]
        for start_r, end_r in be_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "0"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 8. Colors: Yellow for Inputs
        YELLOW = {"red": 1.0, "green": 0.98, "blue": 0.9} # Light yellow
        input_indices = [
            (13, 15), (17, 17), # A
            (21, 25),           # B
            (29, 30),           # C
            (35, 35),           # D
            (39, 41)            # E
        ]
        for start_r, end_r in input_indices:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": YELLOW, "textFormat": {"bold": True}}}, "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat"}})

        # Calculated Cells (Gray)
        GRAY = {"red": 0.96, "green": 0.96, "blue": 0.96}
        calc_indices = [
            (16, 16), (18, 18), (26, 26), (31, 32), (36, 36), (42, 42), (45, 50), (53, 53)
        ]
        for start_r, end_r in calc_indices:
            requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": GRAY}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 9. Column Widths
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 300}, "fields": "pixelSize"}}) 
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 180}, "fields": "pixelSize"}})

        sheet.spreadsheet.batch_update({"requests": requests})

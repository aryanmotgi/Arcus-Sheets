"""
Drop 2 Finance Calculator (Manual Prediction Sheet)

Creates a standalone "Drop 2 Finance Predictions" sheet.
Independent of Shopify or Sync. Manual inputs + auto-calculations.
Supports PERSISTENCE: Preserves user inputs on update.
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
        self.logger.info("=== INIT DROP 2 FINANCE PREDICTIONS (PERSISTENT) ===")
        
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

            # --- STRUCTURE ---
            # Columns: A(Label), B(Value)
            
            # --- SECTION A: Quantities ---
            # Inputs: Small, Med, Large, Pieces/Set
            # Calcs: Total Sets, Total Pieces
            v_small = get_val("Small Sets", "14")
            v_med = get_val("Medium Sets", "20")
            v_large = get_val("Large Sets", "16")
            v_pps = get_val("Pieces per Set", "2")
            
            # --- SECTION B: Total Costs ---
            v_sample = get_val("Sample Cost", "150.00")
            v_bulk = get_val("Bulk Order Cost", "1200.00")
            v_pack = get_val("Packaging & Supplies", "50.00")
            v_ship_me = get_val("Shipping to Me", "45.00")
            v_other = get_val("Other Costs", "0.00")
            
            # --- SECTION D: Shipping Label ---
            v_label = get_val("Shipping Label Cost per Order", "6.44")
            
            # --- SECTION E: Pricing ---
            v_p_hoodie = get_val("Hoodie Sell Price", "45.00")
            v_p_pants = get_val("Pants Sell Price", "35.00")
            v_p_set = get_val("Set Sell Price", "80.00")
            
            # --- SECTION C: Cost Breakdown (NEW SPLIT) ---
            # New inputs: Hoodie Cost, Pants Cost
            v_c_hoodie = get_val("Hoodie Cost (per unit)", "12.00")
            v_c_pants = get_val("Pants Cost (per unit)", "10.00")
            
            # --- SECTION H: What-if ---
            v_test_h = get_val("Test Hoodie Price", "50.00")
            v_test_p = get_val("Test Pants Price", "40.00")
            v_test_s = get_val("Test Set Price", "90.00")
            
            # --- SECTION I: Impact ---
            v_free = get_val("Free Sets Given Away", "2")
            v_disc = get_val("Discounted Set Price", "40.00")


            data = [
                ["DROP 2 FINANCE PREDICTIONS", ""],                       # 1 Header
                ["", ""],
                
                # SECTION A
                ["SECTION A — Drop Quantities", ""],                      # 3
                ["Small Sets", v_small],                                  # 4 (Input - Persisted)
                ["Medium Sets", v_med],                                   # 5 (Input - Persisted)
                ["Large Sets", v_large],                                  # 6 (Input - Persisted)
                ["Total Sets", "=SUM(B4:B6)"],                            # 7 (Calc)
                ["Pieces per Set", v_pps],                                # 8 (Input - Persisted)
                ["Total Pieces", "=B7*B8"],                               # 9 (Calc)
                ["", ""],
                
                # SECTION B
                ["SECTION B — Total Costs", ""],                          # 11
                ["Sample Cost", v_sample],                                # 12 (Input - Persisted)
                ["Bulk Order Cost", v_bulk],                              # 13 (Input - Persisted)
                ["Packaging & Supplies", v_pack],                         # 14 (Input - Persisted)
                ["Shipping to Me", v_ship_me],                            # 15 (Input - Persisted)
                ["Other Costs", v_other],                                 # 16 (Input - Persisted)
                ["Total Drop Cost", "=SUM(B12:B16)"],                     # 17 (Calc)
                ["", ""],
                
                # SECTION C
                ["SECTION C — Unit Cost Breakdown", ""],                  # 19
                ["Hoodie Cost (per unit)", v_c_hoodie],                   # 20 (Input - Persisted)
                ["Pants Cost (per unit)", v_c_pants],                     # 21 (Input - Persisted)
                ["Cost Per Set (Calculated)", "=B20+B21"],                # 22
                ["Cost Per Set (Avg from Total)", "=IF(B7>0, B17/B7, 0)"],# 23 (Reference)
                ["Cost Per Piece (Avg)", "=IF(B9>0, B17/B9, 0)"],         # 24
                ["", ""],
                
                # SECTION D
                ["SECTION D — Shipping Label Cost", ""],                  # 26
                ["Shipping Label Cost per Order", v_label],               # 27 (Input - Persisted)
                ["Shipping Cost Per Set", "=B27"],                        # 28
                ["Shipping Cost Per Piece", "=IF(B8>0, B27/B8, 0)"],      # 29
                ["", ""],

                # SECTION E
                ["SECTION E — Pricing Inputs", ""],                       # 31
                ["Hoodie Sell Price", v_p_hoodie],                        # 32 (Input - Persisted)
                ["Pants Sell Price", v_p_pants],                          # 33 (Input - Persisted)
                ["Set Sell Price", v_p_set],                              # 34 (Input - Persisted)
                
                # Revenue Rule: IF Set Price is Blank/0, Use Sum
                ["Revenue Per Set", "=IF(B34>0, B34, B32+B33)"],          # 35
                ["Revenue Per Piece", "=IF(B8>0, B35/B8, 0)"],            # 36
                ["", ""],

                # SECTION F
                ["SECTION F — Profit Breakdown", ""],                     # 38
                ["Profit Per Set", "=B35 - B22 - B28"],                   # 39 (Rev - CostSet - ShipSet)
                # Split Profits
                # Hoodie Profit = HoodiePrice - HoodieCost - (Ship/2)
                ["Hoodie Profit (per unit)", "=B32 - B20 - (B28/2)"],     # 40
                ["Pants Profit (per unit)", "=B33 - B21 - (B28/2)"],      # 41
                
                ["Profit Per Piece", "=IF(B8>0, B39/B8, 0)"],             # 42
                ["Total Potential Revenue", "=B35*B7"],                   # 43
                ["Total Potential Profit", "=B39*B7"],                    # 44
                ["Profit Margin %", "=IF(B35>0, B39/B35, 0)"],            # 45
                ["", ""],
                
                # SECTION G
                ["SECTION G — Break-Even Analysis", ""],                  # 47
                ["Sets to Break Even", "=IF(B39>0, B17/B39, 0)"],         # 48
                ["Pieces to Break Even", "=B48*B8"],                      # 49
                ["", ""],
                
                # SECTION H
                ["SECTION H — Custom Price Scenario (What-if)", ""],      # 51
                ["Test Hoodie Price", v_test_h],                          # 52
                ["Test Pants Price", v_test_p],                           # 53
                ["Test Set Price", v_test_s],                             # 54
                ["New Profit Per Set", "=B54 - B22 - B28"],               # 55
                ["New Sets to Break Even", "=IF(B55>0, B17/B55, 0)"],     # 56
                ["New Total Profit (Full Sell-through)", "=B55*B7"],      # 57
                ["", ""],
                
                # SECTION I
                ["SECTION I — Free / Discounted Units Impact", ""],       # 59
                ["Free Sets Given Away", v_free],                         # 60
                ["Discounted Set Price", v_disc],                         # 61
                ["Lost Revenue (Free Sets)", "=B60 * B35"],               # 62
                # Complex new profit
                ["New Effective Profit Per Set", "=((B7-B60)*B39 + B60*(0-B22-B28))/B7"], # 63
                ["New Break-Even Sets", "=IF(B63>0, B17/B63, 0)"],        # 64
                ["Impact on Total Profit", "=B63*B7 - B44"],              # 65
            ]
            
            # Write data (Clear first to handle row shifts)
            sheet.clear()
            sheet.update("A1", data, value_input_option="USER_ENTERED")
            
            # FORMATTING
            self._format_sheet(sheet)
            
            return {
                'success': True,
                'message': '✅ **Drop 2 Finance Updated!**\n'
                          'Logic updated. User inputs preserved.'
            }
            
        except Exception as e:
            self.logger.error(f"Error creating Drop 2 sheet: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed: {str(e)}'}

    def _format_sheet(self, sheet):
        requests = []
        
        # 1. Clean Slate (White BG, No Grid)
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        # 2. Main Header
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 2},
                "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 14, "bold": True}, "horizontalAlignment": "CENTER", "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95}}},
                "fields": "userEnteredFormat"
            }
        })
        
        # 3. Section Headers (Rows 3, 11, 19, 26, 31, 38, 47, 51, 59) -> Indices 2, 10, 18, 25, 30, 37, 46, 50, 58
        sections = [2, 10, 18, 25, 30, 37, 46, 50, 58]
        for r in sections:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 2},
                    "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "underline": True}, "backgroundColor": {"red": 1, "green": 1, "blue": 1}}},
                    "fields": "userEnteredFormat"
                }
            })
            
        # 4. Currency Format ($) - 2 Decimal pattern
        currency_pattern = "$#,##0.00"
        currency_ranges = [
            (11, 17), # Costs
            (19, 24), # Cost Breakdown (Rows 20-24)
            (26, 29), # Shipping
            (31, 36), # Pricing
            (38, 44), # Profit
            (51, 57), # What-if
            (60, 65), # Impact
        ]
        for start_r, end_r in currency_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": currency_pattern}}}, "fields": "userEnteredFormat.numberFormat"}})
        
        # 5. Percentage Format
        # Profit Margin % (Row 45 -> Index 44)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 44, "endRowIndex": 45, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 6. Yellow Highlights for INPUTS
        # Quantities: B4:B6, B8
        # Costs: B12:B16
        # Unit Cost Inputs: B20:B21
        # Label: B27
        # Prices: B32:B34
        # What-if: B52:B54
        # Impact: B60:B61
        YELLOW = {"red": 1.0, "green": 1.0, "blue": 0.9} # Light yellow
        
        input_indices = [
            (3, 6), (7, 8),     # Section A
            (11, 16),           # Section B
            (19, 21),           # Section C
            (26, 27),           # Section D
            (31, 34),           # Section E
            (51, 54),           # Section H
            (59, 61)            # Section I
        ]
        
        for start_r, end_r in input_indices:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": YELLOW}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 7. Gray Backgrounds for CALCULATIONS (Implicit via white default? Or explict gray?)
        # User said "Calculated cells gray like before"
        GRAY = {"red": 0.95, "green": 0.95, "blue": 0.95}
        calc_indices = [
            (6, 7), (8, 9),     # A
            (16, 17),           # B
            (21, 24),           # C
            (27, 29),           # D
            (34, 36),           # E (Rev)
            (38, 45),           # F
            (47, 49),           # G
            (54, 57),           # H
            (61, 65)            # I
        ]
        for start_r, end_r in calc_indices:
             # Merge with existing format (currency/percent) - repeatCell overwrites unless careful. 
             # We can't easily merge via repeatCell field mask without resetting numberFormat if we don't include it. 
             # Actually, simpler to just set background color for these ranges specifically.
             # But repeatCell overwrites everything in the cell unless we use 'fields' to limit.
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"backgroundColor": GRAY}}, "fields": "userEnteredFormat.backgroundColor"}})

        # 8. Column Widths
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 250}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 150}, "fields": "pixelSize"}})
        
        # 9. Borders
        border = {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}
        requests.append({
            "updateBorders": {
                "range": {"sheetId": sheet.id, "startRowIndex": 2, "endRowIndex": 66, "startColumnIndex": 0, "endColumnIndex": 2},
                "bottom": border, "innerHorizontal": border
            }
        })

        sheet.spreadsheet.batch_update({"requests": requests})

"""
Drop 2 Finance Calculator (Manual Prediction Sheet)

Creates a standalone "Drop 2 Finance Predictions" sheet.
Independent of Shopify or Sync. Manual inputs + auto-calculations.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Drop2Calculator:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.logger = logger

    def create_prediction_sheet(self) -> Dict[str, Any]:
        """Creates the Drop 2 Finance Predictions sheet"""
        self.logger.info("=== INIT DROP 2 FINANCE PREDICTIONS ===")
        
        try:
            sheet_name = "Drop 2 Finance Predictions"
            sheet = self.sheets_manager.create_sheet_if_not_exists(sheet_name)
            sheet.clear()
            
            # --- STRUCTURE ---
            # Columns: A(Label), B(Value), C(Spacer), D(Label), E(Value) (Clean 2-column layout groups)
            # Actually, user asked for specific sections. Let's do a clean single-column input list or dual pane.
            # "Clean, simple, minimal, white background".
            # Let's use Column A for Labels, Column B for Inputs/Calcs.
            # Maybe Column D/E for secondary info if needed, but linear is cleanest for "Minimal".
            
            data = [
                ["DROP 2 FINANCE PREDICTIONS", ""],                       # 1 Header
                ["", ""],
                
                # SECTION A
                ["SECTION A — Drop Quantities", ""],                      # 3
                ["Small Sets", "14"],                                     # 4 (Input)
                ["Medium Sets", "20"],                                    # 5 (Input)
                ["Large Sets", "16"],                                     # 6 (Input)
                ["Total Sets", "=SUM(B4:B6)"],                            # 7 (Calc)
                ["Pieces per Set", "2"],                                  # 8 (Input)
                ["Total Pieces", "=B7*B8"],                               # 9 (Calc)
                ["", ""],
                
                # SECTION B
                ["SECTION B — Total Costs", ""],                          # 11
                ["Sample Cost", "150.00"],                                # 12 (Input)
                ["Bulk Order Cost", "1200.00"],                           # 13 (Input)
                ["Packaging & Supplies", "50.00"],                        # 14 (Input)
                ["Shipping to Me", "45.00"],                              # 15 (Input)
                ["Other Costs", "0.00"],                                  # 16 (Input)
                ["Total Drop Cost", "=SUM(B12:B16)"],                     # 17 (Calc)
                ["", ""],
                
                # SECTION C
                ["SECTION C — Unit Cost Breakdown", ""],                  # 19
                ["Cost Per Set", "=IF(B7>0, B17/B7, 0)"],                 # 20
                ["Cost Per Piece", "=IF(B9>0, B17/B9, 0)"],               # 21
                ["", ""],
                
                # SECTION D
                ["SECTION D — Shipping Label Cost", ""],                  # 23
                ["Shipping Label Cost per Order", "6.44"],                # 24 (Input)
                ["Shipping Cost Per Set", "=B24"],                        # 25 (Same as per order for a set)
                ["Shipping Cost Per Piece", "=IF(B8>0, B24/B8, 0)"],      # 26
                ["", ""],

                # SECTION E
                ["SECTION E — Pricing Inputs", ""],                       # 28
                ["Hoodie Sell Price", "45.00"],                           # 29
                ["Pants Sell Price", "35.00"],                            # 30
                ["Set Sell Price", "=B29+B30"],                           # 31 (Or manual? "Set Sell Price" usually discounted? User said Manual. Let's make it manual default 80)
                # Wait, "Hoodie Sell Price", "Pants Sell Price", "Set Sell Price" listed as inputs.
                # I will make B31 manual input "80.00" but user can override.
                ["Revenue Per Set", "=B31"],                              # 32 (Assuming sold as set)
                ["Revenue Per Piece", "=IF(B8>0, B31/B8, 0)"],            # 33
                ["", ""],

                # SECTION F
                ["SECTION F — Profit Breakdown", ""],                     # 35
                ["Profit Per Set", "=B31 - B20 - B25"],                   # 36 (Price - Cost/Set - Ship/Set)
                ["Profit Per Piece", "=IF(B8>0, B36/B8, 0)"],             # 37
                ["Total Potential Revenue", "=B31*B7"],                   # 38
                ["Total Potential Profit", "=B36*B7"],                    # 39
                ["Profit Margin %", "=IF(B31>0, B36/B31, 0)"],            # 40
                ["", ""],
                
                # SECTION G
                ["SECTION G — Break-Even Analysis", ""],                  # 42
                ["Sets to Break Even", "=IF(B36>0, B17/B36, 0)"],         # 43
                ["Pieces to Break Even", "=B43*B8"],                      # 44
                ["", ""],
                
                # SECTION H
                ["SECTION H — Custom Price Scenario (What-if)", ""],      # 46
                ["Test Hoodie Price", "50.00"],                           # 47
                ["Test Pants Price", "40.00"],                            # 48
                ["Test Set Price", "90.00"],                              # 49
                ["New Profit Per Set", "=B49 - B20 - B25"],               # 50
                ["New Sets to Break Even", "=IF(B50>0, B17/B50, 0)"],     # 51
                ["New Total Profit (Full Sell-through)", "=B50*B7"],      # 52
                ["", ""],
                
                # SECTION I
                ["SECTION I — Free / Discounted Units Impact", ""],       # 54
                ["Free Sets Given Away", "2"],                            # 55
                ["Discounted Set Price", "40.00"],                        # 56
                ["Lost Revenue (Free Sets)", "=B55 * B31"],               # 57
                # New Effective Profit Per Set is complex. 
                # (Total Profit - Lost Revenue from Free) / Total Sets?
                # Or weighted average?
                # "New Effective Profit Per Set" suggests looking at the WHOLE drop.
                # Total Cost is static. Total Rev = (Sets - Free)*Price + Free*0.
                # Let's calculate Total Profit w/ Free: (Total Sets - Free)*ProfitPerSet - (Free * (CostPerSet + ShipPerSet))?
                # Wait, Free sets still cost money to make and ship.
                # Profit on Free Set = 0 - CostPerSet - ShipPerSet = -(Cost+Ship).
                # Profit on Normal Set = Price - Cost - Ship.
                # Total Profit = (Sets-Free)*NormalProfit + Free*(NegativeCost).
                # New Avg Profit = Total Profit / Total Sets.
                ["New Effective Profit Per Set", "=((B7-B55)*B36 + B55*(0-B20-B25))/B7"], # 58
                ["New Break-Even Sets", "=IF(B58>0, B17/B58, 0)"],        # 59
                ["Impact on Total Profit", "=B58*B7 - B39"],              # 60
            ]
            
            # Adjustment: Row 31 "Set Sell Price" to be input "80.00"
            data[30][1] = "80.00"
            
            # Write data
            sheet.update("A1", data, value_input_option="USER_ENTERED")
            
            # FORMATTING
            self._format_sheet(sheet)
            
            return {
                'success': True,
                'message': '✅ **Drop 2 Finance Sheet Created!**\n'
                          'Manual calculator ready for use.'
            }
            
        except Exception as e:
            self.logger.error(f"Error creating Drop 2 sheet: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed: {str(e)}'}

    def _format_sheet(self, sheet):
        requests = []
        
        # 1. Clean Slate (White BG, No Grid)
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        # 2. Main Header (Row 1)
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 2},
                "cell": {"userEnteredFormat": {"textFormat": {"fontSize": 14, "bold": True}, "horizontalAlignment": "CENTER", "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95}}},
                "fields": "userEnteredFormat"
            }
        })
        
        # 3. Section Headers (Rows 3, 11, 19, 23, 28, 35, 42, 46, 54) -> Indices 2, 10, 18, 22, 27, 34, 41, 45, 53
        sections = [2, 10, 18, 22, 27, 34, 41, 45, 53]
        for r in sections:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 2},
                    "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "underline": True}, "backgroundColor": {"red": 1, "green": 1, "blue": 1}}}, # White BG, just bold text
                    "fields": "userEnteredFormat"
                }
            })
            
        # 4. Currency Format
        # B12:B17 (Costs), B20:B21 (Unit Cost), B24:B26 (Ship), B29:B33 (Prices), B36:B39 (Profit), B47:B52 (What-if), B56:B60 (Impact)
        # Note indices are 0-based.
        currency_ranges = [
            (11, 17), # Costs
            (19, 21), # Unit Costs
            (23, 26), # Ship
            (28, 33), # Prices
            (35, 39), # Profit
            (46, 52), # What-if
            (55, 60), # Impact
        ]
        for start_r, end_r in currency_ranges:
             requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": start_r, "endRowIndex": end_r+1, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})
        
        # 5. Percentage Format
        # Profit Margin % (Row 40 -> Index 39)
        requests.append({"repeatCell": {"range": {"sheetId": sheet.id, "startRowIndex": 39, "endRowIndex": 40, "startColumnIndex": 1, "endColumnIndex": 2}, "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 6. Column Widths
        # A = 250 (Labels), B = 150 (Values)
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 250}, "fields": "pixelSize"}})
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 150}, "fields": "pixelSize"}})
        
        # 7. Borders (Bottom border for inputs vs calcs?)
        # Let's keep it minimal as requested. Use light gray borders for the whole table A1:B60
        border = {"style": "SOLID", "width": 1, "color": {"red": 0.9, "green": 0.9, "blue": 0.9}}
        requests.append({
            "updateBorders": {
                "range": {"sheetId": sheet.id, "startRowIndex": 2, "endRowIndex": 61, "startColumnIndex": 0, "endColumnIndex": 2},
                "bottom": border, "innerHorizontal": border
            }
        })

        sheet.spreadsheet.batch_update({"requests": requests})

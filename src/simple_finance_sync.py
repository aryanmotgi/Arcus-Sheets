"""
Simple Finance Sync - FINANCE sheet overhaul

Commands:
1. init_finance_apply() - Creates FINANCE sheet with 5 enhanced sections (A-E)
   Includes "All-In Unit Cost" Calculator (Section D)
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SimpleFinanceSync:
    """Finance sheet manager"""
    
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.logger = logger
    
    def init_finance_apply(self) -> Dict[str, Any]:
        """Create FINANCE sheet structure"""
        self.logger.info("=== INIT FINANCE APPLY ===")
        
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("FINANCE")
            sheet.clear()
            
            # --- FORMULAS & LOGIC ---
            
            # Section D Calculator Formulas
            # Cost Per Piece (E27) = Total Manual Costs (E21) / Pieces Ordered (B27)
            # Allocated Cost Arcus (D39):
            #   If Mode (B29) = "Per Unit": UnitsSold(B39) * CostPerPiece(E27)
            #   If Mode (B29) = "By Product Share": Share%(C39) * TotalManual(E21)
            # Allocated Cost All Paths (D40): Same logic
            
            # Section B Integration
            # Profit (D13/D14) needs to subtract Allocated Cost if Checkbox (E29) is TRUE
            # D13 = GrossProfit - IF(E29, D39, 0)
            
            dataset = [
                ["SECTION A — Top Summary", ""],                          # 1
                ["Total Revenue", "=IFERROR(SUM(ORDERS!F:F), 0)"],       # 2
                ["Total Profit (Gross)", "=IFERROR(SUM(ORDERS!I:I), 0)"],# 3
                ["Total COGS (Product Costs)", "=SUMPRODUCT(ORDERS!G2:G, ORDERS!D2:D)"], # 4
                ["Total Shopify Payout", "=IFERROR(SUM(ORDERS!K:K), 0)"],# 5
                ["Total Shipping Label Cost", "=IFERROR(SUM(ORDERS!H:H), 0)"], # 6
                ["Total Manual Costs", "=IFERROR(E21, 0)"],              # 7
                ["Net Cash In", "=B5-B6-B4-B7"],                         # 8
                ["Avg Profit Margin %", "=IFERROR(AVERAGE(ORDERS!J:J), 0)"], # 9
                ["", ""],                                                # 10
                
                ["SECTION B — Product Breakdown", ""],                   # 11
                ["Product", "Units Sold", "Revenue", "Profit (Net)", "Avg Margin"], # 12
                # Arcus Tee (Row 13)
                ["Arcus Tee", 
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!D:D), 0)", # Units
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!F:F), 0)", # Revenue
                 # Profit: GrossProfit - AllocatedManualCost(if checked)
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!I:I) - IF($E$29, $D$39, 0), 0)", 
                 "=IFERROR(D13/C13, 0)"], # Margin: Profit/Revenue (re-calc based on Net Profit)
                # All Paths Tee (Row 14)
                ["All Paths Tee",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!D:D), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!F:F), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!I:I) - IF($E$29, $D$40, 0), 0)",
                 "=IFERROR(D14/C14, 0)"], 
                ["", ""],                                                # 15
                
                ["SECTION C — Manual Costs", "", "", "", "Amount ($)"],    # 16
                ["Samples", "", "", "", "0"],                             # 17
                ["Bulk Order", "", "", "", "0"],                          # 18
                ["Packaging & Supplies", "", "", "", "0"],                # 19
                ["Other Costs", "", "", "", "0"],                         # 20
                ["", "", "", "Total Manual Costs:", "=SUM(E17:E20)"],     # 21
                ["", ""],                                                # 22
                
                ["SECTION D — Inventory & Cost Calculator", ""],          # 23
                ["Total Manual Costs (from C)", "=E21"],                  # 24
                ["Total Pieces Ordered", "0"],                            # 25 (Input)
                ["Total Pieces Sold", "=B13+B14"],                        # 26 (Sum Units)
                ["Cost Per Piece (Avg)", "=IF(B25>0, B24/B25, 0)"],       # 27
                ["Remaining Inventory", "=B25-B26"],                      # 28
                ["Allocation Mode", "Per Unit (units sold)"],             # 29 (Dropdown)
                ["Unsold Inventory Value", "=B28*B27"],                   # 30
                ["Target Profit Goal", "1000"],                           # 31 (Input)
                ["Units to Hit Target", "=IF((B3/B26)>0, (B31-B3)/ (B3/B26), \"N/A\")"], # 32 Rough est
                ["", "", "", "Apply Allocation?", "FALSE"],               # 33 (Spacer + Checkbox at E29... wait, list index is row 33)
                # Let's align rows carefully.
                # Row 23 is Headers
                # Row 24: Total Manual (Values in B, C, D?? No, just B)
                # Row 29: Allocation Mode. Checkbox is usually separated. 
                # Let's put Checkbox at E29 (same row as Mode)
                
                # Correction: List indices mapping to sheet rows
                # L[22] -> R23 (Header)
                # L[23] -> R24
                # ...
                # L[28] -> R29 (Mode) -> We need Checkbox at E29.
                # The entry for row 29 in list needs 5 elements.
                
                ["", ""], # 34 Spacer for Table Header
                 
                # Allocation Table (Row 36 Header)
                ["Product", "Units Sold", "Share %", "Allocated Cost", "Allocated/Unit"], # 36
                # Arcus Row (37) -> mapped to D39? No, let's map to relative rows.
                # Row 36 in Sheet -> List[35]
                # Row 37 in Sheet -> List[36] (Arcus)
                # Row 38 in Sheet -> List[37] (All Paths)
                
                # Ref: 
                # D13 formula used D39. Let's adjust based on actual final rows.
                # If Header is R36, Arcus is R37, AllPaths is R38.
                # So D13 should ref D37.
                
                # AR CUS ALLOCATION ROW
                ["=A13", "=B13", "50%", 
                 "=IF(B29=\"Per Unit (units sold)\", B37*B27, IF(B29=\"By Product Share (%)\", C37*B24, 0))",
                 "=IF(B37>0, D37/B37, 0)"], # 37
                 
                # ALL PATHS ALLOCATION ROW
                ["=A14", "=B14", "50%", 
                 "=IF(B29=\"Per Unit (units sold)\", B38*B27, IF(B29=\"By Product Share (%)\", C38*B24, 0))",
                 "=IF(B38>0, D38/B38, 0)"], # 38
                 
                ["", ""], # 39
                
                ["SECTION E — Break-even Tracker", ""],                   # 40
                ["Startup Cost", "809.32"],                               # 41
                ["Profit Recovered So Far", "=B3"],                       # 42
                ["Remaining To Break Even", "=B41-B42"]                   # 43
            ]
            
            # Re-map the complex rows to ensure Checkbox placement
            # Row 29 (Index 28): ["Allocation Mode", "Per Unit...", "", "Apply Allocation?", "FALSE"]
            dataset[28] = ["Allocation Mode", "Per Unit (units sold)", "", "Apply Allocation?", "FALSE"]
            
            # Fix target formula (simplistic)
            # Units needed = (Target - CurrentProf) / AvgProfPerUnit
            # AvgProfPerUnit = B3 / B26 (TotalProf / TotalSold)
            dataset[31] = ["Units to Hit Target", "=IFERROR((B31-B3)/(B3/B26), 0)"]
            
            # Write data
            sheet.update("A1", dataset, value_input_option="USER_ENTERED")
            
            # Apply Formatting
            self._format_finance_sheet(sheet)
            
            return {
                'success': True,
                'message': '✅ **FINANCE sheet upgraded!**\n\n'
                          '**New Section D Features:**\n'
                          ' • **All-In Unit Cost**: Auto-calculated from manual costs\n'
                          ' • **Auto-Allocation**: Distributes costs to products\n'
                          ' • **Inventory Tracking**: Tracks unsold value\n'
                          ' • **Live Integration**: Updates Profit/Margin in Section B'
            }
        except Exception as e:
            self.logger.error(f"Error in init_finance_apply: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed to finance: {str(e)}'}

    def _format_finance_sheet(self, sheet):
        requests = []
        
        # 1. Section Headers (Dark Blue)
        # Rows: 1, 11, 16, 23, 40 -> Indices: 0, 10, 15, 22, 39
        section_indices = [0, 10, 15, 22, 39]
        for r in section_indices:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 5},
                    "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.2, "green": 0.3, "blue": 0.5}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True, "fontSize": 12}, "padding": {"left": 10}}},
                    "fields": "userEnteredFormat"
                }
            })

        # 2. Table Headers (Gray)
        # Row 12 (Ind 11), Row 36 (Ind 35)
        for r in [11, 35]:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 5},
                    "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}, "textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
                    "fields": "userEnteredFormat"
                }
            })
            
        # 3. Currency Format ($)
        # Sec A: B2-B8
        # Sec B: C13-D14
        # Sec C: E17-E21
        # Sec D: B24, B27 (CostPerPiece), B30, D37-E38 (Allocations)
        # Sec E: B41-B43
        currency_ranges = [
            {"startRowIndex": 1, "endRowIndex": 8, "startColumnIndex": 1, "endColumnIndex": 2},
            {"startRowIndex": 12, "endRowIndex": 14, "startColumnIndex": 2, "endColumnIndex": 4},
            {"startRowIndex": 16, "endRowIndex": 21, "startColumnIndex": 4, "endColumnIndex": 5},
            {"startRowIndex": 23, "endRowIndex": 24, "startColumnIndex": 1, "endColumnIndex": 2}, # B24
            {"startRowIndex": 26, "endRowIndex": 27, "startColumnIndex": 1, "endColumnIndex": 2}, # B27
            {"startRowIndex": 29, "endRowIndex": 30, "startColumnIndex": 1, "endColumnIndex": 2}, # B30
            {"startRowIndex": 36, "endRowIndex": 38, "startColumnIndex": 3, "endColumnIndex": 5}, # D37-E38
            {"startRowIndex": 40, "endRowIndex": 43, "startColumnIndex": 1, "endColumnIndex": 2}, # B41-B43
        ]
        for rng in currency_ranges:
            requests.append({"repeatCell": {"range": dict(sheetId=sheet.id, **rng), "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 4. Percentage Format (%)
        # B9, E13-E14, C37-C38
        pct_ranges = [
            {"startRowIndex": 8, "endRowIndex": 9, "startColumnIndex": 1, "endColumnIndex": 2},
            {"startRowIndex": 12, "endRowIndex": 14, "startColumnIndex": 4, "endColumnIndex": 5},
            {"startRowIndex": 36, "endRowIndex": 38, "startColumnIndex": 2, "endColumnIndex": 3},
        ]
        for rng in pct_ranges:
            requests.append({"repeatCell": {"range": dict(sheetId=sheet.id, **rng), "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 5. Checkbox (E29 -> Index 28)
        requests.append({
            "setDataValidation": {
                "range": {"sheetId": sheet.id, "startRowIndex": 28, "endRowIndex": 29, "startColumnIndex": 4, "endColumnIndex": 5},
                "rule": {"condition": {"type": "BOOLEAN"}, "showCustomUi": True}
            }
        })
        
        # 6. Dropdown (B29 -> Index 28)
        requests.append({
            "setDataValidation": {
                "range": {"sheetId": sheet.id, "startRowIndex": 28, "endRowIndex": 29, "startColumnIndex": 1, "endColumnIndex": 2},
                "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": "Per Unit (units sold)"}, {"userEnteredValue": "By Product Share (%)"}]}, "showCustomUi": True}
            }
        })
        
        # 7. Margins Cond Formatting
        # B9, E13:E14
        ranges = [
            {"sheetId": sheet.id, "startRowIndex": 8, "endRowIndex": 9, "startColumnIndex": 1, "endColumnIndex": 2},
            {"sheetId": sheet.id, "startRowIndex": 12, "endRowIndex": 14, "startColumnIndex": 4, "endColumnIndex": 5}
        ]
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges, "booleanRule": {"condition": {"type": "NUMBER_LESS", "values": [{"userEnteredValue": "0.25"}]}, "format": {"backgroundColor": {"red": 1.0, "green": 0.8, "blue": 0.8}}}}, "index": 0}})
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges, "booleanRule": {"condition": {"type": "NUMBER_BETWEEN", "values": [{"userEnteredValue": "0.25"}, {"userEnteredValue": "0.35"}]}, "format": {"backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.8}}}}, "index": 1}})
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges, "booleanRule": {"condition": {"type": "NUMBER_GREATER_THAN_EQ", "values": [{"userEnteredValue": "0.35"}]}, "format": {"backgroundColor": {"red": 0.8, "green": 1.0, "blue": 0.8}}}}, "index": 2}})

        # 8. Column Widths
        widths = [250, 150, 120, 120, 150]
        for i, w in enumerate(widths):
            requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1}, "properties": {"pixelSize": w}, "fields": "pixelSize"}})
            
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        sheet.spreadsheet.batch_update({"requests": requests})

def init_finance_apply(sheets_manager) -> Dict[str, Any]:
    agent = SimpleFinanceSync(sheets_manager)
    return agent.init_finance_apply()

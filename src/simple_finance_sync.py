"""
Simple Finance Sync - FINANCE sheet overhaul (v3 Dashboard)

Commands:
1. init_finance_apply() - Creates FINANCE dashboard
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
            
            # --- FORMULAS & MAPPING (ORDERS v3) ---
            # Qty: Col E
            # Revenue (Item only): Col I
            # Total Collected (Item+Ship): Col Q
            # Profit: Col S
            # COGS: SumProduct(M, E)
            # Payout: Col U
            # Label Cost (Effective): Col P
            # Manual Costs: E21 (Section C)
            
            dataset = [
                ["SECTION A — Top Summary", ""],                          # 1
                ["Total Collected (Revenue + Shipping)", "=IFERROR(SUM(ORDERS!Q:Q), 0)"], # 2
                ["Total Revenue (Items only)", "=IFERROR(SUM(ORDERS!I:I), 0)"], # 3
                ["Total Profit (Net)", "=IFERROR(SUM(ORDERS!S:S), 0)"],  # 4
                ["Avg Profit Margin %", "=IFERROR(AVERAGE(ORDERS!T:T), 0)"], # 5
                
                ["Total Shopify Payout", "=IFERROR(SUM(ORDERS!U:U), 0)"], # 6
                ["Total Shipping Label Cost", "=IFERROR(SUM(ORDERS!P:P), 0)"], # 7
                ["Total COGS (Product Costs)", "=SUMPRODUCT(ORDERS!M2:M, ORDERS!E2:E)"], # 8
                ["Total Manual Costs", "=IFERROR(E21, 0)"],              # 9
                ["Net Cash In", "=B6-B7-B8-B9"],                         # 10
                ["", ""],                                                # 11
                
                ["SECTION B — Product Breakdown", ""],                   # 12
                ["Product", "Units Sold", "Total Collected", "Profit", "Avg Margin"], # 13
                # Arcus Tee
                ["Arcus Tee", 
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!E:E), 0)", # Units (Col E)
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!Q:Q), 0)", # Collected (Col Q)
                 # Profit: GrossProfit - AllocatedManualCost(if checked)
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!S:S) - IF($E$29, $D$38, 0), 0)", 
                 "=IFERROR(D14/C14, 0)"], # Margin
                # All Paths Tee
                ["All Paths Tee",
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!E:E), 0)",
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!Q:Q), 0)",
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!S:S) - IF($E$29, $D$39, 0), 0)",
                 "=IFERROR(D15/C15, 0)"], 
                ["", ""],                                                # 16
                
                ["SECTION C — Manual Costs", "", "", "", "Amount ($)"],    # 17
                ["Samples", "", "", "", "0"],                             # 18
                ["Bulk Order", "", "", "", "=IF(B28, B25, 0)"],           # 19
                ["Packaging & Supplies", "", "", "", "0"],                # 20
                ["Other Costs", "", "", "", "0"],                         # 21
                ["", "", "", "Total Manual Costs:", "=SUM(E18:E21)"],     # 22
                ["", ""],                                                # 23
                
                ["SECTION D — Inventory & Cost Calculator", ""],          # 24
                ["Total Manual Costs (from C)", "=E22"],                  # 25 Total is at E22
                ["Total Pieces Ordered", "0"],                            # 26
                ["Total Pieces Sold", "=B14+B15"],                        # 27
                ["Cost Per Piece (Avg)", "=IF(B26>0, B25/B26, 0)"],       # 28
                ["Apply Bulk Cost to Manual Costs?", "FALSE"],            # 29 (Checkbox E29)
                ["Allocation Mode", "Per Unit (units sold)"],             # 30 (Dropdown B30)
                ["Target Profit Goal", "1000"],                           # 31
                ["Units to Hit Target", "=IFERROR((B31-B4)/(B4/B26), 0)"],# 32
                ["", ""],                                                # 33
                
                ["", ""], # 34 Spacer for Table Header (Wait, we can simplify)
                # Let's clean up indices.
                # R24: Header
                # R25: Manual Costs
                # R26: Pieces Ordered
                # R27: Pieces Sold
                # R28: Cost Per Piece
                # R29: Checkbox (Cols 1,2 empty, label at D, checkbox at E)
                # R30: Allocation Mode
                # R31: Target
                # R32: Units
                
                # R35: Table Header
                
                ["", ""], # 35
                ["Product", "Units Sold", "Share %", "Allocated Cost", "Allocated/Unit"], # 36
                # Arcus Row (37) -> D37 is cost?? No wait.
                # Profit formula (D14) referenced D38.
                # Let's put Arcus at 38, AllPaths at 39. So header at 37.
                
                # Sheet Row 37 (List Index 36) -> Header
                # Sheet Row 38 (List Index 37) -> Arcus
                
                ["=A14", "=B14", "50%", 
                 "=IF(B30=\"Per Unit (units sold)\", B38*B28, IF(B30=\"By Product Share (%)\", C38*B25, 0))",
                 "=IF(B38>0, D38/B38, 0)"], 
                 
                ["=A15", "=B15", "50%", 
                 "=IF(B30=\"Per Unit (units sold)\", B39*B28, IF(B30=\"By Product Share (%)\", C39*B25, 0))",
                 "=IF(B39>0, D39/B39, 0)"], 
                 
                ["", ""], # 40
                
                ["SECTION E — Break-even Tracker", ""],                   # 41
                ["Startup Cost", "809.32"],                               # 42
                ["Break-even (Profit)", "=B42-B4"],                       # 43
                ["Break-even (Net Cash In)", "=B42-B10"]                  # 44
            ]
             
            # Adjust Checkbox Row (Index 28 -> Row 29)
            dataset[28] = ["", "", "", "Apply Bulk Cost to Manual Costs?", "FALSE"]
            
            # Write data
            sheet.update("A1", dataset, value_input_option="USER_ENTERED")
            
            # Apply Formatting
            self._format_finance_sheet(sheet)
            
            return {
                'success': True,
                'message': '✅ **FINANCE sheet upgraded (v3)!**\n'
                          'Top Summary Cards, Persistent manual costs, and break-even tracker.'
            }
        except Exception as e:
            self.logger.error(f"Error in init_finance_apply: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed to finance: {str(e)}'}

    def _format_finance_sheet(self, sheet):
        requests = []
        
        # 1. Section Headers (Row 1, 12, 17, 24, 41) -> Indices 0, 11, 16, 23, 40
        section_indices = [0, 11, 16, 23, 40]
        for r in section_indices:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 5},
                    "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.2, "green": 0.3, "blue": 0.5}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True, "fontSize": 12}, "padding": {"left": 10}}},
                    "fields": "userEnteredFormat"
                }
            })

        # 2. Table Headers (Row 13, 37) -> Indices 12, 36
        for r in [12, 36]:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 5},
                    "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}, "textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
                    "fields": "userEnteredFormat"
                }
            })
            
        # 3. Currency Format ($)
        # Sec A: B2-B10
        # Sec B: C14-D15 (Row 14-15)
        # Sec C: E18-E22
        # Sec D: B25, B28 (CostPerPiece), B31, D38-E39
        # Sec E: B42-B44
        currency_ranges = [
            {"startRowIndex": 1, "endRowIndex": 10, "startColumnIndex": 1, "endColumnIndex": 2},
            {"startRowIndex": 13, "endRowIndex": 15, "startColumnIndex": 2, "endColumnIndex": 4},
            {"startRowIndex": 17, "endRowIndex": 22, "startColumnIndex": 4, "endColumnIndex": 5},
            {"startRowIndex": 24, "endRowIndex": 25, "startColumnIndex": 1, "endColumnIndex": 2}, 
            {"startRowIndex": 27, "endRowIndex": 28, "startColumnIndex": 1, "endColumnIndex": 2}, 
            {"startRowIndex": 30, "endRowIndex": 31, "startColumnIndex": 1, "endColumnIndex": 2}, 
            {"startRowIndex": 37, "endRowIndex": 39, "startColumnIndex": 3, "endColumnIndex": 5}, 
            {"startRowIndex": 41, "endRowIndex": 44, "startColumnIndex": 1, "endColumnIndex": 2},
        ]
        for rng in currency_ranges:
            requests.append({"repeatCell": {"range": dict(sheetId=sheet.id, **rng), "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 4. Percentage Format (%)
        # B5, E14-E15, C38-C39
        pct_ranges = [
            {"startRowIndex": 4, "endRowIndex": 5, "startColumnIndex": 1, "endColumnIndex": 2},
            {"startRowIndex": 13, "endRowIndex": 15, "startColumnIndex": 4, "endColumnIndex": 5},
            {"startRowIndex": 37, "endRowIndex": 39, "startColumnIndex": 2, "endColumnIndex": 3},
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
        
        # 6. Dropdown (B30 -> Index 29)
        requests.append({
            "setDataValidation": {
                "range": {"sheetId": sheet.id, "startRowIndex": 29, "endRowIndex": 30, "startColumnIndex": 1, "endColumnIndex": 2},
                "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": "Per Unit (units sold)"}, {"userEnteredValue": "By Product Share (%)"}]}, "showCustomUi": True}
            }
        })
        
        # 7. Margins Cond Formatting
        ranges = [
            {"sheetId": sheet.id, "startRowIndex": 4, "endRowIndex": 5, "startColumnIndex": 1, "endColumnIndex": 2},
            {"sheetId": sheet.id, "startRowIndex": 13, "endRowIndex": 15, "startColumnIndex": 4, "endColumnIndex": 5}
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

"""
Simple Finance Sync - FINANCE sheet overhaul (Strict Alignment)

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
            
            # --- FORMULAS & MAPPING (ORDERS Strict v4) ---
            # Qty: E
            # Unit Cost: F
            # Price: G
            # Revenue: H
            # Shipping: I
            # Label: J
            # Profit: K
            
            # Total Collected = Revenue(H) + Shipping(I)
            
            dataset = [
                ["SECTION A — Top Summary", ""],                          # 1
                ["Total Collected (Revenue + Shipping)", "=IFERROR(SUM(ORDERS!H:H) + SUM(ORDERS!I:I), 0)"], # 2
                ["Total Revenue (Items only)", "=IFERROR(SUM(ORDERS!H:H), 0)"], # 3
                ["Total Profit (Net)", "=IFERROR(SUM(ORDERS!K:K), 0)"],  # 4
                ["Total Shipping Label Cost", "=IFERROR(SUM(ORDERS!J:J), 0)"], # 5
                ["Total COGS (Product Costs)", "=SUMPRODUCT(ORDERS!F2:F, ORDERS!E2:E)"], # 6
                ["Total Manual Costs", "=IFERROR(E21, 0)"],              # 7
                ["Net Cash In", "=B2-B6-B7"],                            # 8 (Collected - COGS - Manual) (Wait, Label is part of Profit formula so strictly Profit involves Label. But "Net Cash In" usually implies actual bank? 
                # Profit = Collected - COGS - Label. 
                # So Sum(Profit) = Sum(Collected) - Sum(COGS) - Sum(Label).
                # Net Cash In = Sum(Profit) - Manual.
                # Let's simple use: Total Profit - Manual.
                # User asked: "Net Cash In = Shopify Payout – Shipping Label Cost – COGS – Manual Costs"
                # Payout ~ Collected. 
                # So Net Cash In = Collected - Label - COGS - Manual.
                # Yes: = B2 - B5 - B6 - B7.
                
                ["Avg Profit Margin %", "=IFERROR(B4/B2, 0)"],           # 9
                ["", ""],                                                # 10
                
                ["SECTION B — Product Breakdown", ""],                   # 11
                ["Product", "Units Sold", "Total Collected", "Profit", "Avg Margin"], # 12
                # Arcus Tee
                ["Arcus Tee", 
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!E:E), 0)", # Units (Col E)
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!H:H) + SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!I:I), 0)", # Collected (H+I)
                 # Profit: GrossProfit - AllocatedManualCost(if checked)
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!K:K) - IF($E$29, $D$38, 0), 0)", 
                 "=IFERROR(D14/C14, 0)"], # Margin
                # All Paths Tee
                ["All Paths Tee",
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!E:E), 0)",
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!H:H) + SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!I:I), 0)",
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!K:K) - IF($E$29, $D$39, 0), 0)",
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
                ["Total Manual Costs (from C)", "=E22"],                  # 25
                ["Total Pieces Ordered", "0"],                            # 26
                ["Total Pieces Sold", "=B14+B15"],                        # 27
                ["Cost Per Piece (Avg)", "=IF(B26>0, B25/B26, 0)"],       # 28
                ["Apply Bulk Cost to Manual Costs?", "FALSE"],            # 29
                ["Allocation Mode", "Per Unit (units sold)"],             # 30
                ["Target Profit Goal", "1000"],                           # 31
                ["Units to Hit Target", "=IFERROR((B31-B4)/(B4/B26), 0)"],# 32
                ["", ""],                                                # 33
                
                ["", ""], # 34 Spacer for Table Header 
                ["", ""], # 35
                ["Product", "Units Sold", "Share %", "Allocated Cost", "Allocated/Unit"], # 36
                # Header at 37
                
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
                ["Break-even (Net Cash In)", "=B42-B8"]                   # 44
            ]
             
            # Adjust Checkbox Row (Index 28 -> Row 29)
            dataset[28] = ["", "", "", "Apply Bulk Cost to Manual Costs?", "FALSE"]
            
            # Write data
            sheet.update("A1", dataset, value_input_option="USER_ENTERED")
            
            # Apply Formatting
            self._format_finance_sheet(sheet)
            
            return {
                'success': True,
                'message': '✅ **FINANCE sheet aligned!**\n'
                          'Formulas linked to new strict ORDERS layout.'
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
        pct_ranges = [
            {"startRowIndex": 8, "endRowIndex": 9, "startColumnIndex": 1, "endColumnIndex": 2},
            {"startRowIndex": 13, "endRowIndex": 15, "startColumnIndex": 4, "endColumnIndex": 5},
            {"startRowIndex": 37, "endRowIndex": 39, "startColumnIndex": 2, "endColumnIndex": 3},
        ]
        for rng in pct_ranges:
            requests.append({"repeatCell": {"range": dict(sheetId=sheet.id, **rng), "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 5. Checkbox (E29 -> Index 28)
        requests.append({"setDataValidation": {"range": {"sheetId": sheet.id, "startRowIndex": 28, "endRowIndex": 29, "startColumnIndex": 4, "endColumnIndex": 5}, "rule": {"condition": {"type": "BOOLEAN"}, "showCustomUi": True}}})
        
        # 6. Dropdown (B30 -> Index 29)
        requests.append({"setDataValidation": {"range": {"sheetId": sheet.id, "startRowIndex": 29, "endRowIndex": 30, "startColumnIndex": 1, "endColumnIndex": 2}, "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": "Per Unit (units sold)"}, {"userEnteredValue": "By Product Share (%)"}]}, "showCustomUi": True}}})
        
        # 7. Margins Cond Formatting
        # (Removed Blue highlights as requested, only keep Warning/Good margins)
        ranges = [
            {"sheetId": sheet.id, "startRowIndex": 8, "endRowIndex": 9, "startColumnIndex": 1, "endColumnIndex": 2},
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

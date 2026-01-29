"""
Simple Finance Sync - FINANCE sheet overhaul

Commands:
1. init_finance_apply() - Creates FINANCE sheet with 5 enhanced sections (A-E)
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
            
            # Formulas
            # COGS = Sum product of unit cost * qty. 
            # Note: ORDERS!G is Unit Cost, ORDERS!D is Qty.
            # Formula: =SUMPRODUCT(ORDERS!G2:G, ORDERS!D2:D)
            # Actually easier: Sum(ORDERS!G:G * ORDERS!D:D) is ArrayFormula but SUMPRODUCT is cleaner.
            # But wait, we define COGS per row in ORDERS logic as Unit Cost * Qty? 
            # In simple_orders_sync we defined Unit Cost column (G) but didn't make a Total Cost column. 
            # So we calculate it here.
            
            data = [
                ["SECTION A — Top Summary", ""],                          # Row 1
                ["Total Revenue", "=IFERROR(SUM(ORDERS!F:F), 0)"],       # Row 2
                ["Total Profit", "=IFERROR(SUM(ORDERS!I:I), 0)"],        # Row 3
                ["Total COGS (Product Costs)", "=SUMPRODUCT(ORDERS!G2:G, ORDERS!D2:D)"], # Row 4
                ["Total Shopify Payout", "=IFERROR(SUM(ORDERS!K:K), 0)"],# Row 5
                ["Total Shipping Label Cost", "=IFERROR(SUM(ORDERS!H:H), 0)"], # Row 6
                ["Total Manual Costs", "=IFERROR(E23, 0)"],              # Row 7 (Ref Section C)
                ["Net Cash In", "=B5-B6-B4-B7"],                         # Row 8 (Payout - Ship - COGS - Manual)
                ["Avg Profit Margin %", "=IFERROR(AVERAGE(ORDERS!J:J), 0)"], # Row 9
                
                ["SECTION B — Product Breakdown", ""],                   # Row 11
                ["Product", "Units Sold", "Revenue", "Profit", "Avg Margin"], # Row 12
                ["Arcus Tee", 
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!D:D), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!F:F), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!I:I), 0)",
                 "=IFERROR(AverageIf(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!J:J), 0)"], # Row 13
                ["All Paths Tee",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!D:D), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!F:F), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!I:I), 0)",
                 "=IFERROR(AverageIf(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!J:J), 0)"], # Row 14
                
                ["SECTION C — Manual Costs", "", "", "", "Amount ($)"],    # Row 16
                ["Samples", "", "", "", "0"],                             # Row 17
                ["Bulk Order", "", "", "", "=IF(B28, B25, 0)"],           # Row 18 (Auto-fill if checked)
                ["Packaging & Supplies", "", "", "", "0"],                # Row 19
                ["Other Costs", "", "", "", "0"],                         # Row 20
                ["", "", "", "Total Manual Costs:", "=SUM(E17:E20)"],     # Row 23 (Total)
                
                ["SECTION D — Bulk Order Cost Calculator", ""],           # Row 24
                ["Total Bulk Order Cost ($)", "0"],                       # Row 25
                ["Total Pieces Ordered", "0"],                            # Row 26
                ["Cost Per Piece", "=IF(B26>0, B25/B26, \"\")"],          # Row 27
                ["Apply Bulk Cost to Manual Costs?", "FALSE"],            # Row 28 (Checkbox)
                
                ["SECTION E — Break-even Tracker", ""],                   # Row 30
                ["Startup Cost", "809.32"],                               # Row 31
                ["Profit Recovered So Far", "=B3"],                       # Row 32
                ["Break-even using Net Cash In", "=B8"],                  # Row 33
                ["Remaining To Break Even", "=B31-B33"]                   # Row 34
            ]
            
            # Write data (careful with row indices, list represents rows sequentially)
            # My list above has simplified spacing. Let's make it consistent.
            # Row 1: Sec A
            # Row 2-9: Data
            # Row 10: Spacer
            # Row 11: Sec B
            # Row 12: Header
            # Row 13-14: Data
            # Row 15: Spacer
            # Row 16: Sec C
            # Row 17-20: Data
            # Row 21: Total (oops, I put it at 23 index logic visually)
            
            # Let's map exactly to array
            formatted_data = []
            formatted_data.append(data[0]) # R1 Sec A
            formatted_data.append(data[1]) # R2 Rev
            formatted_data.append(data[2]) # R3 Prof
            formatted_data.append(data[3]) # R4 COGS
            formatted_data.append(data[4]) # R5 Payout
            formatted_data.append(data[5]) # R6 Ship
            formatted_data.append(data[6]) # R7 Manual
            formatted_data.append(data[7]) # R8 Net Cash
            formatted_data.append(data[8]) # R9 Avg Margin
            formatted_data.append(["", ""]) # R10 Spacer
            
            formatted_data.append(data[9]) # R11 Sec B
            formatted_data.append(data[10]) # R12 Header
            formatted_data.append(data[11]) # R13 Arcus
            formatted_data.append(data[12]) # R14 All Paths
            formatted_data.append(["", ""]) # R15 Spacer
            
            formatted_data.append(data[13]) # R16 Sec C
            formatted_data.append(data[14]) # R17 Samples
            formatted_data.append(data[15]) # R18 Bulk
            formatted_data.append(data[16]) # R19 Packaging
            formatted_data.append(data[17]) # R20 Other
            formatted_data.append(["", "", "", "Total Manual Costs:", "=SUM(E17:E20)"]) # R21 Total
            formatted_data.append(["", ""]) # R22 Spacer
            
            formatted_data.append(data[19]) # R23 Sec D (Wait, indices shifted)
            # Re-building explicit list is safer to avoid off-by-one errors in my head
            
            dataset = [
                ["SECTION A — Top Summary", ""],                          # 1
                ["Total Revenue", "=IFERROR(SUM(ORDERS!F:F), 0)"],       # 2
                ["Total Profit", "=IFERROR(SUM(ORDERS!I:I), 0)"],        # 3
                ["Total COGS (Product Costs)", "=SUMPRODUCT(ORDERS!G2:G, ORDERS!D2:D)"], # 4
                ["Total Shopify Payout", "=IFERROR(SUM(ORDERS!K:K), 0)"],# 5
                ["Total Shipping Label Cost", "=IFERROR(SUM(ORDERS!H:H), 0)"], # 6
                ["Total Manual Costs", "=IFERROR(E21, 0)"],              # 7 (Ref Row 21)
                ["Net Cash In", "=B5-B6-B4-B7"],                         # 8
                ["Avg Profit Margin %", "=IFERROR(AVERAGE(ORDERS!J:J), 0)"], # 9
                ["", ""],                                                # 10
                
                ["SECTION B — Product Breakdown", ""],                   # 11
                ["Product", "Units Sold", "Revenue", "Profit", "Avg Margin"], # 12
                ["Arcus Tee", 
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!D:D), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!F:F), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!I:I), 0)",
                 "=IFERROR(AverageIf(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!J:J), 0)"], # 13
                ["All Paths Tee",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!D:D), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!F:F), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!I:I), 0)",
                 "=IFERROR(AverageIf(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!J:J), 0)"], # 14
                ["", ""],                                                # 15
                
                ["SECTION C — Manual Costs", "", "", "", "Amount ($)"],    # 16
                ["Samples", "", "", "", "0"],                             # 17
                ["Bulk Order", "", "", "", "=IF(B27, B24, 0)"],           # 18 (Ref R27 Checkbox, R24 Cost)
                ["Packaging & Supplies", "", "", "", "0"],                # 19
                ["Other Costs", "", "", "", "0"],                         # 20
                ["", "", "", "Total Manual Costs:", "=SUM(E17:E20)"],     # 21
                ["", ""],                                                # 22
                
                ["SECTION D — Bulk Order Cost Calculator", ""],           # 23
                ["Total Bulk Order Cost ($)", "0"],                       # 24
                ["Total Pieces Ordered", "0"],                            # 25
                ["Cost Per Piece", "=IF(B25>0, B24/B25, \"\")"],          # 26
                ["Apply Bulk Cost to Manual Costs?", "FALSE"],            # 27
                ["", ""],                                                # 28               
                
                ["SECTION E — Break-even Tracker", ""],                   # 29
                ["Startup Cost", "809.32"],                               # 30
                ["Profit Recovered So Far", "=B3"],                       # 31
                ["Break-even using Net Cash In", "=B8"],                  # 32
                ["Remaining To Break Even", "=B30-B32"]                   # 33
            ]

            sheet.update("A1", dataset, value_input_option="USER_ENTERED")
            
            # Apply Formatting & Checkbox
            self._format_finance_sheet(sheet)
            
            return {
                'success': True,
                'message': '✅ **FINANCE sheet upgraded!**\n\n'
                          'Updated sections:\n'
                          ' • Section A: Added COGS & Net Cash In\n'
                          ' • Section C: Fixed 4 manual cost rows\n'
                          ' • Section D: Added bulk cost checkbox automation\n'
                          ' • Margin Health: Color coded (Green >35%)'
            }
        except Exception as e:
            self.logger.error(f"Error in init_finance_apply: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed to finance: {str(e)}'}

    def _format_finance_sheet(self, sheet):
        requests = []
        
        # 1. Section Headers (Row 1, 11, 16, 23, 29) -> Bold, Dark Blue BG
        # Indices: 0, 10, 15, 22, 28
        section_indices = [0, 10, 15, 22, 28]
        for r in section_indices:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 5},
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.2, "green": 0.3, "blue": 0.5},
                            "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True, "fontSize": 12},
                            "padding": {"left": 10}
                        }
                    },
                    "fields": "userEnteredFormat"
                }
            })

        # 2. Section B Table Header (Row 12 -> Index 11)
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 11, "endRowIndex": 12, "startColumnIndex": 0, "endColumnIndex": 5},
                "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}, "textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
                "fields": "userEnteredFormat"
            }
        })
        
        # 3. Currency Format ($)
        # Sec A: B2-B8 (Ind 1-8)
        # Sec B: C13-D14 (Ind 12-14)
        # Sec C: E17-E21 (Ind 16-21)
        # Sec D: B24, B26 (Ind 23, 25)
        # Sec E: B30-B33 (Ind 29-33)
        currency_ranges = [
            {"startRowIndex": 1, "endRowIndex": 8, "startColumnIndex": 1, "endColumnIndex": 2},
            {"startRowIndex": 12, "endRowIndex": 14, "startColumnIndex": 2, "endColumnIndex": 4},
            {"startRowIndex": 16, "endRowIndex": 21, "startColumnIndex": 4, "endColumnIndex": 5},
            {"startRowIndex": 23, "endRowIndex": 24, "startColumnIndex": 1, "endColumnIndex": 2},
            {"startRowIndex": 25, "endRowIndex": 26, "startColumnIndex": 1, "endColumnIndex": 2},
            {"startRowIndex": 29, "endRowIndex": 33, "startColumnIndex": 1, "endColumnIndex": 2},
        ]
        for rng in currency_ranges:
            requests.append({"repeatCell": {"range": dict(sheetId=sheet.id, **rng), "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 4. Percentage Format (%) (B9, E13-E14) -> Indices 8, 12-14
        pct_ranges = [
            {"startRowIndex": 8, "endRowIndex": 9, "startColumnIndex": 1, "endColumnIndex": 2},
            {"startRowIndex": 12, "endRowIndex": 14, "startColumnIndex": 4, "endColumnIndex": 5},
        ]
        for rng in pct_ranges:
            requests.append({"repeatCell": {"range": dict(sheetId=sheet.id, **rng), "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 5. Checkbox (B27 -> Index 26)
        requests.append({
            "setDataValidation": {
                "range": {"sheetId": sheet.id, "startRowIndex": 26, "endRowIndex": 27, "startColumnIndex": 1, "endColumnIndex": 2},
                "rule": {"condition": {"type": "BOOLEAN"}, "showCustomUi": True}
            }
        })
        
        # 6. Margin Health Conditional Formatting
        # Ranges: B9 (Avg Margin), E13:E14 (Prod Margin)
        ranges = [
            {"sheetId": sheet.id, "startRowIndex": 8, "endRowIndex": 9, "startColumnIndex": 1, "endColumnIndex": 2},
            {"sheetId": sheet.id, "startRowIndex": 12, "endRowIndex": 14, "startColumnIndex": 4, "endColumnIndex": 5}
        ]
        
        # Red < 25%
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges, "booleanRule": {"condition": {"type": "NUMBER_LESS", "values": [{"userEnteredValue": "0.25"}]}, "format": {"backgroundColor": {"red": 1.0, "green": 0.8, "blue": 0.8}}}}, "index": 0}})
        # Yellow 25-35%
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges, "booleanRule": {"condition": {"type": "NUMBER_BETWEEN", "values": [{"userEnteredValue": "0.25"}, {"userEnteredValue": "0.35"}]}, "format": {"backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.8}}}}, "index": 1}})
        # Green >= 35%
        requests.append({"addConditionalFormatRule": {"rule": {"ranges": ranges, "booleanRule": {"condition": {"type": "NUMBER_GREATER_THAN_EQ", "values": [{"userEnteredValue": "0.35"}]}, "format": {"backgroundColor": {"red": 0.8, "green": 1.0, "blue": 0.8}}}}, "index": 2}})

        # 7. Column Widths
        widths = [250, 150, 120, 120, 150]
        for i, w in enumerate(widths):
            requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1}, "properties": {"pixelSize": w}, "fields": "pixelSize"}})
            
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        sheet.spreadsheet.batch_update({"requests": requests})

def init_finance_apply(sheets_manager) -> Dict[str, Any]:
    agent = SimpleFinanceSync(sheets_manager)
    return agent.init_finance_apply()

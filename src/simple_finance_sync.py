"""
Simple Finance Sync - FINANCE sheet overhaul

Commands:
1. init_finance_apply() - Creates FINANCE sheet with 5 sections (A-E)
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
            
            # Define structure (Values and Formulas)
            data = [
                ["SECTION A — Top Summary", ""],                          # Row 1
                ["Total Revenue", "=IFERROR(SUM(ORDERS!F:F), 0)"],       # Row 2
                ["Total Profit", "=IFERROR(SUM(ORDERS!I:I), 0)"],        # Row 3
                ["Avg Profit Margin %", "=IFERROR(AVERAGE(ORDERS!J:J), 0)"], # Row 4
                ["Total Shopify Payout", "=IFERROR(SUM(ORDERS!K:K), 0)"],# Row 5
                ["Total Shipping Label Cost", "=IFERROR(SUM(ORDERS!H:H), 0)"], # Row 6
                ["Total Order Costs", "=IFERROR(E23, 0)"],               # Row 7 (Ref Section C)
                ["Net Cash In", "=IFERROR(B5-B6-B7, 0)"],                # Row 8
                ["", ""],
                
                ["SECTION B — Product Breakdown", ""],                   # Row 10
                ["Product", "Units Sold", "Revenue", "Profit", "Avg Margin"], # Row 11
                ["Arcus Tee", 
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!D:D), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!F:F), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!I:I), 0)",
                 "=IFERROR(AverageIf(ORDERS!B:B, \"*Arcus Tee*\", ORDERS!J:J), 0)"], # Row 12
                ["All Paths Tee",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!D:D), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!F:F), 0)",
                 "=IFERROR(SUMIF(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!I:I), 0)",
                 "=IFERROR(AverageIf(ORDERS!B:B, \"*All Paths Tee*\", ORDERS!J:J), 0)"], # Row 13
                ["", "", "", "", ""],
                
                ["SECTION C — Manual Order/Inventory Costs", "", "", "", ""], # Row 15
                ["Cost Name", "", "", "", "Amount ($)"],                 # Row 16
                ["Samples", "", "", "", "0"],                            # Row 17
                ["Bulk Order", "", "", "", "0"],                         # Row 18
                ["Shipping to Me", "", "", "", "0"],                     # Row 19
                ["Packaging / Supplies", "", "", "", "0"],               # Row 20
                ["Other", "", "", "", "0"],                              # Row 21
                ["", "", "", "Total Order Costs:", "=SUM(E17:E21)"],     # Row 22 (Total at E23)
                ["", "", "", "", ""],
                
                ["SECTION D — Bulk Order Cost Calculator", ""],          # Row 24
                ["Total Bulk Order Cost ($)", "0"],                      # Row 25
                ["Total Pieces Ordered", "0"],                           # Row 26
                ["Cost Per Piece", "=IF(B26>0, B25/B26, \"\")"],         # Row 27
                ["", ""],
                
                ["SECTION E — Break-even Tracker", ""],                  # Row 29
                ["Startup Cost", "809.32"],                              # Row 30
                ["Profit Recovered So Far", "=B3"],                      # Row 31 (Ref Total Profit)
                ["Remaining To Break Even", "=B30-B31"]                  # Row 32
            ]
            
            # Write data
            sheet.update("A1", data, value_input_option="USER_ENTERED")
            
            # Apply Formatting
            self._format_finance_sheet(sheet)
            
            return {
                'success': True,
                'message': '✅ **FINANCE sheet updated!**\n\n'
                          'Updated sections:\n'
                          ' • Section A: Top Summary (Live data)\n'
                          ' • Section B: Product Breakdown (Aggr data)\n'
                          ' • Section C: Manual Costs (Editable)\n'
                          ' • Section D: Calculator\n'
                          ' • Section E: Break-even'
            }
        except Exception as e:
            self.logger.error(f"Error in init_finance_apply: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed to finance: {str(e)}'}

    def _format_finance_sheet(self, sheet):
        requests = []
        
        # 1. Section Headers (A1, A10, A15, A24, A29) -> Bold, Dark Blue BG, White Text
        section_rows = [0, 9, 14, 23, 28]
        for r in section_rows:
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
                    "fields": "userEnteredFormat(backgroundColor,textFormat,padding)"
                }
            })

        # 2. Section B Table Header (Row 11) -> Bold, Gray BG
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 10, "endRowIndex": 11, "startColumnIndex": 0, "endColumnIndex": 5},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                        "textFormat": {"bold": True},
                        "horizontalAlignment": "CENTER",
                        "borders": {"bottom": {"style": "SOLID", "width": 1}}
                    }
                },
                "fields": "userEnteredFormat"
            }
        })
        
        # 3. Currency Formatting
        # Section A: B2, B3, B5-B8
        # Section B: C12-C13, D12-D13
        # Section C: E17-E21, E23
        # Section D: B25, B27
        # Section E: B30-B32
        
        currency_ranges = [
            # Sec A
            {"startRowIndex": 1, "endRowIndex": 3, "startColumnIndex": 1, "endColumnIndex": 2}, # B2-B3
            {"startRowIndex": 4, "endRowIndex": 8, "startColumnIndex": 1, "endColumnIndex": 2}, # B5-B8
            # Sec B (Revenue, Profit)
            {"startRowIndex": 11, "endRowIndex": 13, "startColumnIndex": 2, "endColumnIndex": 4}, # C12-D13
            # Sec C
            {"startRowIndex": 16, "endRowIndex": 23, "startColumnIndex": 4, "endColumnIndex": 5}, # E17-E23
            # Sec D
            {"startRowIndex": 24, "endRowIndex": 25, "startColumnIndex": 1, "endColumnIndex": 2}, # B25
            {"startRowIndex": 26, "endRowIndex": 27, "startColumnIndex": 1, "endColumnIndex": 2}, # B27
            # Sec E
            {"startRowIndex": 29, "endRowIndex": 32, "startColumnIndex": 1, "endColumnIndex": 2}, # B30-B32
        ]
        
        for rng in currency_ranges:
            requests.append({
                "repeatCell": {
                    "range": dict(sheetId=sheet.id, **rng),
                    "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}},
                    "fields": "userEnteredFormat.numberFormat"
                }
            })
            
        # 4. Percentage Formatting
        # Section A: B4
        # Section B: E12-E13
        pct_ranges = [
            {"startRowIndex": 3, "endRowIndex": 4, "startColumnIndex": 1, "endColumnIndex": 2}, # B4
            {"startRowIndex": 11, "endRowIndex": 13, "startColumnIndex": 4, "endColumnIndex": 5}, # E12-E13
        ]
        for rng in pct_ranges:
            requests.append({
                "repeatCell": {
                    "range": dict(sheetId=sheet.id, **rng),
                    "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}},
                    "fields": "userEnteredFormat.numberFormat"
                }
            })
            
        # 5. Column Widths
        # A=250, B=150, C=120, D=120, E=150
        widths = [250, 150, 120, 120, 150]
        for i, w in enumerate(widths):
            requests.append({
                "updateDimensionProperties": {
                    "range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1},
                    "properties": {"pixelSize": w},
                    "fields": "pixelSize"
                }
            })
            
        # 6. Hide Gridlines
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        sheet.spreadsheet.batch_update({"requests": requests})

def init_finance_apply(sheets_manager) -> Dict[str, Any]:
    agent = SimpleFinanceSync(sheets_manager)
    return agent.init_finance_apply()

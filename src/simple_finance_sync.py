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
            
            # SECTION A (Rows 1-10) - Preserved Layout
            # Row index 0-9
            
            dataset = [
                ["SECTION A — Top Summary", ""],                          # 1
                ["Total Collected (Revenue + Shipping)", "=IFERROR(SUM(ORDERS!H:H) + SUM(ORDERS!I:I), 0)"], # 2
                ["Total Revenue (Items only)", "=IFERROR(SUM(ORDERS!H:H), 0)"], # 3
                ["Total Profit (Net)", "=IFERROR(SUM(ORDERS!K:K), 0)"],  # 4
                ["Total Shipping Label Cost", "=IFERROR(SUM(ORDERS!J:J), 0)"], # 5
                ["Total COGS (Product Costs)", "=SUMPRODUCT(ORDERS!F2:F, ORDERS!E2:E)"], # 6
                ["Total Manual Costs", "=IFERROR(E21, 0)"],              # 7 (Linked to Section C Total)
                ["Net Cash In", "=B2-B6-B7"],                            # 8 (Collected - COGS - Manual)
                ["Avg Profit Margin %", "=IFERROR(B4/B2, 0)"],           # 9
                ["", ""],                                                # 10
                
                # SECTION B (Rows 11-15) - Product Breakdown
                ["SECTION B — Product Breakdown", ""],                   # 11
                ["Product", "Units Sold", "Revenue", "Profit", "Margin %"], # 12
                # Arcus Tee (Row 13)
                ["Arcus Tee", 
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!E:E), 0)", # Units
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!H:H), 0)", # Revenue (Clean sum)
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!K:K), 0)", # Profit
                 "=IFERROR(D13/(C13+SUMIF(ORDERS!C:C, \"*Arcus Tee*\", ORDERS!I:I)), 0)"], # Margin (Profit / Collected)
                # All Paths Tee (Row 14)
                ["All Paths Tee",
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!E:E), 0)",
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!H:H), 0)",
                 "=IFERROR(SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!K:K), 0)",
                 "=IFERROR(D14/(C14+SUMIF(ORDERS!C:C, \"*All Paths Tee*\", ORDERS!I:I)), 0)"],
                ["", ""],                                                # 15
                
                # SECTION C (Rows 16-22) - Manual Costs
                ["SECTION C — Manual Costs", "", "", "", "Amount ($)"],    # 16
                ["Sample Orders", "", "", "", "0"],                       # 17
                ["Bulk Order Total", "", "", "", "0"],                    # 18
                ["Packaging & Supplies", "", "", "", "0"],                # 19
                ["Other Costs", "", "", "", "0"],                         # 20
                ["", "", "", "Total Manual Costs:", "=SUM(E17:E20)"],     # 21
                ["", ""],                                                # 22
                
                # SECTION D (Rows 23+) - Inventory & Break-even
                ["SECTION D — Inventory & Break-even Tools", ""],         # 23
                
                # D1 Inventory
                ["D1) Inventory Tracker", ""],                            # 24
                ["Total Pieces Ordered", "100"],                          # 25 (Manual)
                ["Total Pieces Sold", "=B13+B14"],                        # 26
                ["Remaining Inventory", "=B25-B26"],                      # 27
                
                # D2 Cost Per Piece
                ["D2) Cost Per Piece", ""],                               # 28
                ["Cost Per Piece (Avg)", "=IF(B26>0, B6/B26, 0)"],        # 29 (COGS / Sold)
                ["", ""],                                                # 30
                
                # D4 Break-even (Fixed)
                ["D4) Break-even Analysis (Fixed Prices)", ""],           # 31
                ["Arcus Avg Sell Price", "20"],                           # 32
                ["All Paths Avg Sell Price", "17"],                       # 33
                
                # Unit Profits (Price - Avg Cost from Orders)
                ["Arcus Unit Profit", "=B32 - IFERROR(AVERAGEIF(ORDERS!C:C, \"*Arcus*\", ORDERS!F:F), 0)"], # 34
                ["All Paths Unit Profit", "=B33 - IFERROR(AVERAGEIF(ORDERS!C:C, \"*All Paths*\", ORDERS!F:F), 0)"], # 35
                
                ["Startup Cost (Section E Legacy)", "809.32"],            # 36
                ["Remaining to Break Even ($)", "=B36-B4"],               # 37
                
                ["Units to Break Even (Arcus)", "=IF(B34>0, B37/B34, 0)"], # 38
                ["Units to Break Even (All Paths)", "=IF(B35>0, B37/B35, 0)"], # 39
                
                # Weighted Avg
                ["W. Avg Unit Profit", "=IF(B26>0, (B34*B13 + B35*B14)/B26, 0)"], # 40
                ["Units to Break Even (Mixed)", "=IF(B40>0, B37/B40, 0)"],    # 41
                ["", ""],                                                 # 42
                
                # D5 What-if
                ["D5) What-if Scenario", ""],                             # 43
                ["Scenario Arcus Price", "25"],                           # 44
                ["Scenario All Paths Price", "22"],                       # 45
                
                ["New Arcus Unit Profit", "=B44 - IFERROR(AVERAGEIF(ORDERS!C:C, \"*Arcus*\", ORDERS!F:F), 0)"], # 46
                ["New All Paths Unit Profit", "=B45 - IFERROR(AVERAGEIF(ORDERS!C:C, \"*All Paths*\", ORDERS!F:F), 0)"], # 47
                
                ["Arcus Units Needed", "=IF(B46>0, B37/B46, 0)"],         # 48
                ["All Paths Units Needed", "=IF(B47>0, B37/B47, 0)"],     # 49
                
                ["New W. Avg Profit", "=IF(B26>0, (B46*B13 + B47*B14)/B26, 0)"], # 50
                ["Mixed Units Needed", "=IF(B50>0, B37/B50, 0)"]          # 51
            ]
            
            # Write data
            sheet.update("A1", dataset, value_input_option="USER_ENTERED")
            
            # Apply Formatting
            self._format_finance_sheet(sheet)
            
            return {
                'success': True,
                'message': '✅ **FINANCE sheet updated!**\n'
                          'Sections B, C, D rebuilt. Formatting aligned.'
            }
        except Exception as e:
            self.logger.error(f"Error in init_finance_apply: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed to finance: {str(e)}'}

    def _format_finance_sheet(self, sheet):
        requests = []
        
        # 1. Section Headers (Dark Blue)
        # Rows: 1, 11, 16, 23 (Indices: 0, 10, 15, 22) + Subheaders in D (Indices 23, 27, 30, 42)
        main_headers = [0, 10, 15, 22]
        for r in main_headers:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 5},
                    "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.2, "green": 0.3, "blue": 0.5}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True, "fontSize": 12}, "padding": {"left": 10}}},
                    "fields": "userEnteredFormat"
                }
            })
            
        # Sub-headers in D (Generic Bold, maybe light gray)
        # 24(D1), 28(D2), 31(D4), 43(D5) -> Indices 23, 27, 30, 42
        sub_headers = [23, 27, 30, 42]
        for r in sub_headers:
            requests.append({
                "repeatCell": {
                    "range": {"sheetId": sheet.id, "startRowIndex": r, "endRowIndex": r+1, "startColumnIndex": 0, "endColumnIndex": 5},
                    "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "fontSize": 10, "underline": True}}},
                    "fields": "userEnteredFormat.textFormat"
                }
            })

        # 2. Table Headers (Light Gray)
        # Row 12 (Index 11), Row 16 (Index 15 part), Row 31/43 inputs?
        # Specifically Section B header (Row 12 -> Index 11)
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 11, "endRowIndex": 12, "startColumnIndex": 0, "endColumnIndex": 5},
                "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}, "textFormat": {"bold": True}, "horizontalAlignment": "CENTER"}},
                "fields": "userEnteredFormat"
            }
        })
        
        # Section C Header Row 16 (Index 15) is handled by main headers, but "Amount ($)" is in col 4
        # Let's bold the labels in Section C (Col A) and D (Col A)
        requests.append({
            "repeatCell": {
                "range": {"sheetId": sheet.id, "startRowIndex": 16, "endRowIndex": 51, "startColumnIndex": 0, "endColumnIndex": 1},
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat.textFormat"
            }
        })
            
        # 3. Currency Format ($)
        # Pattern: "$#,##0.00"
        currency_ranges = [
            # Section A
            {"startRowIndex": 1, "endRowIndex": 8, "startColumnIndex": 1, "endColumnIndex": 2}, # B2:B8
            # Section B (Rev, Profit)
            {"startRowIndex": 12, "endRowIndex": 14, "startColumnIndex": 2, "endColumnIndex": 4}, # C13:D14
            # Section C (Amount)
            {"startRowIndex": 16, "endRowIndex": 21, "startColumnIndex": 4, "endColumnIndex": 5}, # E17:E21
            # Section D
            {"startRowIndex": 28, "endRowIndex": 29, "startColumnIndex": 1, "endColumnIndex": 2}, # B29
            {"startRowIndex": 31, "endRowIndex": 37, "startColumnIndex": 1, "endColumnIndex": 2}, # B32:B37 (Prices, Profits, Startup, Remaining)
            {"startRowIndex": 43, "endRowIndex": 47, "startColumnIndex": 1, "endColumnIndex": 2}, # B44:B47
            {"startRowIndex": 49, "endRowIndex": 50, "startColumnIndex": 1, "endColumnIndex": 2}, # B50 (New W Avg)
        ]
        for rng in currency_ranges:
            requests.append({"repeatCell": {"range": dict(sheetId=sheet.id, **rng), "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 4. Percentage Format (%)
        # Pattern: "0.0%" (1 decimal)
        pct_pattern = "0.0%"
        pct_ranges = [
            # Section A
            {"startRowIndex": 8, "endRowIndex": 9, "startColumnIndex": 1, "endColumnIndex": 2}, # B9
            # Section B
            {"startRowIndex": 12, "endRowIndex": 14, "startColumnIndex": 4, "endColumnIndex": 5}, # E13:E14
        ]
        for rng in pct_ranges:
            requests.append({"repeatCell": {"range": dict(sheetId=sheet.id, **rng), "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": pct_pattern}}}, "fields": "userEnteredFormat.numberFormat"}})

        # 5. Borders (Simple Grid for Section B, C, D)
        # We can just apply borders to the whole range of data
        # Section B: 11-14
        # Section C: 16-21
        # Section D: 24-51
        border_ranges = [
            {"startRowIndex": 11, "endRowIndex": 14, "startColumnIndex": 0, "endColumnIndex": 5},
            {"startRowIndex": 16, "endRowIndex": 21, "startColumnIndex": 0, "endColumnIndex": 5}, # E22 is empty
            {"startRowIndex": 24, "endRowIndex": 51, "startColumnIndex": 0, "endColumnIndex": 2}, # D covers A:B primarily
        ]
        
        # Define border style
        border = {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}
        
        for rng in border_ranges:
             requests.append({
                "updateBorders": {
                    "range": dict(sheetId=sheet.id, **rng),
                    "top": border, "bottom": border, "left": border, "right": border, "innerHorizontal": border, "innerVertical": border
                }
            })

        # 6. Column Widths
        widths = [200, 150, 120, 120, 120]
        for i, w in enumerate(widths):
            requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1}, "properties": {"pixelSize": w}, "fields": "pixelSize"}})
            
        requests.append({"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}})
        
        sheet.spreadsheet.batch_update({"requests": requests})

def init_finance_apply(sheets_manager) -> Dict[str, Any]:
    agent = SimpleFinanceSync(sheets_manager)
    return agent.init_finance_apply()

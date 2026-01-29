                    except Exception as e:
                        self.logger.warning(f"Error processing order: {e}")
                        skipped_orders += 1
            
            if not rows:
                return {'success': True, 'message': '⚠️ No line items processed.'}
            
            # Clear existing data (rows 2+)
            try:
                num_existing_rows = len(sheet.get_all_values())
                if num_existing_rows > 1:
                    sheet.batch_clear([f'A2:L{num_existing_rows}'])
            except:
                pass
            
            # Write new data
            sheet.update(f'A2:L{len(rows) + 1}', rows, value_input_option='USER_ENTERED')
            
            # Re-apply formulas
            self._fill_formulas_for_rows(sheet, len(rows))
            
            return {
                'success': True,
                'message': f'✅ **Sync Complete!**\n\n'
                          f'📦 Orders Processed: {orders_count}\n'
                          f'📝 Rows Written: {len(rows)}\n'
                          f'⚡ formatting applied automatically.',
                'data': {'orders': orders_count, 'rows': len(rows)}
            }
            
        except Exception as e:
            self.logger.error(f"Error in sync_orders: {e}", exc_info=True)
            return {'success': False, 'message': f'❌ Failed to sync: {str(e)}'}

    def _extract_size(self, text: str) -> str:
        """Extract size code from text (Small->S, etc)"""
        text = text.lower()
        if 'small' in text or ' sm' in text: return 'S'
        if 'medium' in text or ' med' in text: return 'M'
        if 'large' in text or ' lg' in text: return 'L'
        if 'extra large' in text or 'xl' in text: return 'XL'
        if 'xxl' in text: return 'XXL'
        return ''

    # ============================================
    # FORMATTING HELPERS
    # ============================================
    
    def _apply_header_formatting(self, sheet):
        """Bold, centered, gray bg, borders"""
        requests = [{
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 0, "endRowIndex": 1,
                    "startColumnIndex": 0, "endColumnIndex": len(ORDERS_HEADERS)
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.88, "green": 0.88, "blue": 0.88},
                        "textFormat": {"bold": True, "fontSize": 11},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "borders": {
                            "top": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                            "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                            "left": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}},
                            "right": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0}}
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders)"
            }
        }]
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
    
    def _apply_column_formatting(self, sheet):
        """Currency, Dates, Borders"""
        requests = []
        
        # Apply borders to ALL data cells
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 1, "endRowIndex": FORMULA_ROWS + 1,
                    "startColumnIndex": 0, "endColumnIndex": len(ORDERS_HEADERS)
                },
                "cell": {
                    "userEnteredFormat": {
                        "borders": {
                            "top": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
                            "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
                            "left": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
                            "right": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(borders,horizontalAlignment)"
            }
        })
        
        # Currency columns: Price(E), Revenue(F), Cost(G), Ship(H), Profit(I), Payout(K)
        # 0-based: 4, 5, 6, 7, 8, 10
        for col in [4, 5, 6, 7, 8, 10]:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": 1, "endRowIndex": FORMULA_ROWS + 1,
                        "startColumnIndex": col, "endColumnIndex": col + 1
                    },
                    "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}},
                    "fields": "userEnteredFormat.numberFormat"
                }
            })
            
        # Percentage: J (9)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 1, "endRowIndex": FORMULA_ROWS + 1,
                    "startColumnIndex": 9, "endColumnIndex": 10
                },
                "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}},
                "fields": "userEnteredFormat.numberFormat"
            }
        })
        
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
    
    def _apply_conditional_formatting(self, sheet):
        requests = []
        
        # 1. Product = "Arcus Tee" -> Light Gray
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 0, "endColumnIndex": 12}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "Arcus Tee"}]},
                        "format": {"backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95}}
                    }
                }, "index": 0
            }
        })
        
        # 2. Product = "All Paths Tee" -> Light Purple
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 0, "endColumnIndex": 12}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "All Paths Tee"}]},
                        "format": {"backgroundColor": {"red": 0.95, "green": 0.9, "blue": 1.0}} # Light purple
                    }
                }, "index": 1
            }
        })
        
        # 3. Profit > 0 -> Green (Col I, index 8)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 8, "endColumnIndex": 9}],
                    "booleanRule": {
                        "condition": {"type": "NUMBER_GREATER", "values": [{"userEnteredValue": "0"}]},
                        "format": {
                            "backgroundColor": {"red": 0.85, "green": 0.95, "blue": 0.85},
                            "textFormat": {"foregroundColor": {"red": 0, "green": 0.4, "blue": 0}}
                        }
                    }
                }, "index": 2
            }
        })
        
        # 4. Profit < 0 -> Red (Col I, index 8)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 8, "endColumnIndex": 9}],
                    "booleanRule": {
                        "condition": {"type": "NUMBER_LESS", "values": [{"userEnteredValue": "0"}]},
                        "format": {
                            "backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.9},
                            "textFormat": {"foregroundColor": {"red": 0.8, "green": 0, "blue": 0}}
                        }
                    }
                }, "index": 3
            }
        })
        
        # 5. Fulfillment = "Fulfilled" -> Green (Col L, index 11)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 11, "endColumnIndex": 12}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Fulfilled"}]},
                        "format": {"backgroundColor": {"red": 0.8, "green": 1.0, "blue": 0.8}}
                    }
                }, "index": 4
            }
        })
        
        # 6. Fulfillment = "Unfulfilled" -> Orange (Col L, index 11)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 11, "endColumnIndex": 12}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Unfulfilled"}]},
                        "format": {"backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.8}}
                    }
                }, "index": 5
            }
        })
        
        # 7. S Size -> Light Blue (Col C, index 2)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 2, "endColumnIndex": 3}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "S"}]},
                        "format": {"backgroundColor": {"red": 0.85, "green": 0.92, "blue": 1.0}}
                    }
                }, "index": 6
            }
        })
        
        # 8. M Size -> Light Green (Col C, index 2)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 2, "endColumnIndex": 3}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "M"}]},
                        "format": {"backgroundColor": {"red": 0.85, "green": 1.0, "blue": 0.85}}
                    }
                }, "index": 7
            }
        })
        
        # 9. L Size -> Light Yellow (Col C, index 2)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 2, "endColumnIndex": 3}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "L"}]},
                        "format": {"backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.8}}
                    }
                }, "index": 8
            }
        })
        
        # 10. XL Size -> Light Orange (Col C, index 2)
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet.id, "startRowIndex": 1, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 2, "endColumnIndex": 3}],
                    "booleanRule": {
                        "condition": {"type": "TEXT_CONTAINS", "values": [{"userEnteredValue": "XL"}]},
                        "format": {"backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.8}}
                    }
                }, "index": 9
            }
        })
        
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
    
    def _fill_formulas(self, sheet):
        """Fill formulas for Revenue, Profit, Margin"""
        # Rev = Qty(D)*Price(E) -> F
        # Profit = Rev(F) - (Cost(G)*Qty(D)) - Ship(H) -> I
        # Margin = Profit(I) / Rev(F) -> J
        
        formulas_rev = []
        formulas_prof = []
        formulas_marg = []
        
        for r in range(2, FORMULA_ROWS + 2):
            formulas_rev.append([f'=IFERROR(D{r}*E{r},"")'])
            formulas_prof.append([f'=IFERROR(F{r}-(G{r}*D{r})-H{r},"")'])
            formulas_marg.append([f'=IFERROR(I{r}/F{r},"")'])
        
        sheet.update(f'F2:F{FORMULA_ROWS+1}', formulas_rev, value_input_option='USER_ENTERED')
        sheet.update(f'I2:I{FORMULA_ROWS+1}', formulas_prof, value_input_option='USER_ENTERED')
        sheet.update(f'J2:J{FORMULA_ROWS+1}', formulas_marg, value_input_option='USER_ENTERED')
    
    def _fill_formulas_for_rows(self, sheet, num_rows):
        """Fill formulas for partial rows (optimization)"""
        if num_rows == 0: return
        
        formulas_rev = []
        formulas_prof = []
        formulas_marg = []
        
        for r in range(2, num_rows + 2):
            formulas_rev.append([f'=IFERROR(D{r}*E{r},"")'])
            formulas_prof.append([f'=IFERROR(F{r}-(G{r}*D{r})-H{r},"")'])
            formulas_marg.append([f'=IFERROR(I{r}/F{r},"")'])
            
        sheet.update(f'F2:F{num_rows+1}', formulas_rev, value_input_option='USER_ENTERED')
        sheet.update(f'I2:I{num_rows+1}', formulas_prof, value_input_option='USER_ENTERED')
        sheet.update(f'J2:J{num_rows+1}', formulas_marg, value_input_option='USER_ENTERED')

    def _freeze_and_filter(self, sheet):
        requests = [
            {"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}},
            {"setBasicFilter": {"filter": {"range": {"sheetId": sheet.id, "startRowIndex": 0, "endRowIndex": FORMULA_ROWS, "startColumnIndex": 0, "endColumnIndex": len(ORDERS_HEADERS)}}}}
        ]
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
    
    def _set_column_widths(self, sheet):
        # A:Name(150), B:Prod(200), C:Size(80), D:Qty(50), E:Price(80), F:Rev(80), G:Cost(80), H:Ship(100), I:Prof(80), J:Marg(80), K:Pay(100), L:Stat(100)
        widths = [150, 200, 80, 50, 80, 80, 80, 100, 80, 80, 100, 100]
        requests = []
        for i, w in enumerate(widths):
            requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1}, "properties": {"pixelSize": w}, "fields": "pixelSize"}})
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})
    
    def _hide_gridlines(self, sheet):
        requests = [{"updateSheetProperties": {"properties": {"sheetId": sheet.id, "gridProperties": {"hideGridlines": True}}, "fields": "gridProperties.hideGridlines"}}]
        self.sheets_manager.spreadsheet.batch_update({"requests": requests})

def init_orders_apply(sheets_manager, shopify_client=None, config=None) -> Dict[str, Any]:
    agent = SimpleOrdersSync(sheets_manager, shopify_client, config)
    return agent.init_orders_apply()

def sync_orders(sheets_manager, shopify_client, config=None) -> Dict[str, Any]:
    agent = SimpleOrdersSync(sheets_manager, shopify_client, config)
    return agent.sync_orders()

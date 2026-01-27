"""
Create Setup and Costs sheet for cost tracking
This sheet tracks manufacturing and setup costs with enhanced features
"""
import logging
from sheets_manager import SheetsManager

logger = logging.getLogger(__name__)


def create_setup_costs_sheet(manager: SheetsManager):
    """Create and format the enhanced Setup and Costs sheet"""
    
        logger.info("Creating enhanced COSTS sheet...")
    
    # Create or get the sheet
    try:
        # Use manifest tab name "COSTS"
        sheet = manager.create_sheet_if_not_exists("COSTS")
        
        # Clear existing content
        sheet.clear()
        
        # Define headers - Enhanced with more useful columns
        headers = [
            "Date",           # A - When cost was incurred
            "Category",        # B - Type of cost
            "Description",     # C - What it's for
            "Vendor",          # D - Who you paid
            "Amount ($)",      # E - Base cost
            "Shipping Fee",    # F - Shipping cost
            "Sales Fees",      # G - Platform fees
            "Total Cost",      # H - Auto-calculated total
            "Status",          # I - Paid, Pending, Reimbursed
            "Payment Method",  # J - How it was paid
            "Notes"           # K - Additional details
        ]
        
        # Initial sample data (user can modify)
        from datetime import datetime, timedelta
        today = datetime.now()
        
        sample_data = [
            [today - timedelta(days=30), "Manufacturing", "ths Black Purple/Black Gre", "Manufacturer A", 70.00, 35.00, 6.39, "", "Paid", "Credit Card", "Sample order"],
            [today - timedelta(days=25), "Manufacturing", "odie & Sweatpants Tracks", "Manufacturer B", 215.00, 0.00, 19.63, "", "Paid", "Bank Transfer", ""],
            [today - timedelta(days=20), "Supplies", "100 Poly Zip Bags", "Supplier Co", 50.00, 0.00, 0.00, "", "Paid", "PayPal", "Packaging supplies"],
            [today - timedelta(days=15), "Manufacturing", "Tshirts Bulk Order", "Manufacturer A", 465.00, 95.00, 42.43, "", "Paid", "Credit Card", "Main production run"],
            [today - timedelta(days=10), "Manufacturing", "Additional 6 Tee", "Manufacturer A", 37.50, 8.00, 0.00, "", "Pending", "Credit Card", "Rush order"],
            [today - timedelta(days=5), "Samples", "Test Order", "Manufacturer C", 17.00, 5.99, 0.00, "", "Paid", "PayPal", "Quality check"],
            [today - timedelta(days=2), "Manufacturing", "Hoodie Bulk", "Manufacturer B", 1200.00, 355.00, 0.00, "", "Paid", "Bank Transfer", "Large order"],
            [today - timedelta(days=1), "Samples", "Jacket Sample", "Manufacturer C", 100.00, 0.00, 0.00, "", "Pending", "Credit Card", "New product sample"],
            [today, "Other", "Sample 9 Cost", "Various", 0.00, 0.00, 0.00, "", "Paid", "Cash", "Placeholder"],
        ]
        
        # Prepare all data for batch write
        all_data = [headers]
        
        # Add data rows with formulas for Total Cost (Column H)
        for row_data in sample_data:
            date_val = row_data[0].strftime("%Y-%m-%d") if isinstance(row_data[0], datetime) else row_data[0]
            category = row_data[1]
            description = row_data[2]
            vendor = row_data[3]
            amount = row_data[4]
            shipping = row_data[5]
            sales_fees = row_data[6]
            status = row_data[7] if len(row_data) > 7 else "Paid"
            payment_method = row_data[8] if len(row_data) > 8 else ""
            notes = row_data[9] if len(row_data) > 9 else ""
            
            # Formula for total: =SUM(E{row}:G{row})
            row_num = len(all_data) + 1
            total_formula = f"=SUM(E{row_num}:G{row_num})"
            
            all_data.append([
                date_val, category, description, vendor, amount, shipping, sales_fees,
                total_formula, status, payment_method, notes
            ])
        
        # Add empty row for spacing
        all_data.append([""] * len(headers))
        
        # Add summary section
        last_data_row = len(all_data)  # Before adding summary rows
        summary_start_row = last_data_row + 1
        
        # Summary rows
        summary_rows = [
            ["SUMMARY", "", "", "", "", "", "", "", "", "", ""],  # Header
            ["Total Costs", "", "", "", f"=SUM(E2:E{last_data_row-1})", f"=SUM(F2:F{last_data_row-1})", f"=SUM(G2:G{last_data_row-1})", f"=SUM(H2:H{last_data_row-1})", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", ""],  # Empty row
            ["By Status:", "", "", "", "", "", "", "", "", "", ""],
            ["  Paid", "", "", "", f"=SUMIF(I2:I{last_data_row-1},\"Paid\",E2:E{last_data_row-1})", f"=SUMIF(I2:I{last_data_row-1},\"Paid\",F2:F{last_data_row-1})", f"=SUMIF(I2:I{last_data_row-1},\"Paid\",G2:G{last_data_row-1})", f"=SUMIF(I2:I{last_data_row-1},\"Paid\",H2:H{last_data_row-1})", "", "", ""],
            ["  Pending", "", "", "", f"=SUMIF(I2:I{last_data_row-1},\"Pending\",E2:E{last_data_row-1})", f"=SUMIF(I2:I{last_data_row-1},\"Pending\",F2:F{last_data_row-1})", f"=SUMIF(I2:I{last_data_row-1},\"Pending\",G2:G{last_data_row-1})", f"=SUMIF(I2:I{last_data_row-1},\"Pending\",H2:H{last_data_row-1})", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", ""],  # Empty row
            ["By Category:", "", "", "", "", "", "", "", "", "", ""],
            ["  Manufacturing", "", "", "", f"=SUMIF(B2:B{last_data_row-1},\"Manufacturing\",E2:E{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Manufacturing\",F2:F{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Manufacturing\",G2:G{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Manufacturing\",H2:H{last_data_row-1})", "", "", ""],
            ["  Samples", "", "", "", f"=SUMIF(B2:B{last_data_row-1},\"Samples\",E2:E{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Samples\",F2:F{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Samples\",G2:G{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Samples\",H2:H{last_data_row-1})", "", "", ""],
            ["  Supplies", "", "", "", f"=SUMIF(B2:B{last_data_row-1},\"Supplies\",E2:E{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Supplies\",F2:F{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Supplies\",G2:G{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Supplies\",H2:H{last_data_row-1})", "", "", ""],
            ["  Other", "", "", "", f"=SUMIF(B2:B{last_data_row-1},\"Other\",E2:E{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Other\",F2:F{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Other\",G2:G{last_data_row-1})", f"=SUMIF(B2:B{last_data_row-1},\"Other\",H2:H{last_data_row-1})", "", "", ""],
        ]
        
        all_data.extend(summary_rows)
        
        # Write all data at once
        sheet.update("A1", all_data, value_input_option='USER_ENTERED')
        
        # Format the sheet
        format_setup_costs_sheet(sheet, len(sample_data))
        
        # Add data validation for dropdowns
        add_data_validation(sheet, len(sample_data))
        
        logger.info("✅ Enhanced Setup and Costs sheet created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating Setup and Costs sheet: {e}", exc_info=True)
        raise


def format_setup_costs_sheet(sheet, num_data_rows: int):
    """Format the enhanced Setup and Costs sheet with better organization"""
    
    logger.info("Formatting Setup and Costs sheet...")
    
    # Get sheet ID
    sheet_id = sheet.id
    
    # Calculate ranges
    header_row = 1
    first_data_row = 2
    last_data_row = first_data_row + num_data_rows
    summary_start_row = last_data_row + 2  # After empty row
    
    requests = []
    
    # 1. Format Header Row (Row 1) - Blue background, all columns
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": header_row - 1,
                "endRowIndex": header_row,
                "startColumnIndex": 0,
                "endColumnIndex": 11  # Columns A-K
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.26666666666666666,  # Blue color
                        "green": 0.5843137254901961,
                        "blue": 0.8431372549019608
                    },
                    "textFormat": {
                        "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},  # White text
                        "bold": True,
                        "fontSize": 11
                    },
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE"
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
        }
    })
    
    # 2. Format Data Rows - Currency columns (E, F, G, H)
    for col_idx in [4, 5, 6, 7]:  # Columns E, F, G, H (indices 4, 5, 6, 7)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": first_data_row - 1,
                    "endRowIndex": last_data_row,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "horizontalAlignment": "RIGHT",
                        "verticalAlignment": "MIDDLE",
                        "numberFormat": {
                            "type": "CURRENCY",
                            "pattern": "$#,##0.00"
                        }
                    }
                },
                "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment,numberFormat)"
            }
        })
    
    # 3. Format Total Cost column (H) - Light green background
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": first_data_row - 1,
                "endRowIndex": last_data_row,
                "startColumnIndex": 7,  # Column H (index 7)
                "endColumnIndex": 8
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.85,  # Light green
                        "green": 0.95,
                        "blue": 0.85
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor)"
        }
    })
    
    # 4. Format Date column (A) - Date format
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": first_data_row - 1,
                "endRowIndex": last_data_row,
                "startColumnIndex": 0,  # Column A
                "endColumnIndex": 1
            },
            "cell": {
                "userEnteredFormat": {
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE",
                    "numberFormat": {
                        "type": "DATE",
                        "pattern": "yyyy-mm-dd"
                    }
                }
            },
            "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment,numberFormat)"
        }
    })
    
    # 5. Conditional formatting for Status column (I) - Color code by status
    # Paid = Green, Pending = Yellow, Reimbursed = Blue
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": first_data_row - 1,
                    "endRowIndex": last_data_row,
                    "startColumnIndex": 8,  # Column I (index 8)
                    "endColumnIndex": 9
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_EQ",
                        "values": [{"userEnteredValue": "Paid"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 0.85, "green": 0.95, "blue": 0.85}
                    }
                }
            },
            "index": 0
        }
    })
    
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": first_data_row - 1,
                    "endRowIndex": last_data_row,
                    "startColumnIndex": 8,  # Column I
                    "endColumnIndex": 9
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_EQ",
                        "values": [{"userEnteredValue": "Pending"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8}  # Light yellow
                    }
                }
            },
            "index": 1
        }
    })
    
    # 6. Format Summary Section
    summary_end_row = summary_start_row + 12  # Approximate end of summary
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": summary_start_row - 1,
                "endRowIndex": summary_start_row,
                "startColumnIndex": 0,
                "endColumnIndex": 11
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.4,  # Dark grey
                        "green": 0.4,
                        "blue": 0.4
                    },
                    "textFormat": {
                        "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},  # White text
                        "bold": True,
                        "fontSize": 12
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat)"
        }
    })
    
    # Format summary totals row
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": summary_start_row,
                "endRowIndex": summary_start_row + 1,
                "startColumnIndex": 4,
                "endColumnIndex": 8  # Columns E-H
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.0,  # Bright green
                        "green": 1.0,
                        "blue": 0.5
                    },
                    "textFormat": {
                        "bold": True,
                        "fontSize": 11
                    },
                    "numberFormat": {
                        "type": "CURRENCY",
                        "pattern": "$#,##0.00"
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,numberFormat)"
        }
    })
    
    # 7. Set column widths
    column_widths = {
        0: 100,   # Date
        1: 120,   # Category
        2: 250,   # Description
        3: 150,   # Vendor
        4: 110,   # Amount
        5: 110,   # Shipping
        6: 110,   # Sales Fees
        7: 110,   # Total Cost
        8: 100,   # Status
        9: 120,   # Payment Method
        10: 200   # Notes
    }
    
    for col_idx, width in column_widths.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": col_idx,
                    "endIndex": col_idx + 1
                },
                "properties": {
                    "pixelSize": width
                },
                "fields": "pixelSize"
            }
        })
    
    # 8. Freeze header row
    requests.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {
                    "frozenRowCount": 1
                }
            },
            "fields": "gridProperties.frozenRowCount"
        }
    })
    
    # Execute batch update
    if requests:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("✅ Setup and Costs sheet formatted successfully!")
    else:
        logger.warning("No formatting requests to execute")


def add_data_validation(sheet, num_data_rows: int):
    """Add data validation dropdowns for Category and Status columns"""
    
    sheet_id = sheet.id
    first_data_row = 2
    last_data_row = first_data_row + num_data_rows
    
    requests = []
    
    # Category dropdown (Column B)
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": first_data_row - 1,
                "endRowIndex": last_data_row,
                "startColumnIndex": 1,  # Column B
                "endColumnIndex": 2
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [
                        {"userEnteredValue": "Manufacturing"},
                        {"userEnteredValue": "Samples"},
                        {"userEnteredValue": "Supplies"},
                        {"userEnteredValue": "Shipping"},
                        {"userEnteredValue": "Other"}
                    ]
                },
                "showCustomUi": True,
                "strict": False
            }
        }
    })
    
    # Status dropdown (Column I)
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": first_data_row - 1,
                "endRowIndex": last_data_row,
                "startColumnIndex": 8,  # Column I
                "endColumnIndex": 9
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [
                        {"userEnteredValue": "Paid"},
                        {"userEnteredValue": "Pending"},
                        {"userEnteredValue": "Reimbursed"}
                    ]
                },
                "showCustomUi": True,
                "strict": False
            }
        }
    })
    
    # Payment Method dropdown (Column J)
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": first_data_row - 1,
                "endRowIndex": last_data_row,
                "startColumnIndex": 9,  # Column J
                "endColumnIndex": 10
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [
                        {"userEnteredValue": "Credit Card"},
                        {"userEnteredValue": "Bank Transfer"},
                        {"userEnteredValue": "PayPal"},
                        {"userEnteredValue": "Cash"},
                        {"userEnteredValue": "Check"},
                        {"userEnteredValue": "Other"}
                    ]
                },
                "showCustomUi": True,
                "strict": False
            }
        }
    })
    
    if requests:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("✅ Data validation dropdowns added!")

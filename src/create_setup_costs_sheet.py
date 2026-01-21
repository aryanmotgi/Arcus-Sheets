"""
Create Setup and Costs sheet for cost tracking
This sheet tracks manufacturing and setup costs
"""
import logging
from sheets_manager import SheetsManager

logger = logging.getLogger(__name__)


def create_setup_costs_sheet(manager: SheetsManager):
    """Create and format the Setup and Costs sheet exactly like the sample image"""
    
    logger.info("Creating Setup and Costs sheet...")
    
    # Create or get the sheet
    try:
        sheet = manager.create_sheet_if_not_exists("Setup and Costs")
        
        # Clear existing content
        sheet.clear()
        
        # Define headers
        headers = ["Category", "Amount ($)", "Shipping Fee", "Sales Fees", ""]
        
        # Initial sample data (user can modify)
        sample_data = [
            ["ths Black Purple/Black Gre", 70.00, 35.00, 6.39],
            ["odie & Sweatpants Tracks", 215.00, 0.00, 19.63],
            ["100 Poly Zip Bags", 50.00, 0.00, 0.00],
            ["Tshirts Bulk Order", 465.00, 95.00, 42.43],
            ["Additional 6 Tee", 37.50, 8.00, 0.00],
            ["Test Order", 17.00, 5.99, 0.00],
            ["Hoodie Bulk", 1200.00, 355.00, 0.00],
            ["Jacket Sample", 100.00, 0.00, 0.00],
            ["Sample 9 Cost", 0.00, 0.00, 0.00],
        ]
        
        # Prepare all data for batch write
        all_data = [headers]
        
        # Add data rows with formulas for Total Cost (Column E)
        for row_data in sample_data:
            category = row_data[0]
            amount = row_data[1]
            shipping = row_data[2]
            sales_fees = row_data[3]
            
            # Formula for total: =SUM(B{row}:D{row})
            row_num = len(all_data) + 1
            total_formula = f"=SUM(B{row_num}:D{row_num})"
            
            all_data.append([category, amount, shipping, sales_fees, total_formula])
        
        # Add summary row
        last_data_row = len(all_data) + 1
        summary_row = [
            "TOTAL SAMPLE COSTS",
            f"=SUM(B2:B{last_data_row-1})",
            f"=SUM(C2:C{last_data_row-1})",
            f"=SUM(D2:D{last_data_row-1})",
            f"=SUM(E2:E{last_data_row-1})"
        ]
        all_data.append(summary_row)
        
        # Write all data at once
        sheet.update("A1", all_data, value_input_option='USER_ENTERED')
        
        # Format the sheet
        format_setup_costs_sheet(sheet, len(sample_data))
        
        logger.info("✅ Setup and Costs sheet created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating Setup and Costs sheet: {e}", exc_info=True)
        raise


def format_setup_costs_sheet(sheet, num_data_rows: int):
    """Format the Setup and Costs sheet to match the sample image exactly"""
    
    import gspread
    from google.oauth2.service_account import Credentials
    
    logger.info("Formatting Setup and Costs sheet...")
    
    # Get sheet ID
    sheet_id = sheet.id
    
    # Calculate ranges
    header_row = 1
    first_data_row = 2
    last_data_row = first_data_row + num_data_rows
    summary_row = last_data_row + 1
    
    requests = []
    
    # 1. Format Header Row (Row 1) - Blue background
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": header_row - 1,
                "endRowIndex": header_row,
                "startColumnIndex": 0,
                "endColumnIndex": 5  # Columns A-E
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
                    "horizontalAlignment": "LEFT",
                    "verticalAlignment": "MIDDLE"
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
        }
    })
    
    # 2. Format Data Rows (Rows 2-10) - Light green background for Column E (Total Cost)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": first_data_row - 1,
                "endRowIndex": last_data_row,
                "startColumnIndex": 4,  # Column E (index 4)
                "endColumnIndex": 5
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.85,  # Light green
                        "green": 0.95,
                        "blue": 0.85
                    },
                    "textFormat": {
                        "fontSize": 11
                    },
                    "horizontalAlignment": "RIGHT",
                    "verticalAlignment": "MIDDLE",
                    "numberFormat": {
                        "type": "CURRENCY",
                        "pattern": "$#,##0.00"
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,numberFormat)"
        }
    })
    
    # 3. Format Summary Row (Row 11) - Dark grey background, bold text
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": summary_row - 1,
                "endRowIndex": summary_row,
                "startColumnIndex": 0,
                "endColumnIndex": 5  # Columns A-E
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
                        "fontSize": 11
                    },
                    "horizontalAlignment": "LEFT",
                    "verticalAlignment": "MIDDLE",
                    "numberFormat": {
                        "type": "CURRENCY",
                        "pattern": "$#,##0.00"
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,numberFormat)"
        }
    })
    
    # 4. Special formatting for Column E in Summary Row - Bright green background
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": summary_row - 1,
                "endRowIndex": summary_row,
                "startColumnIndex": 4,  # Column E (index 4)
                "endColumnIndex": 5
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.0,  # Bright green
                        "green": 1.0,
                        "blue": 0.5
                    },
                    "textFormat": {
                        "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0},  # Black text
                        "bold": True,
                        "fontSize": 11
                    },
                    "horizontalAlignment": "RIGHT",
                    "verticalAlignment": "MIDDLE",
                    "numberFormat": {
                        "type": "CURRENCY",
                        "pattern": "$#,##0.00"
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,numberFormat)"
        }
    })
    
    # 5. Format Amount columns (B, C, D) - Currency format, right-aligned
    for col_idx in [1, 2, 3]:  # Columns B, C, D (indices 1, 2, 3)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": first_data_row - 1,
                    "endRowIndex": summary_row,
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
    
    # 6. Format Category column (A) - Left-aligned
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": first_data_row - 1,
                "endRowIndex": summary_row,
                "startColumnIndex": 0,
                "endColumnIndex": 1
            },
            "cell": {
                "userEnteredFormat": {
                    "horizontalAlignment": "LEFT",
                    "verticalAlignment": "MIDDLE",
                    "textFormat": {
                        "fontSize": 11
                    }
                }
            },
            "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment,textFormat)"
        }
    })
    
    # 7. Set column widths
    requests.append({
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "COLUMNS",
                "startIndex": 0,
                "endIndex": 1
            },
            "properties": {
                "pixelSize": 250  # Category column wider
            },
            "fields": "pixelSize"
        }
    })
    
    for col_idx in range(1, 5):  # Columns B-E
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": col_idx,
                    "endIndex": col_idx + 1
                },
                "properties": {
                    "pixelSize": 130  # Money columns
                },
                "fields": "pixelSize"
            }
        })
    
    # Execute batch update
    if requests:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("✅ Setup and Costs sheet formatted successfully!")
    else:
        logger.warning("No formatting requests to execute")

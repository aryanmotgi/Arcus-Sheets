"""
Google Sheets Manager for creating and formatting comprehensive data sheets
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SheetsManager:
    """Manages Google Sheets operations with comprehensive formatting"""
    
    # Define scopes needed for Google Sheets and Drive
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, spreadsheet_id: str, service_account_path: str = None, google_credentials_json: str = None):
        """
        Initialize Google Sheets manager
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            service_account_path: Path to service account JSON file (optional if google_credentials_json provided)
            google_credentials_json: Service account JSON as string (from environment variable)
        """
        import json
        import os
        
        self.logger = logging.getLogger(__name__)
        self.spreadsheet_id = spreadsheet_id
        
        # Try to load credentials from environment variable first
        if google_credentials_json:
            try:
                creds_dict = json.loads(google_credentials_json)
                creds = Credentials.from_service_account_info(
                    creds_dict,
                    scopes=self.SCOPES
                )
                self.logger.info("Using Google credentials from environment variable")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid GOOGLE_CREDENTIALS JSON: {e}")
        # Fall back to file path
        elif service_account_path:
            service_account_path = Path(service_account_path)
            if not service_account_path.exists():
                raise FileNotFoundError(
                    f"Service account file not found: {service_account_path}\n"
                    f"Please download your service account JSON from Google Cloud Console"
                )
            creds = Credentials.from_service_account_file(
                str(service_account_path),
                scopes=self.SCOPES
            )
            self.logger.info(f"Using Google credentials from file: {service_account_path}")
        else:
            raise ValueError(
                "Either service_account_path or google_credentials_json (environment variable) must be provided"
            )
        
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(spreadsheet_id)
        self.logger.info(f"Connected to spreadsheet: {self.spreadsheet.title}")
    
    def get_or_create_spreadsheet(self, title: str = "Arcuswear Store Analytics") -> gspread.Spreadsheet:
        """
        Get existing spreadsheet or create new one
        
        Args:
            title: Spreadsheet title
            
        Returns:
            Spreadsheet object
        """
        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            self.logger.info(f"Opened existing spreadsheet: {spreadsheet.title}")
            return spreadsheet
        except gspread.exceptions.SpreadsheetNotFound:
            # Create new spreadsheet
            spreadsheet = self.client.create(title)
            # Share with service account email (if needed)
            self.logger.info(f"Created new spreadsheet: {spreadsheet.title}")
            return spreadsheet
    
    def create_sheet_if_not_exists(self, sheet_name: str) -> gspread.Worksheet:
        """
        Create sheet if it doesn't exist
        
        Args:
            sheet_name: Name of the sheet
            
        Returns:
            Worksheet object
        """
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            self.logger.info(f"Sheet '{sheet_name}' already exists")
            return sheet
        except gspread.exceptions.WorksheetNotFound:
            sheet = self.spreadsheet.add_worksheet(
                title=sheet_name,
                rows=1000,
                cols=20
            )
            self.logger.info(f"Created new sheet: {sheet_name}")
            return sheet
    
    def write_headers(self, sheet: gspread.Worksheet, headers: List[str]):
        """
        Write headers and apply formatting
        
        Args:
            sheet: Worksheet object
            headers: List of header names
        """
        # Write headers
        sheet.update('A1', [headers])
        
        # Format headers
        requests = [{
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": len(headers)
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.26, "green": 0.52, "blue": 0.96},  # Google blue
                        "textFormat": {
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},  # White
                            "fontSize": 11,
                            "bold": True
                        },
                        "horizontalAlignment": "CENTER",
                        "borders": {
                            "top": {"style": "SOLID", "width": 1},
                            "bottom": {"style": "SOLID", "width": 1},
                            "left": {"style": "SOLID", "width": 1},
                            "right": {"style": "SOLID", "width": 1}
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,borders)"
            }
        }]
        
        # Freeze header row
        requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet.id,
                    "gridProperties": {
                        "frozenRowCount": 1
                    }
                },
                "fields": "gridProperties.frozenRowCount"
            }
        })
        
        # Auto-resize columns
        requests.append({
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet.id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": len(headers)
                }
            }
        })
        
        self.spreadsheet.batch_update({"requests": requests})
    
    def write_dataframe(self, sheet: gspread.Worksheet, df: pd.DataFrame, 
                       clear_existing: bool = False, start_row: int = 2):
        """
        Write DataFrame to sheet
        
        Args:
            sheet: Worksheet object
            df: DataFrame to write
            clear_existing: Whether to clear existing data
            start_row: Row number to start writing (1-indexed, header is row 1)
        """
        if df.empty:
            self.logger.warning("DataFrame is empty, nothing to write")
            return
        
        # Clear existing data if requested
        if clear_existing:
            try:
                # Get all existing data
                all_values = sheet.get_all_values()
                if len(all_values) > 1:  # More than just headers
                    sheet.delete_rows(start_row, len(all_values))
            except:
                pass
        
        # Convert DataFrame to list of lists
        values = df.fillna('').values.tolist()
        
        # Write in chunks to avoid rate limits
        chunk_size = 1000
        for i in range(0, len(values), chunk_size):
            chunk = values[i:i+chunk_size]
            range_name = f'A{start_row + i}'
            sheet.update(range_name, chunk, value_input_option='USER_ENTERED')
            self.logger.debug(f"Wrote {len(chunk)} rows starting at {range_name}")
        
        self.logger.info(f"Wrote {len(values)} rows to sheet '{sheet.title}'")
    
    def format_numbers(self, sheet: gspread.Worksheet, headers: List[str], 
                      currency_cols: List[str] = None, 
                      percent_cols: List[str] = None,
                      date_cols: List[str] = None):
        """
        Apply number formatting to columns
        
        Args:
            sheet: Worksheet object
            headers: List of header names
            currency_cols: List of column names to format as currency
            percent_cols: List of column names to format as percentage
            date_cols: List of column names to format as date
        """
        if currency_cols is None:
            currency_cols = []
        if percent_cols is None:
            percent_cols = []
        if date_cols is None:
            date_cols = []
        
        requests = []
        
        # Currency formatting
        for col_name in currency_cols:
            if col_name in headers:
                col_idx = headers.index(col_name)
                requests.append({
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet.id,
                            "startRowIndex": 1,  # Skip header
                            "startColumnIndex": col_idx,
                            "endColumnIndex": col_idx + 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "numberFormat": {
                                    "type": "CURRENCY",
                                    "pattern": "$#,##0.00"
                                }
                            }
                        },
                        "fields": "userEnteredFormat.numberFormat"
                    }
                })
        
        # Percentage formatting
        for col_name in percent_cols:
            if col_name in headers:
                col_idx = headers.index(col_name)
                requests.append({
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet.id,
                            "startRowIndex": 1,
                            "startColumnIndex": col_idx,
                            "endColumnIndex": col_idx + 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "numberFormat": {
                                    "type": "PERCENT",
                                    "pattern": "0.00%"
                                }
                            }
                        },
                        "fields": "userEnteredFormat.numberFormat"
                    }
                })
        
        # Date formatting
        for col_name in date_cols:
            if col_name in headers:
                col_idx = headers.index(col_name)
                requests.append({
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet.id,
                            "startRowIndex": 1,
                            "startColumnIndex": col_idx,
                            "endColumnIndex": col_idx + 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "numberFormat": {
                                    "type": "DATE",
                                    "pattern": "yyyy-mm-dd"
                                }
                            }
                        },
                        "fields": "userEnteredFormat.numberFormat"
                    }
                })
        
        if requests:
            self.spreadsheet.batch_update({"requests": requests})
    
    def apply_conditional_formatting(self, sheet: gspread.Worksheet, sheet_type: str, headers: List[str]):
        """
        Apply conditional formatting based on sheet type
        
        Args:
            sheet: Worksheet object
            sheet_type: Type of sheet ('financial', 'products', 'orders', 'customers')
            headers: List of header names
        """
        requests = []
        
        if sheet_type == 'financial':
            # Profit/loss indicators
            profit_col = None
            if 'Gross Profit' in headers:
                profit_col = headers.index('Gross Profit')
            elif 'Total Profit' in headers:
                profit_col = headers.index('Total Profit')
            
            if profit_col is not None:
                # Green for positive profit
                requests.append({
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [{
                                "sheetId": sheet.id,
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": profit_col,
                                "endColumnIndex": profit_col + 1
                            }],
                            "booleanRule": {
                                "condition": {
                                    "type": "NUMBER_GREATER",
                                    "values": [{"userEnteredValue": "0"}]
                                },
                                "format": {
                                    "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83}
                                }
                            }
                        },
                        "index": 0
                    }
                })
                
                # Red for negative profit
                requests.append({
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [{
                                "sheetId": sheet.id,
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": profit_col,
                                "endColumnIndex": profit_col + 1
                            }],
                            "booleanRule": {
                                "condition": {
                                    "type": "NUMBER_LESS",
                                    "values": [{"userEnteredValue": "0"}]
                                },
                                "format": {
                                    "backgroundColor": {"red": 0.96, "green": 0.80, "blue": 0.80}
                                }
                            }
                        },
                        "index": 1
                    }
                })
        
        elif sheet_type == 'products':
            # Stock level indicators
            stock_col = None
            if 'Total Stock' in headers:
                stock_col = headers.index('Total Stock')
            elif 'Current Stock (all locations)' in headers:
                stock_col = headers.index('Current Stock (all locations)')
            
            if stock_col is not None:
                # Red for critical stock (< 10)
                requests.append({
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [{
                                "sheetId": sheet.id,
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": stock_col,
                                "endColumnIndex": stock_col + 1
                            }],
                            "booleanRule": {
                                "condition": {
                                    "type": "NUMBER_LESS",
                                    "values": [{"userEnteredValue": "10"}]
                                },
                                "format": {
                                    "backgroundColor": {"red": 0.96, "green": 0.80, "blue": 0.80}
                                }
                            }
                        },
                        "index": 0
                    }
                })
                
                # Yellow for low stock (10-50)
                requests.append({
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [{
                                "sheetId": sheet.id,
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": stock_col,
                                "endColumnIndex": stock_col + 1
                            }],
                            "booleanRule": {
                                "condition": {
                                    "type": "NUMBER_BETWEEN",
                                    "values": [
                                        {"userEnteredValue": "10"},
                                        {"userEnteredValue": "50"}
                                    ]
                                },
                                "format": {
                                    "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8}
                                }
                            }
                        },
                        "index": 1
                    }
                })
        
        elif sheet_type == 'orders':
            # Status color coding
            status_col = None
            if 'Order Status' in headers:
                status_col = headers.index('Order Status')
            elif 'Financial Status' in headers:
                status_col = headers.index('Financial Status')
            
            if status_col is not None:
                # Green for paid/fulfilled
                requests.append({
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [{
                                "sheetId": sheet.id,
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": status_col,
                                "endColumnIndex": status_col + 1
                            }],
                            "booleanRule": {
                                "condition": {
                                    "type": "TEXT_EQ",
                                    "values": [{"userEnteredValue": "paid"}]
                                },
                                "format": {
                                    "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83}
                                }
                            }
                        },
                        "index": 0
                    }
                })
        
        elif sheet_type == 'customers':
            # VIP customer highlighting
            segment_col = None
            if 'Customer Segment' in headers:
                segment_col = headers.index('Customer Segment')
            
            if segment_col is not None:
                requests.append({
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [{
                                "sheetId": sheet.id,
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": segment_col,
                                "endColumnIndex": segment_col + 1
                            }],
                            "booleanRule": {
                                "condition": {
                                    "type": "TEXT_EQ",
                                    "values": [{"userEnteredValue": "VIP"}]
                                },
                                "format": {
                                    "backgroundColor": {"red": 1.0, "green": 0.84, "blue": 0.0},
                                    "textFormat": {"bold": True}
                                }
                            }
                        },
                        "index": 0
                    }
                })
        
        if requests:
            self.spreadsheet.batch_update({"requests": requests})
    
    def apply_zebra_striping(self, sheet: gspread.Worksheet, num_rows: int):
        """
        Apply alternating row colors (zebra striping)
        
        Args:
            sheet: Worksheet object
            num_rows: Number of data rows (excluding header)
        """
        requests = []
        
        # Apply light gray to even rows
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 1,  # Skip header
                    "endRowIndex": min(1 + num_rows, 1000),
                    "startColumnIndex": 0,
                    "endColumnIndex": 100  # Wide range
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.98, "green": 0.98, "blue": 0.98}
                    }
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        })
        
        # Note: Odd rows remain white (default)
        # We could add more sophisticated alternating logic if needed
        
        if requests:
            self.spreadsheet.batch_update({"requests": requests})
    
    def create_financial_dashboard(self, financial_df: pd.DataFrame):
        """
        Create Financial Dashboard sheet
        
        Args:
            financial_df: DataFrame with financial metrics
        """
        self.logger.info("Creating Financial Dashboard sheet...")
        
        sheet = self.create_sheet_if_not_exists("Financial Dashboard")
        
        # Define headers
        headers = [
            'Date', 'Order ID', 'Channel', 'Gross Sales', 'Discounts', 'Returns', 
            'Refunds', 'Taxes', 'Shipping Costs', 'COGS', 'Net Sales', 'Gross Profit', 
            'Profit Margin %', 'Payment Method', 'Transaction Fees', 'Order Status', 
            'Fulfillment Status'
        ]
        
        # Write headers
        self.write_headers(sheet, headers)
        
        # Write data
        if not financial_df.empty:
            # Ensure all columns exist
            for col in headers:
                if col not in financial_df.columns:
                    financial_df[col] = ''
            
            # Reorder columns to match headers
            financial_df = financial_df[headers]
            self.write_dataframe(sheet, financial_df, clear_existing=True)
        
        # Format numbers
        currency_cols = ['Gross Sales', 'Discounts', 'Returns', 'Refunds', 'Taxes', 
                        'Shipping Costs', 'COGS', 'Net Sales', 'Gross Profit', 'Transaction Fees']
        percent_cols = ['Profit Margin %']
        date_cols = ['Date']
        
        self.format_numbers(sheet, headers, currency_cols, percent_cols, date_cols)
        
        # Apply conditional formatting
        self.apply_conditional_formatting(sheet, 'financial', headers)
        
        # Apply zebra striping
        if not financial_df.empty:
            self.apply_zebra_striping(sheet, len(financial_df))
        
        self.logger.info("Financial Dashboard sheet created successfully")
    
    def create_products_sheet(self, products_df: pd.DataFrame):
        """
        Create Products & Inventory sheet
        
        Args:
            products_df: DataFrame with product data
        """
        self.logger.info("Creating Products & Inventory sheet...")
        
        sheet = self.create_sheet_if_not_exists("Products & Inventory")
        
        # Define headers
        headers = [
            'Product ID', 'Variant ID', 'SKU', 'Product Name', 'Variant Title', 
            'Product Type', 'Vendor', 'Category/Tags', 'Price', 'Cost (COGS)', 
            'Current Stock (all locations)', 'Total Stock', 'Location Details', 
            'Last Restock Date', 'Units Sold (30 days)', 'Units Sold (60 days)', 
            'Units Sold (90 days)', 'Revenue (30 days)', 'Revenue (60 days)', 
            'Revenue (90 days)', 'Profit (30 days)', 'Profit (60 days)', 
            'Profit (90 days)', 'Margin %', 'Turnover Rate', 
            'Days of Inventory Remaining', 'Low Stock Alert', 'Status', 
            'Created Date', 'Updated Date'
        ]
        
        # Write headers
        self.write_headers(sheet, headers)
        
        # Write data
        if not products_df.empty:
            # Ensure all columns exist
            for col in headers:
                if col not in products_df.columns:
                    products_df[col] = ''
            
            # Reorder columns to match headers
            products_df = products_df[headers]
            self.write_dataframe(sheet, products_df, clear_existing=True)
        
        # Format numbers
        currency_cols = ['Price', 'Cost (COGS)', 'Revenue (30 days)', 'Revenue (60 days)', 
                        'Revenue (90 days)', 'Profit (30 days)', 'Profit (60 days)', 'Profit (90 days)']
        percent_cols = ['Margin %', 'Turnover Rate']
        date_cols = ['Last Restock Date', 'Created Date', 'Updated Date']
        
        self.format_numbers(sheet, headers, currency_cols, percent_cols, date_cols)
        
        # Apply conditional formatting
        self.apply_conditional_formatting(sheet, 'products', headers)
        
        # Apply zebra striping
        if not products_df.empty:
            self.apply_zebra_striping(sheet, len(products_df))
        
        self.logger.info("Products & Inventory sheet created successfully")
    
    def create_orders_sheet(self, orders_df: pd.DataFrame):
        """
        Create Orders Detail sheet
        
        Args:
            orders_df: DataFrame with order line items
        """
        self.logger.info("Creating Orders Detail sheet...")
        
        sheet = self.create_sheet_if_not_exists("Orders Detail")
        
        # Define headers
        headers = [
            'Order ID', 'Order Number', 'Date', 'Time', 'Customer ID', 'Customer Name', 
            'Customer Email', 'Billing Address', 'Shipping Address', 'Order Status', 
            'Financial Status', 'Fulfillment Status', 'Payment Method', 'Gateway', 
            'Line Item ID', 'Product ID', 'Variant ID', 'SKU', 'Product Name', 
            'Variant Title', 'Quantity', 'Unit Price', 'Line Total', 'Discount Amount', 
            'Tax Amount', 'Shipping Cost', 'Order Subtotal', 'Order Total', 'Currency', 
            'Channel', 'Source', 'Tags', 'Notes', 'Shipping Method', 'Tracking Number', 
            'Fulfillment Date'
        ]
        
        # Write headers
        self.write_headers(sheet, headers)
        
        # Write data
        if not orders_df.empty:
            # Ensure all columns exist
            for col in headers:
                if col not in orders_df.columns:
                    orders_df[col] = ''
            
            # Reorder columns to match headers
            orders_df = orders_df[headers]
            self.write_dataframe(sheet, orders_df, clear_existing=True)
        
        # Format numbers
        currency_cols = ['Unit Price', 'Line Total', 'Discount Amount', 'Tax Amount', 
                        'Shipping Cost', 'Order Subtotal', 'Order Total']
        date_cols = ['Date', 'Fulfillment Date']
        
        self.format_numbers(sheet, headers, currency_cols, None, date_cols)
        
        # Apply conditional formatting
        self.apply_conditional_formatting(sheet, 'orders', headers)
        
        # Apply zebra striping
        if not orders_df.empty:
            self.apply_zebra_striping(sheet, len(orders_df))
        
        self.logger.info("Orders Detail sheet created successfully")
    
    def create_customers_sheet(self, customers_df: pd.DataFrame):
        """
        Create Customer Analytics sheet
        
        Args:
            customers_df: DataFrame with customer data
        """
        self.logger.info("Creating Customer Analytics sheet...")
        
        sheet = self.create_sheet_if_not_exists("Customer Analytics")
        
        # Define headers
        headers = [
            'Customer ID', 'First Name', 'Last Name', 'Full Name', 'Email', 'Phone', 
            'Address', 'City', 'State', 'Country', 'ZIP', 'Customer Tags', 
            'Accepts Marketing', 'First Purchase Date', 'Last Purchase Date', 
            'Total Orders', 'Total Spent (Lifetime Value)', 'Average Order Value', 
            'Largest Order Value', 'Favorite Product Category', 'Favorite Product', 
            'Customer Segment', 'Days Since Last Purchase', 'Total Items Purchased', 
            'Average Items Per Order', 'Preferred Payment Method', 
            'Preferred Shipping Method', 'Account Status'
        ]
        
        # Write headers
        self.write_headers(sheet, headers)
        
        # Write data
        if not customers_df.empty:
            # Ensure all columns exist
            for col in headers:
                if col not in customers_df.columns:
                    customers_df[col] = ''
            
            # Reorder columns to match headers
            customers_df = customers_df[headers]
            self.write_dataframe(sheet, customers_df, clear_existing=True)
        
        # Format numbers
        currency_cols = ['Total Spent (Lifetime Value)', 'Average Order Value', 'Largest Order Value']
        date_cols = ['First Purchase Date', 'Last Purchase Date']
        
        self.format_numbers(sheet, headers, currency_cols, None, date_cols)
        
        # Apply conditional formatting
        self.apply_conditional_formatting(sheet, 'customers', headers)
        
        # Apply zebra striping
        if not customers_df.empty:
            self.apply_zebra_striping(sheet, len(customers_df))
        
        self.logger.info("Customer Analytics sheet created successfully")
    
    def sync_all_data(self, orders_df: pd.DataFrame, products_df: pd.DataFrame, 
                     customers_df: pd.DataFrame, financial_df: pd.DataFrame):
        """
        Sync all data to sheets
        
        Args:
            orders_df: Processed orders DataFrame
            products_df: Processed products DataFrame
            customers_df: Processed customers DataFrame
            financial_df: Financial metrics DataFrame
            
        Returns:
            Dictionary with success status for each sheet
        """
        results = {}
        
        try:
            self.create_financial_dashboard(financial_df)
            results['Financial Dashboard'] = True
        except Exception as e:
            self.logger.error(f"Failed to create Financial Dashboard: {e}")
            results['Financial Dashboard'] = False
        
        try:
            self.create_products_sheet(products_df)
            results['Products & Inventory'] = True
        except Exception as e:
            self.logger.error(f"Failed to create Products & Inventory: {e}")
            results['Products & Inventory'] = False
        
        try:
            self.create_orders_sheet(orders_df)
            results['Orders Detail'] = True
        except Exception as e:
            self.logger.error(f"Failed to create Orders Detail: {e}")
            results['Orders Detail'] = False
        
        try:
            self.create_customers_sheet(customers_df)
            results['Customer Analytics'] = True
        except Exception as e:
            self.logger.error(f"Failed to create Customer Analytics: {e}")
            results['Customer Analytics'] = False
        
        return results


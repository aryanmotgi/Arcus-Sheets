"""
Google Sheets Manager for creating and formatting comprehensive data sheets
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional, Tuple
import pandas as pd
from pathlib import Path
import logging
import time
import random
from functools import wraps

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
        
        # Rate limiting and caching
        self._sheet_metadata_cache = {}  # {sheet_name: {id, title, grid_properties}}
        self._headers_cache = {}  # {sheet_name: (headers_list, column_index_map)}
        self._last_api_call_time = 0
        self._min_call_interval = 0.15  # 150ms default throttle
        self._api_call_count = {'reads': 0, 'writes': 0, 'batches': 0}
    
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
    
    def hide_sheet(self, sheet_name: str):
        """Hide a sheet from view"""
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            sheet_id = sheet.id
            requests = [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "hidden": True
                    },
                    "fields": "hidden"
                }
            }]
            self.spreadsheet.batch_update({"requests": requests})
            self.logger.info(f"Hidden sheet: {sheet_name}")
        except gspread.exceptions.WorksheetNotFound:
            self.logger.warning(f"Sheet '{sheet_name}' not found, cannot hide")
    
    def show_sheet(self, sheet_name: str):
        """Show a hidden sheet"""
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            sheet_id = sheet.id
            requests = [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "hidden": False
                    },
                    "fields": "hidden"
                }
            }]
            self.spreadsheet.batch_update({"requests": requests})
            self.logger.info(f"Shown sheet: {sheet_name}")
        except gspread.exceptions.WorksheetNotFound:
            self.logger.warning(f"Sheet '{sheet_name}' not found, cannot show")
    
    def freeze_header_row(self, sheet_name: str, num_rows: int = 1):
        """Freeze header rows"""
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            sheet_id = sheet.id
            requests = [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {
                            "frozenRowCount": num_rows
                        }
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            }]
            self.spreadsheet.batch_update({"requests": requests})
            self.logger.info(f"Froze {num_rows} row(s) in sheet: {sheet_name}")
        except gspread.exceptions.WorksheetNotFound:
            self.logger.warning(f"Sheet '{sheet_name}' not found")
    
    def clear_gridlines(self, sheet_name: str):
        """Clear gridlines on a sheet (makes it look cleaner)"""
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            sheet_id = sheet.id
            requests = [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {
                            "hideGridlines": True
                        }
                    },
                    "fields": "gridProperties.hideGridlines"
                }
            }]
            self.spreadsheet.batch_update({"requests": requests})
            self.logger.info(f"Cleared gridlines on sheet: {sheet_name}")
        except gspread.exceptions.WorksheetNotFound:
            self.logger.warning(f"Sheet '{sheet_name}' not found")
    
    def insert_image(self, sheet_name: str, url: str, cell: str, width: int = 200, height: int = 100):
        """
        Insert an image into a sheet cell
        Note: Google Sheets API doesn't directly support images, but we can use IMAGE() formula
        """
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            image_formula = f'=IMAGE("{url}", 1, {width}, {height})'
            sheet.update(cell, image_formula, value_input_option='USER_ENTERED')
            self.logger.info(f"Inserted image at {cell} in sheet: {sheet_name}")
        except Exception as e:
            self.logger.error(f"Error inserting image: {e}")
    
    def create_manual_overrides_sheet(self):
        """Create MANUAL_OVERRIDES sheet structure"""
        sheet = self.create_sheet_if_not_exists("MANUAL_OVERRIDES")
        
        headers = ["order_id", "order_number", "psl", "shipping_label_cost", "notes", "updated_at", "updated_by"]
        self.write_headers(sheet, headers)
        
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
                        "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
                        "textFormat": {
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                            "bold": True,
                            "fontSize": 11
                        }
                    }
                },
                "fields": "userEnteredFormat"
            }
        }]
        
        # Set column widths
        column_widths = {
            0: 120,  # order_id
            1: 120,  # order_number
            2: 150,  # psl
            3: 140,  # shipping_label_cost
            4: 300,  # notes
            5: 150,  # updated_at
            6: 120   # updated_by
        }
        
        for col_idx, width in column_widths.items():
            requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": col_idx,
                        "endIndex": col_idx + 1
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize"
                }
            })
        
        self.spreadsheet.batch_update({"requests": requests})
        self.freeze_header_row("MANUAL_OVERRIDES")
        self.logger.info("Created MANUAL_OVERRIDES sheet")
        return sheet
    
    def upsert_manual_override(self, order_id: str, order_number: str = None, 
                               psl: str = None, shipping_label_cost: float = None, 
                               notes: str = None, updated_by: str = "system"):
        """
        Upsert a row in MANUAL_OVERRIDES
        Returns: (row_number, is_new)
        """
        from datetime import datetime
        
        sheet = self.create_sheet_if_not_exists("MANUAL_OVERRIDES")
        all_data = sheet.get_all_values()
        
        # Find existing row by order_id
        existing_row = None
        for idx, row in enumerate(all_data[1:], start=2):  # Skip header
            if len(row) > 0 and row[0] == str(order_id):
                existing_row = idx
                break
        
        # Prepare data
        now = datetime.now().isoformat()
        row_data = [
            str(order_id),
            order_number or "",
            psl or "",
            shipping_label_cost if shipping_label_cost is not None else "",
            notes or "",
            now,
            updated_by
        ]
        
        if existing_row:
            # Update existing row
            sheet.update(f"A{existing_row}:G{existing_row}", [row_data])
            self.logger.info(f"Updated MANUAL_OVERRIDES row {existing_row} for order_id {order_id}")
            return existing_row, False
        else:
            # Append new row
            sheet.append_row(row_data)
            self.logger.info(f"Added new MANUAL_OVERRIDES row for order_id {order_id}")
            return len(all_data) + 1, True
    
    def get_manual_override(self, order_id: str = None, order_number: str = None):
        """Get manual override data for an order"""
        sheet = self.create_sheet_if_not_exists("MANUAL_OVERRIDES")
        all_data = sheet.get_all_values()
        
        if not all_data or len(all_data) < 2:
            return None
        
        # Find by order_id or order_number
        for row in all_data[1:]:  # Skip header
            if len(row) >= 2:
                if order_id and row[0] == str(order_id):
                    return {
                        "order_id": row[0],
                        "order_number": row[1] if len(row) > 1 else "",
                        "psl": row[2] if len(row) > 2 else "",
                        "shipping_label_cost": float(row[3]) if len(row) > 3 and row[3] else None,
                        "notes": row[4] if len(row) > 4 else "",
                        "updated_at": row[5] if len(row) > 5 else "",
                        "updated_by": row[6] if len(row) > 6 else ""
                    }
                if order_number and len(row) > 1 and row[1] == str(order_number):
                    return {
                        "order_id": row[0],
                        "order_number": row[1],
                        "psl": row[2] if len(row) > 2 else "",
                        "shipping_label_cost": float(row[3]) if len(row) > 3 and row[3] else None,
                        "notes": row[4] if len(row) > 4 else "",
                        "updated_at": row[5] if len(row) > 5 else "",
                        "updated_by": row[6] if len(row) > 6 else ""
                    }
        
        return None
    
    def get_all_manual_overrides(self):
        """Get all manual overrides as a list of dicts"""
        sheet = self.create_sheet_if_not_exists("MANUAL_OVERRIDES")
        all_data = sheet.get_all_values()
        
        if not all_data or len(all_data) < 2:
            return []
        
        headers = all_data[0]
        results = []
        
        for row in all_data[1:]:
            if len(row) > 0 and row[0]:  # Has order_id
                override = {}
                for idx, header in enumerate(headers):
                    override[header] = row[idx] if idx < len(row) else ""
                # Convert shipping_label_cost to float if present
                if "shipping_label_cost" in override and override["shipping_label_cost"]:
                    try:
                        override["shipping_label_cost"] = float(override["shipping_label_cost"])
                    except:
                        override["shipping_label_cost"] = None
                results.append(override)
        
        return results
    
    def create_metrics_sheet(self):
        """Create METRICS sheet structure - single source of truth for all KPIs"""
        sheet = self.create_sheet_if_not_exists("METRICS")
        
        headers = ["metric_key", "label", "value", "updated_at"]
        self.write_headers(sheet, headers)
        
        # Initialize required metrics if sheet is empty
        all_data = sheet.get_all_values()
        if not all_data or len(all_data) < 2:
            required_metrics = [
                ["total_revenue", "Total Revenue", "0", ""],
                ["total_units", "Total Units Sold", "0", ""],
                ["total_cogs", "Total COGS", "0", ""],
                ["total_shipping_label_cost", "Total Shipping Label Cost", "0", ""],
                ["gross_profit", "Gross Profit", "0", ""],
                ["contribution_profit", "Contribution Profit", "0", ""],
                ["setup_costs", "Setup Costs", "809.32", ""],
                ["net_profit_after_setup", "Net Profit After Setup", "0", ""],
                ["unfulfilled_count", "Unfulfilled Orders", "0", ""],
                ["missing_label_cost_count", "Missing Label Cost", "0", ""],
            ]
            sheet.update('A2', required_metrics)
        
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
                        "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
                        "textFormat": {
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                            "bold": True,
                            "fontSize": 11
                        }
                    }
                },
                "fields": "userEnteredFormat"
            }
        }]
        
        # Set column widths
        column_widths = {
            0: 200,  # metric_key
            1: 200,  # label
            2: 150,  # value
            3: 180   # updated_at
        }
        
        for col_idx, width in column_widths.items():
            requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": col_idx,
                        "endIndex": col_idx + 1
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize"
                }
            })
        
        self.spreadsheet.batch_update({"requests": requests})
        self.freeze_header_row("METRICS")
        self.logger.info("Created/verified METRICS sheet")
        return sheet
    
    def get_metric(self, metric_key: str):
        """Get metric value by key"""
        sheet = self.create_sheet_if_not_exists("METRICS")
        all_data = sheet.get_all_values()
        
        if not all_data or len(all_data) < 2:
            return None
        
        headers = all_data[0]
        try:
            key_col_idx = headers.index("metric_key")
            value_col_idx = headers.index("value")
        except ValueError:
            return None
        
        for row in all_data[1:]:
            if len(row) > key_col_idx and row[key_col_idx] == metric_key:
                if len(row) > value_col_idx:
                    value = row[value_col_idx]
                    try:
                        return float(value)
                    except:
                        return value
                return None
        
        return None
    
    def set_metric(self, metric_key: str, value, label: str = None):
        """Set metric value by key (upsert)"""
        from datetime import datetime
        
        sheet = self.create_sheet_if_not_exists("METRICS")
        all_data = sheet.get_all_values()
        
        if not all_data:
            all_data = [["metric_key", "label", "value", "updated_at"]]
        
        headers = all_data[0]
        try:
            key_col_idx = headers.index("metric_key")
            label_col_idx = headers.index("label")
            value_col_idx = headers.index("value")
            updated_col_idx = headers.index("updated_at")
        except ValueError:
            self.logger.error("METRICS sheet missing required columns")
            return False
        
        # Find existing row
        existing_row = None
        for idx, row in enumerate(all_data[1:], start=2):
            if len(row) > key_col_idx and row[key_col_idx] == metric_key:
                existing_row = idx
                break
        
        now = datetime.now().isoformat()
        value_str = str(value) if value is not None else "0"
        
        if existing_row:
            # Update existing row
            row_data = [""] * len(headers)
            row_data[key_col_idx] = metric_key
            row_data[label_col_idx] = label or metric_key.replace("_", " ").title()
            row_data[value_col_idx] = value_str
            row_data[updated_col_idx] = now
            
            # Ensure row has enough columns
            while len(row_data) < len(headers):
                row_data.append("")
            
            sheet.update(f"A{existing_row}:D{existing_row}", [row_data[:4]])
            self.logger.info(f"Updated metric {metric_key} = {value_str}")
        else:
            # Append new row
            row_data = [
                metric_key,
                label or metric_key.replace("_", " ").title(),
                value_str,
                now
            ]
            sheet.append_row(row_data)
            self.logger.info(f"Added new metric {metric_key} = {value_str}")
        
        return True
    
    def get_all_metrics(self):
        """Get all metrics as a dict"""
        sheet = self.create_sheet_if_not_exists("METRICS")
        all_data = sheet.get_all_values()
        
        if not all_data or len(all_data) < 2:
            return {}
        
        headers = all_data[0]
        try:
            key_col_idx = headers.index("metric_key")
            value_col_idx = headers.index("value")
        except ValueError:
            return {}
        
        metrics = {}
        for row in all_data[1:]:
            if len(row) > key_col_idx and row[key_col_idx]:
                key = row[key_col_idx]
                value = row[value_col_idx] if len(row) > value_col_idx else "0"
                try:
                    metrics[key] = float(value)
                except:
                    metrics[key] = value
        
        return metrics
    
    # ==================== RATE LIMIT SAFE WRAPPERS ====================
    
    def _throttle(self):
        """Throttle API calls to avoid rate limits"""
        now = time.time()
        time_since_last_call = now - self._last_api_call_time
        if time_since_last_call < self._min_call_interval:
            sleep_time = self._min_call_interval - time_since_last_call
            time.sleep(sleep_time)
        self._last_api_call_time = time.time()
    
    def _retry_with_backoff(self, func, max_retries=5, *args, **kwargs):
        """
        Retry function with exponential backoff for 429/RESOURCE_EXHAUSTED errors
        """
        for attempt in range(max_retries):
            try:
                self._throttle()
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = (
                    '429' in error_str or 
                    'rate_limit' in error_str or 
                    'resource_exhausted' in error_str or
                    'quota' in error_str
                )
                
                if is_rate_limit and attempt < max_retries - 1:
                    # Exponential backoff: 0.5s, 1s, 2s, 4s, 8s + jitter
                    backoff_time = (0.5 * (2 ** attempt)) + random.uniform(0, 0.1)
                    self.logger.warning(
                        f"Rate limit hit (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {backoff_time:.2f}s..."
                    )
                    time.sleep(backoff_time)
                    continue
                else:
                    # Not a rate limit error, or max retries reached
                    raise
    
    def batch_get_values(self, sheet_name: str, ranges: List[str]) -> Dict[str, List[List]]:
        """
        Batch get values for multiple ranges in one API call
        
        Args:
            sheet_name: Name of the sheet
            ranges: List of A1 notation ranges (e.g., ['A1:B10', 'D1:D20'])
        
        Returns:
            Dict mapping range to values: {'A1:B10': [[...]], 'D1:D20': [[...]]}
        """
        try:
            sheet = self.create_sheet_if_not_exists(sheet_name)
            
            def _batch_get():
                result = self.client.batch_get(
                    self.spreadsheet_id,
                    ranges=[f"{sheet_name}!{r}" for r in ranges]
                )
                self._api_call_count['batches'] += 1
                return result
            
            result = self._retry_with_backoff(_batch_get)
            
            # Map results back to original ranges
            output = {}
            for i, range_str in enumerate(ranges):
                if i < len(result):
                    output[range_str] = result[i]
                else:
                    output[range_str] = []
            
            return output
        except Exception as e:
            self.logger.error(f"Error in batch_get_values: {e}")
            # Fallback to individual gets
            output = {}
            for r in ranges:
                try:
                    values = sheet.get_values(r)
                    output[r] = values if values else []
                except:
                    output[r] = []
            return output
    
    def batch_update_values(self, sheet_name: str, updates: List[Dict]) -> bool:
        """
        Batch update multiple ranges in one API call
        
        Args:
            sheet_name: Name of the sheet
            updates: List of dicts with 'range' and 'values' keys
                    [{'range': 'A1:B10', 'values': [[...]]}, ...]
        
        Returns:
            True if successful
        """
        try:
            sheet = self.create_sheet_if_not_exists(sheet_name)
            
            # Prepare batch update request
            data = []
            for update in updates:
                range_str = f"{sheet_name}!{update['range']}"
                data.append({
                    'range': range_str,
                    'values': update['values']
                })
            
            def _batch_update():
                self.client.batch_update(
                    self.spreadsheet_id,
                    data,
                    value_input_option='USER_ENTERED'
                )
                self._api_call_count['batches'] += 1
                self._api_call_count['writes'] += len(updates)
            
            self._retry_with_backoff(_batch_update)
            return True
        except Exception as e:
            self.logger.error(f"Error in batch_update_values: {e}")
            return False
    
    def get_sheet_metadata_cached(self, sheet_name: str) -> Dict:
        """
        Get sheet metadata (id, title, grid_properties) with caching
        
        Cache persists for the duration of the SheetsManager instance
        """
        if sheet_name in self._sheet_metadata_cache:
            return self._sheet_metadata_cache[sheet_name]
        
        try:
            sheet = self.create_sheet_if_not_exists(sheet_name)
            
            def _get_metadata():
                # Get sheet properties via batch_get_sheet_metadata
                metadata = self.spreadsheet.batch_get_sheet_metadata()
                self._api_call_count['reads'] += 1
                return metadata
            
            metadata_list = self._retry_with_backoff(_get_metadata)
            
            # Find our sheet
            for sheet_meta in metadata_list:
                if sheet_meta.get('properties', {}).get('title') == sheet_name:
                    props = sheet_meta.get('properties', {})
                    cached = {
                        'id': props.get('sheetId'),
                        'title': props.get('title'),
                        'grid_properties': props.get('gridProperties', {})
                    }
                    self._sheet_metadata_cache[sheet_name] = cached
                    return cached
            
            # Fallback
            cached = {
                'id': sheet.id,
                'title': sheet_name,
                'grid_properties': {}
            }
            self._sheet_metadata_cache[sheet_name] = cached
            return cached
        except Exception as e:
            self.logger.warning(f"Error getting sheet metadata: {e}, using fallback")
            sheet = self.create_sheet_if_not_exists(sheet_name)
            cached = {
                'id': sheet.id,
                'title': sheet_name,
                'grid_properties': {}
            }
            self._sheet_metadata_cache[sheet_name] = cached
            return cached
    
    def get_headers_cached(self, sheet_name: str) -> Tuple[List[str], Dict[str, int]]:
        """
        Get headers and column index mapping with caching
        
        Returns:
            (headers_list, column_index_map) where column_index_map maps header_name -> column_index
        """
        if sheet_name in self._headers_cache:
            return self._headers_cache[sheet_name]
        
        try:
            sheet = self.create_sheet_if_not_exists(sheet_name)
            
            def _get_headers():
                values = sheet.get_values('1:1')  # Get first row only
                self._api_call_count['reads'] += 1
                return values[0] if values else []
            
            headers = self._retry_with_backoff(_get_headers)
            
            # Build column index map
            column_map = {header: idx for idx, header in enumerate(headers) if header}
            
            result = (headers, column_map)
            self._headers_cache[sheet_name] = result
            return result
        except Exception as e:
            self.logger.warning(f"Error getting headers: {e}")
            return ([], {})
    
    def clear_cache(self):
        """Clear all caches (useful after major sheet changes)"""
        self._sheet_metadata_cache.clear()
        self._headers_cache.clear()
        self.logger.info("Cleared sheet metadata and headers cache")
    
    def get_api_call_summary(self) -> Dict[str, int]:
        """Get summary of API calls made"""
        return self._api_call_count.copy()
    
    def reset_api_call_count(self):
        """Reset API call counter"""
        self._api_call_count = {'reads': 0, 'writes': 0, 'batches': 0}


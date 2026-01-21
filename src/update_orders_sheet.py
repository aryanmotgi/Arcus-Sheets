"""
Script to update Orders sheet: remove Total Price, add black borders, fix formatting
"""
import yaml
import logging
from pathlib import Path
import pandas as pd
from sheets_manager import SheetsManager
from shopify_client import ShopifyClient
from data_processor import DataProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from environment variables or config.yaml"""
    import os
    
    # Try to load from environment variables first
    config = {}
    
    # Shopify config from env
    if os.getenv('SHOPIFY_STORE_URL'):
        config['shopify'] = {
            'store_url': os.getenv('SHOPIFY_STORE_URL'),
            'client_id': os.getenv('SHOPIFY_CLIENT_ID', ''),
            'client_secret': os.getenv('SHOPIFY_CLIENT_SECRET', '')
        }
    
    # Google Sheets config from env
    if os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'):
        config['google_sheets'] = {
            'spreadsheet_id': os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'),
            'service_account_path': os.getenv('GOOGLE_CREDENTIALS')  # Will be handled differently
        }
    
    # If we have env vars, return config
    if config.get('shopify') and config.get('google_sheets'):
        return config
    
    # Fall back to config.yaml file
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            file_config = yaml.safe_load(f)
            if file_config:
                return file_config
    
    # If neither exists, raise error
    raise ValueError(
        "Configuration not found! Please set environment variables:\n"
        "- SHOPIFY_STORE_URL\n"
        "- SHOPIFY_CLIENT_ID\n"
        "- SHOPIFY_CLIENT_SECRET\n"
        "- GOOGLE_SHEETS_SPREADSHEET_ID\n"
        "- GOOGLE_CREDENTIALS"
    )


def update_orders_sheet():
    """Update Orders sheet with proper formatting"""
    logger.info("=" * 60)
    logger.info("Updating Orders sheet...")
    logger.info("=" * 60)
    
    config = load_config()
    
    # Initialize clients
    shopify_config = config.get('shopify', {})
    if not shopify_config.get('store_url'):
        raise ValueError("Shopify store URL not found in configuration")
    if not shopify_config.get('client_id') or not shopify_config.get('client_secret'):
        raise ValueError("Shopify client_id or client_secret not found in configuration")
    
    shopify = ShopifyClient(
        store_url=shopify_config['store_url'],
        client_id=shopify_config['client_id'],
        client_secret=shopify_config['client_secret']
    )
    
    # Initialize sheets manager - support both file path and env var
    import os
    google_credentials_json = os.getenv('GOOGLE_CREDENTIALS')
    service_account_path = config['google_sheets'].get('service_account_path')
    
    manager = SheetsManager(
        spreadsheet_id=config['google_sheets']['spreadsheet_id'],
        service_account_path=service_account_path if not google_credentials_json else None,
        google_credentials_json=google_credentials_json
    )
    
    # Initialize data processor
    processor = DataProcessor()
    
    try:
        # Fetch ALL orders from Shopify (no filters - get everything)
        logger.info("Fetching ALL orders from Shopify (fresh data)...")
        orders = shopify.get_orders(
            limit=250,  # Max per page
            status='any',  # Get all statuses
            created_at_min=None,  # No date filter - get everything
            since_id=None  # No ID filter - get everything
        )
        logger.info(f"✅ Fetched {len(orders)} orders from Shopify")
        
        # Process orders
        orders_df = processor.process_orders(orders)
        orders_df = processor.clean_data(orders_df)
        
        # Get or create Orders sheet
        sheet = manager.create_sheet_if_not_exists("Orders")
        
        # Clear existing data
        try:
            sheet.clear()
        except:
            pass
        
        # Headers with new columns
        headers = [
            'Customer Name',
            'Product Name',
            'Size',
            'Quantity',
            'Sold Price',
            'Shipping Cost',
            'PSL',  # Private Shipping Label - User can input custom numbers here - will be preserved
            'Unit Cost',
            'Profit',
            'Profit Margin %',
            'Date',
            'Order Status',
            'Shipping Status'
        ]
        
        # Start from column A
        start_col = 1  # Column A
        
        # CRITICAL: Read existing PSL values BEFORE writing headers or any data
        # Use individual cell reads as a more reliable method
        existing_psl_values_by_row = {}  # Map sheet_row_number -> PSL value
        existing_psl_values_by_key = {}  # Map (customer, product, date) -> PSL value
        
        try:
            psl_col_letter = 'G'  # PSL is in column G based on headers
            logger.info(f"[PSL PROTECTION] Reading PSL column {psl_col_letter} using individual cell reads...")
            
            # Method 1: Read individual cells for rows 2-100 (more reliable than range reads)
            psl_values_read = 0
            for row_num in range(2, 101):  # Rows 2-100
                try:
                    cell_ref = f'{psl_col_letter}{row_num}'
                    cell_value = sheet.acell(cell_ref, value_render_option='FORMATTED_VALUE').value
                    if cell_value and str(cell_value).strip() != '':
                        psl_val_str = str(cell_value).strip()
                        psl_val_clean = psl_val_str.replace('$', '').replace(',', '').strip()
                        if psl_val_clean != '' and psl_val_clean != '0':
                            existing_psl_values_by_row[row_num] = psl_val_str
                            psl_values_read += 1
                            if psl_values_read <= 5:  # Log first 5
                                logger.info(f"[PSL PROTECTION] Found PSL in row {row_num}: '{psl_val_str}'")
                except Exception as cell_err:
                    # Cell might be empty or doesn't exist - that's okay
                    continue
            
            logger.info(f"[PSL PROTECTION] Successfully read {psl_values_read} PSL values using individual cell reads")
            
            # Also try to read headers and full data for key-based matching
            existing_sheet_data = []
            existing_headers = []
            try:
                existing_sheet_data = sheet.get_all_values()
                logger.info(f"[PSL PROTECTION] get_all_values() returned {len(existing_sheet_data)} total rows")
                if existing_sheet_data:
                    existing_headers = existing_sheet_data[0] if existing_sheet_data else []
                    logger.info(f"[PSL PROTECTION] Existing headers: {existing_headers}")
            except Exception as e3:
                logger.warning(f"[PSL PROTECTION] get_all_values() failed: {e3}")
            
            if len(existing_sheet_data) > 0:
                
                # Find PSL column in existing sheet (may be named differently)
                existing_psl_col_idx = None
                for idx, h in enumerate(existing_headers):
                    if h:
                        h_clean = str(h).strip().lower()
                        if h_clean in ['psl', 'manual input', 'private shipping label']:
                            existing_psl_col_idx = idx
                            logger.info(f"[PSL PROTECTION] Found PSL column at index {idx}: '{h}'")
                            break
                
                # Also try reading PSL column directly if we have headers
                logger.info(f"[PSL PROTECTION] PSL column data length: {len(psl_column_data) if psl_column_data else 0}")
                
                if psl_column_data and len(psl_column_data) > 0:
                    # Read PSL values directly from column G (data starts at row 2)
                    for row_idx, psl_row in enumerate(psl_column_data, start=2):  # Start at row 2 (first data row)
                        if psl_row and len(psl_row) > 0:
                            psl_val = psl_row[0] if isinstance(psl_row, list) else psl_row
                            psl_val_str = str(psl_val).strip() if psl_val else ''
                            psl_val_clean = psl_val_str.replace('$', '').replace(',', '').strip()
                            
                            if psl_val_str and psl_val_clean != '' and psl_val_clean != '0':
                                # Only add if not already found
                                if row_idx not in existing_psl_values_by_row:
                                    existing_psl_values_by_row[row_idx] = psl_val_str
                                    logger.info(f"[PSL PROTECTION] Found PSL value in row {row_idx} from direct read: '{psl_val_str}'")
                
                if existing_psl_col_idx is not None and len(existing_sheet_data) > 1:
                    # Find customer, product, date columns for key matching
                    customer_col_idx = next((i for i, h in enumerate(existing_headers) if h and 'customer' in str(h).lower()), None)
                    product_col_idx = next((i for i, h in enumerate(existing_headers) if h and 'product' in str(h).lower()), None)
                    date_col_idx = next((i for i, h in enumerate(existing_headers) if h and 'date' in str(h).lower()), None)
                    
                    logger.info(f"[PSL PROTECTION] Customer col: {customer_col_idx}, Product col: {product_col_idx}, Date col: {date_col_idx}, PSL col: {existing_psl_col_idx}")
                    
                    # Also read from full sheet data if available
                    for row_idx, row_data in enumerate(existing_sheet_data[1:], start=2):  # Row 2 is first data row
                        if not isinstance(row_data, list):
                            continue
                        
                        # Expand row_data if needed
                        while len(row_data) <= existing_psl_col_idx:
                            row_data.append('')
                        
                        if len(row_data) > existing_psl_col_idx:
                            psl_val = row_data[existing_psl_col_idx]
                            psl_val_str = str(psl_val).strip() if psl_val is not None else ''
                            psl_val_clean = psl_val_str.replace('$', '').replace(',', '').strip()
                            
                            if psl_val_str and psl_val_clean != '' and psl_val_clean != '0':
                                # Only add if not already found from direct read
                                if row_idx not in existing_psl_values_by_row:
                                    existing_psl_values_by_row[row_idx] = psl_val_str
                                    logger.info(f"[PSL PROTECTION] Found PSL value in row {row_idx} from full sheet read: '{psl_val_str}'")
                                
                                # Create key-based mapping
                                if customer_col_idx is not None and product_col_idx is not None and date_col_idx is not None:
                                    max_col_needed = max(customer_col_idx, product_col_idx, date_col_idx, existing_psl_col_idx)
                                    while len(row_data) <= max_col_needed:
                                        row_data.append('')
                                    
                                    if len(row_data) > max_col_needed:
                                        customer_val = str(row_data[customer_col_idx]).strip() if len(row_data) > customer_col_idx else ''
                                        product_val = str(row_data[product_col_idx]).strip() if len(row_data) > product_col_idx else ''
                                        date_val = str(row_data[date_col_idx]).strip() if len(row_data) > date_col_idx else ''
                                        
                                        key = (
                                            customer_val.lower(),
                                            product_val.lower(),
                                            date_val.lower()
                                        )
                                        existing_psl_values_by_key[key] = psl_val_str
                                        logger.info(f"[PSL PROTECTION] Mapped PSL '{psl_val_str}' to key: ({customer_val}, {product_val}, {date_val})")
                
                logger.info(f"[PSL PROTECTION] Successfully read {len(existing_psl_values_by_row)} PSL values (by row)")
                logger.info(f"[PSL PROTECTION] Successfully read {len(existing_psl_values_by_key)} PSL values (by key)")
                
                if len(existing_psl_values_by_row) > 0:
                    sample_rows = list(existing_psl_values_by_row.items())[:5]
                    logger.info(f"[PSL PROTECTION] Sample PSL values found: {sample_rows}")
                else:
                    logger.warning(f"[PSL PROTECTION] No PSL values found in column {psl_col_letter}")
            else:
                logger.info("[PSL PROTECTION] Sheet appears empty (no headers found)")
        except Exception as e:
            logger.error(f"[PSL PROTECTION] ERROR reading existing PSL: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Now write headers (after reading existing data)
        header_range = f'{chr(64 + start_col)}1'
        sheet.update(header_range, [headers])
        
        # Get PSL column index in new headers
        psl_col_idx = headers.index('PSL') if 'PSL' in headers else None
        
        if psl_col_idx is not None:
            try:
                # Read PSL column directly using range - this ensures we get all rows
                psl_column_letter = chr(64 + start_col + psl_col_idx)
                # Read a large range to get all existing PSL values (up to row 1000)
                psl_range = f'{psl_column_letter}2:{psl_column_letter}1000'
                psl_values_raw = sheet.get_values(psl_range)  # Use get_values() which returns a list directly
                
                logger.info(f"[PSL PROTECTION] Reading PSL column {psl_column_letter} from range {psl_range}")
                
                # Also read customer, product, date columns for key-based matching
                customer_col_idx = headers.index('Customer Name') if 'Customer Name' in headers else None
                product_col_idx = headers.index('Product Name') if 'Product Name' in headers else None
                date_col_idx = headers.index('Date') if 'Date' in headers else None
                
                if customer_col_idx is not None and product_col_idx is not None and date_col_idx is not None:
                    customer_col = chr(64 + start_col + customer_col_idx)
                    product_col = chr(64 + start_col + product_col_idx)
                    date_col = chr(64 + start_col + date_col_idx)
                    
                    customer_values = sheet.get_values(f'{customer_col}2:{customer_col}1000')
                    product_values = sheet.get_values(f'{product_col}2:{product_col}1000')
                    date_values = sheet.get_values(f'{date_col}2:{date_col}1000')
                else:
                    customer_values = product_values = date_values = []
                
                # Process PSL values
                logger.info(f"[PSL PROTECTION] Raw PSL data type: {type(psl_values_raw)}, length: {len(psl_values_raw) if psl_values_raw else 0}")
                if psl_values_raw:
                    logger.info(f"[PSL PROTECTION] First few PSL rows: {psl_values_raw[:5]}")
                
                for row_idx, psl_row in enumerate(psl_values_raw, start=2):  # Row 2 is first data row
                    # Handle different return formats from Google Sheets API
                    if psl_row:
                        if isinstance(psl_row, list):
                            psl_val = psl_row[0] if len(psl_row) > 0 else ''
                        else:
                            psl_val = psl_row
                        
                        # Check if value exists and is not empty
                        psl_val_str = str(psl_val).strip() if psl_val else ''
                        if psl_val_str and psl_val_str != '' and psl_val_str != '0':
                            existing_psl_values_by_row[row_idx] = psl_val
                            logger.info(f"[PSL PROTECTION] Found PSL value in row {row_idx}: '{psl_val}' (type: {type(psl_val)})")
                            
                            # Create key-based mapping
                            if (customer_col_idx is not None and product_col_idx is not None and date_col_idx is not None and
                                row_idx - 2 < len(customer_values) and row_idx - 2 < len(product_values) and row_idx - 2 < len(date_values)):
                                customer_val = customer_values[row_idx - 2][0] if customer_values[row_idx - 2] and len(customer_values[row_idx - 2]) > 0 else ''
                                product_val = product_values[row_idx - 2][0] if product_values[row_idx - 2] and len(product_values[row_idx - 2]) > 0 else ''
                                date_val = date_values[row_idx - 2][0] if date_values[row_idx - 2] and len(date_values[row_idx - 2]) > 0 else ''
                                
                                key = (
                                    str(customer_val).strip().lower(),
                                    str(product_val).strip().lower(),
                                    str(date_val).strip().lower()
                                )
                                existing_psl_values_by_key[key] = psl_val
                                logger.info(f"[PSL PROTECTION] Mapped PSL value to key: {key}")
                
                logger.info(f"[PSL PROTECTION] Read {len(existing_psl_values_by_row)} existing PSL values (by row)")
                logger.info(f"[PSL PROTECTION] Read {len(existing_psl_values_by_key)} existing PSL values (by key)")
            except Exception as e:
                logger.error(f"[PSL PROTECTION] ERROR reading existing PSL values: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Prepare order data
        if not orders_df.empty:
            orders_output = pd.DataFrame()
            
            # Map basic columns
            if 'Customer Name' in orders_df.columns:
                orders_output['Customer Name'] = orders_df['Customer Name']
            else:
                orders_output['Customer Name'] = ''
                
            if 'Product Name' in orders_df.columns:
                orders_output['Product Name'] = orders_df['Product Name']
            else:
                orders_output['Product Name'] = ''
                
            if 'Quantity' in orders_df.columns:
                orders_output['Quantity'] = orders_df['Quantity']
            else:
                orders_output['Quantity'] = 0
                
            # Get Sold Price from Unit Price column
            if 'Unit Price' in orders_df.columns:
                orders_output['Sold Price'] = pd.to_numeric(orders_df['Unit Price'], errors='coerce').fillna(0)
            else:
                orders_output['Sold Price'] = 0
            
            # Get Shipping Cost (what customer paid for shipping)
            if 'Shipping Cost' in orders_df.columns:
                orders_output['Shipping Cost'] = pd.to_numeric(orders_df['Shipping Cost'], errors='coerce').fillna(0)
            else:
                orders_output['Shipping Cost'] = 0
            
            # Add PSL column (Private Shipping Label) - initialize as empty, will be preserved from existing data
            # DO NOT set to empty string here - let preservation logic handle it
            if 'PSL' not in orders_output.columns:
                orders_output['PSL'] = ''
                
            # Extract size from Variant Title or Product Name or Product Name
            def extract_size_from_text(text):
                """Extract size from text (variant title or product name)"""
                if pd.isna(text) or text == '':
                    return ''
                
                text_str = str(text).upper()
                
                # First check for exact size codes (XXL, XL, L, M, S, etc.)
                # Check in order from largest to smallest to avoid partial matches
                for size in ['XXXL', 'XXL', 'XL', 'XS', 'S', 'M', 'L']:
                    # Match whole words only (with word boundaries)
                    import re
                    if re.search(r'\b' + size + r'\b', text_str):
                        return size
                
                # Then check for full size names in product name
                size_map = {
                    'SMALL': 'S',
                    'MEDIUM': 'M', 'MED': 'M',
                    'LARGE': 'L', 'LG': 'L',
                    'EXTRA LARGE': 'XL', 'EXTRALARGE': 'XL',
                    'EXTRA SMALL': 'XS', 'EXTRASMALL': 'XS',
                    'EXTRA EXTRA LARGE': 'XXL', 'XXLARGE': 'XXL'
                }
                
                for size_name, size_code in size_map.items():
                    if size_name in text_str:
                        return size_code
                
                # If no match, try to extract from variant title format (e.g., "Large / Red")
                if '/' in text_str:
                    parts = text_str.split('/')
                    first_part = parts[0].strip()
                    # Check if first part is a size
                    for size_name, size_code in size_map.items():
                        if size_name in first_part:
                            return size_code
                    # Return first part if it looks like a size code
                    if first_part in ['S', 'M', 'L', 'XL', 'XXL', 'XXXL', 'XS']:
                        return first_part
                
                return ''
            
            # First try to extract from Variant Title
            if 'Variant Title' in orders_df.columns:
                orders_output['Size'] = orders_df['Variant Title'].apply(extract_size_from_text)
            else:
                orders_output['Size'] = ''
            
            # If Size is still empty, check Product Name
            if 'Product Name' in orders_df.columns:
                empty_size_mask = (orders_output['Size'] == '') | (orders_output['Size'].isna())
                if empty_size_mask.any():
                    # Extract size from Product Name where Size is empty
                    product_names = orders_df.loc[empty_size_mask, 'Product Name']
                    extracted_sizes = product_names.apply(extract_size_from_text)
                    orders_output.loc[empty_size_mask, 'Size'] = extracted_sizes
            
            # Add Unit Cost (12.26 for all t-shirts)
            cost_per_unit = config.get('profit', {}).get('cost_per_shirt', 12.26)
            orders_output['Unit Cost'] = cost_per_unit
            
            # Profit and Profit Margin % will be calculated using Google Sheets formulas
            # We'll add the formulas after preserving PSL values
            # Placeholder columns for now
            orders_output['Profit'] = 0  # Will be replaced with formula
            orders_output['Profit Margin %'] = 0  # Will be replaced with formula
            
            # Add Date
            if 'Date' in orders_df.columns:
                orders_output['Date'] = orders_df['Date']
            else:
                orders_output['Date'] = ''
            
            # Add Order Status (from Financial Status)
            if 'Financial Status' in orders_df.columns:
                orders_output['Order Status'] = orders_df['Financial Status'].str.title()
            else:
                orders_output['Order Status'] = 'Paid'  # Default
            
            # Add Shipping Status (from Fulfillment Status)
            if 'Fulfillment Status' in orders_df.columns:
                fulfillment_status = orders_df['Fulfillment Status'].fillna('')
                orders_output['Shipping Status'] = fulfillment_status.apply(
                    lambda x: 'Shipped' if x and str(x).lower() in ['fulfilled', 'shipped'] 
                    else 'Pending' if x and str(x).lower() in ['pending', 'partial'] 
                    else 'Unfulfilled' if x == '' or pd.isna(x)
                    else str(x).title()
                )
            else:
                orders_output['Shipping Status'] = 'Unfulfilled'  # Default
            
            # Ensure all header columns exist
            for col in headers:
                if col not in orders_output.columns:
                    orders_output[col] = ''
            
            # PRESERVE PSL VALUES: Read existing PSL (Private Shipping Label) entries BEFORE writing
            # This is CRITICAL - we must preserve user-entered PSL values
            try:
                existing_data = sheet.get_all_values()
                if len(existing_data) > 1:  # Has header + data
                    existing_df = pd.DataFrame(existing_data[1:], columns=existing_data[0])
                    
                    # Match rows by Customer Name + Product Name + Date to preserve PSL values
                    # Check for PSL column (current name) or Manual Input (old name)
                    # Also check for variations with spaces (case-insensitive)
                    psl_column_name = None
                    existing_columns_lower = [str(col).strip().lower() for col in existing_df.columns]
                    if 'psl' in existing_columns_lower:
                        # Find the actual column name (preserving case)
                        psl_col_idx = existing_columns_lower.index('psl')
                        psl_column_name = existing_df.columns[psl_col_idx]
                    elif 'manual input' in existing_columns_lower:
                        psl_col_idx = existing_columns_lower.index('manual input')
                        psl_column_name = existing_df.columns[psl_col_idx]
                    
                    if psl_column_name:
                        logger.info(f"Found PSL column: '{psl_column_name}' with {len(existing_df)} rows")
                        # Create a mapping dictionary from existing data (case-insensitive matching)
                        psl_map = {}
                        for idx, row in existing_df.iterrows():
                            # Create a key from Customer Name, Product Name, and Date (normalized to lowercase)
                            key = (
                                str(row.get('Customer Name', '')).strip().lower(),
                                str(row.get('Product Name', '')).strip().lower(),
                                str(row.get('Date', '')).strip().lower()
                            )
                            # Get PSL value (could be number or text)
                            psl_value = row.get(psl_column_name, '')
                            # Preserve the value as-is if it exists and is not empty
                            if pd.notna(psl_value) and str(psl_value).strip() != '' and str(psl_value).strip() != '0':
                                # Preserve the value as-is (could be number or text)
                                psl_map[key] = psl_value
                        
                        logger.info(f"Found {len(psl_map)} non-empty PSL values in existing sheet")
                        
                        # Apply preserved values to new data (case-insensitive matching)
                        psl_values = []
                        for idx, row in orders_output.iterrows():
                            key = (
                                str(row.get('Customer Name', '')).strip().lower(),
                                str(row.get('Product Name', '')).strip().lower(),
                                str(row.get('Date', '')).strip().lower()
                            )
                            # Use preserved value if exists, otherwise empty
                            preserved_value = psl_map.get(key, '')
                            psl_values.append(preserved_value)
                        
                        # IMPORTANT: Set PSL values BEFORE reordering
                        orders_output['PSL'] = psl_values
                        preserved_count = len([x for x in psl_values if x != '' and pd.notna(x) and str(x).strip() != '0'])
                        logger.info(f"Preserved {preserved_count} existing PSL values in output")
                    else:
                        # No PSL column found, initialize as empty
                        if 'PSL' not in orders_output.columns:
                            orders_output['PSL'] = ''
                        logger.warning(f"PSL column not found in existing sheet. Available columns: {list(existing_df.columns)}")
            except Exception as e:
                logger.error(f"ERROR: Could not read existing PSL values: {e}")
                logger.error("PSL values may be lost! Please check the sheet manually.")
                # Still initialize PSL column even if read fails
                if 'PSL' not in orders_output.columns:
                    orders_output['PSL'] = ''
            
            # Reorder to match headers
            # Note: PSL values were already read above (before headers were written)
            orders_output = orders_output[headers]
            
            # CRITICAL: ALWAYS write PSL column position to maintain column alignment
            # If we can't read existing PSL values, write empty strings - DO NOT overwrite existing
            # Set PSL to empty in the DataFrame before writing (to maintain column structure)
            if 'PSL' in orders_output.columns:
                # Clear PSL values from DataFrame - we'll preserve existing sheet values by NOT updating PSL
                orders_output['PSL'] = ''
            
            # Write all data INCLUDING PSL column (as empty) to maintain column alignment
            values = orders_output.fillna('').values.tolist()
            data_range = f'{chr(64 + start_col)}2'
            
            # CRITICAL: Use batch_update to write all columns EXCEPT PSL if we can't read existing PSL values
            # This preserves PSL values while maintaining correct column alignment
            if psl_col_idx is not None and (len(existing_psl_values_by_row) == 0 and len(existing_psl_values_by_key) == 0):
                # Could not read PSL values - write all columns EXCEPT PSL using batch_update
                logger.warning("="*70)
                logger.warning("[PSL PROTECTION] CRITICAL: Could not read existing PSL values!")
                logger.warning("[PSL PROTECTION] Writing data but SKIPPING PSL column (column G) to preserve your manual entries")
                logger.warning("[PSL PROTECTION] Your PSL values will remain untouched")
                logger.warning("="*70)
                
                # CRITICAL: Write all columns EXCEPT PSL, then restore PSL values afterward
                # Write columns in two parts: before PSL and after PSL (skip PSL column entirely)
                if psl_col_idx > 0:
                    # Write columns A through (PSL-1) - these are before PSL
                    before_psl_range = f'{chr(64 + start_col)}2:{chr(64 + start_col + psl_col_idx - 1)}{len(values) + 1}'
                    before_psl_values = [[row[i] for i in range(psl_col_idx)] for row in values]
                    sheet.update(before_psl_range, before_psl_values, value_input_option='USER_ENTERED')
                    logger.info(f"[PSL PROTECTION] Wrote columns A-{chr(64 + start_col + psl_col_idx - 1)} (before PSL)")
                
                # DO NOT write PSL column (column G) - this preserves existing values
                logger.info(f"[PSL PROTECTION] SKIPPED column {chr(64 + start_col + psl_col_idx)} (PSL) - will restore values after")
                
                if psl_col_idx < len(headers) - 1:
                    # Write columns (PSL+1) through end - these are after PSL
                    after_psl_start_col = start_col + psl_col_idx + 1  # Column after PSL
                    after_psl_end_col = start_col + len(headers) - 1  # Last column
                    
                    # Calculate column letters
                    if after_psl_start_col <= 26:
                        after_psl_start_letter = chr(64 + after_psl_start_col)
                    else:
                        first_letter = chr(64 + ((after_psl_start_col - 1) // 26))
                        second_letter = chr(64 + ((after_psl_start_col - 1) % 26) + 1)
                        after_psl_start_letter = first_letter + second_letter
                    
                    if after_psl_end_col <= 26:
                        after_psl_end_letter = chr(64 + after_psl_end_col)
                    else:
                        first_letter = chr(64 + ((after_psl_end_col - 1) // 26))
                        second_letter = chr(64 + ((after_psl_end_col - 1) % 26) + 1)
                        after_psl_end_letter = first_letter + second_letter
                    
                    after_psl_range = f'{after_psl_start_letter}2:{after_psl_end_letter}{len(values) + 1}'
                    after_psl_values = [[row[i] for i in range(psl_col_idx + 1, len(headers))] for row in values]
                    sheet.update(after_psl_range, after_psl_values, value_input_option='USER_ENTERED')
                    logger.info(f"[PSL PROTECTION] Wrote columns {after_psl_start_letter}-{after_psl_end_letter} (after PSL)")
                
                # CRITICAL: Restore PSL values that we read earlier
                if len(existing_psl_values_by_row) > 0:
                    psl_column_letter = chr(64 + start_col + psl_col_idx)
                    logger.info(f"[PSL PROTECTION] Restoring {len(existing_psl_values_by_row)} PSL values to column {psl_column_letter}")
                    
                    # Restore PSL values using individual cell writes for each preserved value
                    restored_count = 0
                    for row_num, psl_value in existing_psl_values_by_row.items():
                        try:
                            cell_ref = f'{psl_column_letter}{row_num}'
                            sheet.update_acell(cell_ref, psl_value)
                            restored_count += 1
                        except Exception as restore_err:
                            logger.warning(f"[PSL PROTECTION] Failed to restore PSL in row {row_num}: {restore_err}")
                    
                    logger.info(f"[PSL PROTECTION] Successfully restored {restored_count} PSL values")
                else:
                    # Try to restore from backup file if we couldn't read values
                    backup_file = Path('config/psl_backup.json')
                    if backup_file.exists():
                        logger.info(f"[PSL PROTECTION] No PSL values read - attempting restore from backup file...")
                        try:
                            import json
                            with open(backup_file, 'r') as f:
                                backup_psl_values = json.load(f)
                            
                            if backup_psl_values and len(backup_psl_values) > 0:
                                psl_column_letter = chr(64 + start_col + psl_col_idx)
                                restored_count = 0
                                for row_num, psl_value in backup_psl_values.items():
                                    try:
                                        cell_ref = f'{psl_column_letter}{int(row_num)}'
                                        sheet.update_acell(cell_ref, str(psl_value))
                                        restored_count += 1
                                        if restored_count <= 3:
                                            logger.info(f"  [PSL PROTECTION] Restored row {row_num}: {psl_value}")
                                    except Exception:
                                        continue
                                
                                if restored_count > 0:
                                    logger.info(f"[PSL PROTECTION] ✓ Restored {restored_count} PSL values from backup!")
                                else:
                                    logger.warning("[PSL PROTECTION] Backup file exists but restore failed")
                            else:
                                logger.warning("[PSL PROTECTION] Backup file is empty")
                        except Exception as backup_err:
                            logger.warning(f"[PSL PROTECTION] Failed to restore from backup: {backup_err}")
                    else:
                        logger.warning("[PSL PROTECTION] No PSL values found to restore and no backup file exists")
            else:
                # We can read PSL values OR PSL column doesn't exist - write normally
                sheet.update(data_range, values, value_input_option='USER_ENTERED')
                
                # NOW restore PSL values if we found any
                if psl_col_idx is not None and (len(existing_psl_values_by_row) > 0 or len(existing_psl_values_by_key) > 0):
                    psl_column_letter = chr(64 + start_col + psl_col_idx)
                    psl_updates = []
                    
                    for row_idx_in_df, (idx, row) in enumerate(orders_output.iterrows(), start=0):
                        row_num_in_sheet = row_idx_in_df + 2
                        
                        # Use preserved values
                        preserved_psl = row.get('PSL', '') if 'PSL' in orders_output.columns else ''
                        final_psl = ''
                        
                        if preserved_psl and str(preserved_psl).strip() != '' and str(preserved_psl).strip() != '0':
                            final_psl = preserved_psl
                        elif row_num_in_sheet in existing_psl_values_by_row:
                            final_psl = existing_psl_values_by_row[row_num_in_sheet]
                        else:
                            key = (
                                str(row.get('Customer Name', '')).strip().lower(),
                                str(row.get('Product Name', '')).strip().lower(),
                                str(row.get('Date', '')).strip().lower()
                            )
                            if key in existing_psl_values_by_key:
                                final_psl = existing_psl_values_by_key[key]
                        
                        psl_updates.append([final_psl])
                    
                    if len(psl_updates) > 0:
                        psl_range = f'{psl_column_letter}2:{psl_column_letter}{len(psl_updates) + 1}'
                        sheet.update(psl_range, psl_updates, value_input_option='USER_ENTERED')
                        preserved_count = len([u for u in psl_updates if u and u[0] and str(u[0]).strip() != '' and str(u[0]).strip() != '0'])
                        logger.info(f"[PSL PROTECTION] Restored {preserved_count} PSL values")
            
            # Now add Profit formulas: (Sold Price - Unit Cost - PSL) + Shipping Cost
            # Get column letters for formula
            sold_price_col = chr(64 + start_col + headers.index('Sold Price'))  # Column E (index 4)
            shipping_cost_col = chr(64 + start_col + headers.index('Shipping Cost'))  # Column F (index 5)
            psl_col = chr(64 + start_col + headers.index('PSL'))  # Column G (index 6)
            unit_cost_col = chr(64 + start_col + headers.index('Unit Cost'))  # Column H (index 7)
            profit_col = chr(64 + start_col + headers.index('Profit'))  # Column I (index 8)
            
            # Create Profit formulas for each row
            profit_formulas = []
            for row_idx in range(len(orders_output)):
                row_num = row_idx + 2  # Row 2 is first data row
                # Formula: (Sold Price - Unit Cost - PSL) + Shipping Cost
                profit_formula = f'=({sold_price_col}{row_num}-{unit_cost_col}{row_num}-{psl_col}{row_num})+{shipping_cost_col}{row_num}'
                profit_formulas.append(profit_formula)
            
            # Update Profit column with formulas
            if len(profit_formulas) > 0:
                profit_range = f'{profit_col}2:{profit_col}{len(profit_formulas) + 1}'
                profit_values = [[formula] for formula in profit_formulas]
                sheet.update(profit_range, profit_values, value_input_option='USER_ENTERED')
            
            # Update Profit Margin % formulas: (Profit / Sold Price)
            profit_margin_col = chr(64 + start_col + headers.index('Profit Margin %'))  # Column J (index 9)
            profit_margin_formulas = []
            for row_idx in range(len(orders_output)):
                row_num = row_idx + 2
                # Formula: Profit / Sold Price (will be formatted as percentage)
                profit_margin_formula = f'=IF({sold_price_col}{row_num}<>0, {profit_col}{row_num}/{sold_price_col}{row_num}, 0)'
                profit_margin_formulas.append(profit_margin_formula)
            
            # Update Profit Margin % column with formulas
            if len(profit_margin_formulas) > 0:
                profit_margin_range = f'{profit_margin_col}2:{profit_margin_col}{len(profit_margin_formulas) + 1}'
                profit_margin_values = [[formula] for formula in profit_margin_formulas]
                sheet.update(profit_margin_range, profit_margin_values, value_input_option='USER_ENTERED')
            
        else:
            logger.warning("No order data to write")
        
        # Apply formatting (centered, borders, colors only for Product Name)
        apply_formatting(sheet, headers, start_col)
        
        # Format numbers
        currency_cols = ['Sold Price', 'Shipping Cost', 'PSL', 'Unit Cost', 'Profit']
        percent_cols = ['Profit Margin %']
        date_cols = ['Date']
        format_numbers_custom(sheet, headers, currency_cols, percent_cols, date_cols, start_col)
        
        # Apply conditional formatting for Product Name only
        apply_product_name_formatting(sheet, headers, start_col)
        
        # Apply conditional formatting for Size column
        apply_size_formatting(sheet, headers, start_col)
        
        # Apply conditional formatting for Order Status
        apply_order_status_formatting(sheet, headers, start_col)
        
        # Apply conditional formatting for Shipping Status
        apply_shipping_status_formatting(sheet, headers, start_col)
        
        # Apply strikethrough formatting for Partially Refunded orders
        apply_strikethrough_for_refunded(sheet, orders_output, headers, start_col)
        
        # Format PSL column (make it clear it's for user input)
        format_psl_column(sheet, headers, start_col, len(orders_output) if not orders_output.empty else 0)
        
        # Auto-resize columns for better spacing, then manually widen Profit and Date
        try:
            # First auto-resize all columns
            sheet.spreadsheet.batch_update({
                "requests": [{
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": start_col - 1,
                            "endIndex": start_col - 1 + len(headers)
                        }
                    }
                }]
            })
            
            # Then manually set wider widths for Profit and Date columns
            col_start = start_col - 1
            profit_col = col_start + headers.index('Profit')
            date_col = col_start + headers.index('Date')
            
            sheet.spreadsheet.batch_update({
                "requests": [
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet.id,
                                "dimension": "COLUMNS",
                                "startIndex": profit_col,
                                "endIndex": profit_col + 1
                            },
                            "properties": {
                                "pixelSize": 120  # Wider for Profit column
                            },
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet.id,
                                "dimension": "COLUMNS",
                                "startIndex": date_col,
                                "endIndex": date_col + 1
                            },
                            "properties": {
                                "pixelSize": 120  # Wider for Date column
                            },
                            "fields": "pixelSize"
                        }
                    }
                ]
            })
        except Exception as e:
            logger.warning(f"Could not resize columns: {e}")
        
        # Clean up empty columns A-C and L-M (remove borders and formatting)
        cleanup_empty_columns(sheet, start_col, len(headers))
        
        # Add summary section on the right side
        add_summary_section(sheet, orders_output, headers, start_col, len(headers))
        
        # Delete unused sheets (Customers, Products, Inventory) if they exist
        delete_unused_sheets(manager)
        
        # Create/Update Financial Tracking sheet
        create_financial_tracking_sheet(manager, orders_output, orders_df)
        
        # Add filter (starting from column D)
        try:
            num_rows = len(orders_output) + 1 if not orders_df.empty else 1
            sheet.spreadsheet.batch_update({
                "requests": [{
                    "setBasicFilter": {
                        "filter": {
                            "range": {
                                "sheetId": sheet.id,
                                "startRowIndex": 0,
                                "endRowIndex": num_rows,
                                "startColumnIndex": start_col - 1,  # 0-indexed, so D = 3
                                "endColumnIndex": start_col - 1 + len(headers)
                            }
                        }
                    }
                }]
            })
        except Exception as e:
            logger.warning(f"Could not add filter: {e}")
        
        # CRITICAL: Final PSL restore from backup file (runs at the very end, after ALL operations complete)
        # This ensures PSL values are restored even if they were accidentally cleared during any operation
        if psl_col_idx is not None:
            backup_file = Path('config/psl_backup.json')
            if backup_file.exists():
                logger.info("="*70)
                logger.info("[PSL PROTECTION] FINAL RESTORE: Restoring PSL values from backup file...")
                try:
                    import json
                    with open(backup_file, 'r') as f:
                        backup_psl_values = json.load(f)
                    
                    if backup_psl_values and len(backup_psl_values) > 0:
                        psl_column_letter = chr(64 + start_col + psl_col_idx)
                        restored_count = 0
                        
                        for row_num, psl_value in backup_psl_values.items():
                            try:
                                cell_ref = f'{psl_column_letter}{int(row_num)}'
                                sheet.update_acell(cell_ref, str(psl_value))
                                restored_count += 1
                                if restored_count <= 5:
                                    logger.info(f"  [PSL PROTECTION] ✓ Restored row {row_num}: {psl_value}")
                            except Exception as restore_err:
                                logger.warning(f"[PSL PROTECTION] Failed to restore row {row_num}: {restore_err}")
                        
                        if restored_count > 0:
                            logger.info(f"[PSL PROTECTION] ✓✓✓ FINAL RESTORE SUCCESS: Restored {restored_count} PSL values! ✓✓✓")
                        else:
                            logger.warning("[PSL PROTECTION] Backup file exists but no values could be restored")
                    else:
                        logger.warning("[PSL PROTECTION] Backup file is empty")
                except Exception as backup_err:
                    logger.error(f"[PSL PROTECTION] ERROR during final restore: {backup_err}")
                    import traceback
                    logger.error(traceback.format_exc())
                logger.info("="*70)
            else:
                logger.warning("[PSL PROTECTION] No backup file found")
                logger.warning("[PSL PROTECTION] TIP: Run 'python src/backup_restore_psl.py backup' before syncing next time")
        
        logger.info("Orders sheet updated successfully!")
        
    except Exception as e:
        logger.error(f"Error during update: {str(e)}", exc_info=True)
        raise


def apply_formatting(sheet, headers: list, start_col: int):
    """Apply formatting: centered columns, borders, blue header, white background"""
    requests = []
    
    col_start = start_col - 1  # Convert to 0-indexed
    
    # Blue header background with white text, centered
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": col_start,
                "endColumnIndex": col_start + len(headers)
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.26, "green": 0.52, "blue": 0.96},  # Google blue
                    "textFormat": {
                        "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},  # White text
                        "fontSize": 11,
                        "bold": True
                    },
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE"
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
        }
    })
    
    # White background for data rows, centered, black text
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 1,
                "endRowIndex": 1000,
                "startColumnIndex": col_start,
                "endColumnIndex": col_start + len(headers)
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},  # White background
                    "textFormat": {
                        "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}  # Black text
                    },
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE"
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
        }
    })
    
    # Add black borders to all cells
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": 1000,
                "startColumnIndex": col_start,
                "endColumnIndex": col_start + len(headers)
            },
            "cell": {
                "userEnteredFormat": {
                    "borders": {
                        "top": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "left": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "right": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}}
                    }
                }
            },
            "fields": "userEnteredFormat.borders"
        }
    })
    
    try:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info(f"Applied formatting to sheet '{sheet.title}'")
    except Exception as e:
        logger.warning(f"Could not apply formatting: {e}")


def format_numbers_custom(sheet, headers: list, currency_cols: list, percent_cols: list, date_cols: list, start_col: int):
    """Format numbers with custom column offset"""
    requests = []
    col_start = start_col - 1  # Convert to 0-indexed
    
    # Currency formatting
    for col_name in currency_cols:
        if col_name in headers:
            col_idx = col_start + headers.index(col_name)
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
            col_idx = col_start + headers.index(col_name)
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
    
    # Quantity formatting - should be number, not currency
    if 'Quantity' in headers:
        quantity_col = col_start + headers.index('Quantity')
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 1,
                    "startColumnIndex": quantity_col,
                    "endColumnIndex": quantity_col + 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "NUMBER",
                            "pattern": "0"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })
    
    # Date formatting
    for col_name in date_cols:
        if col_name in headers:
            col_idx = col_start + headers.index(col_name)
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
        try:
            sheet.spreadsheet.batch_update({"requests": requests})
            logger.info("Formatted numbers")
        except Exception as e:
            logger.warning(f"Could not format numbers: {e}")


def apply_product_name_formatting(sheet, headers: list, start_col: int):
    """Apply darker grey background for Arcus Tee, purple for All Paths Tee - ONLY for Product Name column"""
    requests = []
    
    # Find Product Name column index
    if 'Product Name' not in headers:
        return
    
    col_start = start_col - 1  # Convert to 0-indexed
    product_name_col = col_start + headers.index('Product Name')
    
    # Darker grey background for Arcus Tee
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet.id,
                    "startRowIndex": 1,  # Skip header
                    "endRowIndex": 1000,
                    "startColumnIndex": product_name_col,
                    "endColumnIndex": product_name_col + 1
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_CONTAINS",
                        "values": [{"userEnteredValue": "Arcus"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 0.7, "green": 0.7, "blue": 0.7}  # Darker grey
                    }
                }
            },
            "index": 0
        }
    })
    
    # Purple background for All Paths Tee
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet.id,
                    "startRowIndex": 1,  # Skip header
                    "endRowIndex": 1000,
                    "startColumnIndex": product_name_col,
                    "endColumnIndex": product_name_col + 1
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_CONTAINS",
                        "values": [{"userEnteredValue": "All Paths"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 0.8, "green": 0.7, "blue": 0.9}  # Light purple
                    }
                }
            },
            "index": 1
        }
    })
    
    try:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("Applied product name formatting (darker grey for Arcus, purple for All Paths)")
    except Exception as e:
        logger.warning(f"Could not apply product name formatting: {e}")


def add_summary_section(sheet, orders_output, headers: list, start_col: int, num_data_cols: int):
    """Add summary section on the right side of the Orders table using Google Sheets formulas"""
    # Position: Start 2 columns after Shipping Status
    # Shipping Status is the last column (index 11 = column L)
    # Summary starts 2 columns after that = column O (15th column)
    summary_start_col = 15  # Column O (2 columns after Shipping Status at column L)
    summary_col_start_idx = summary_start_col - 1  # Convert to 0-indexed (14)
    
    # Get column letters for formulas (based on headers position)
    # Headers start at column A (start_col = 1)
    # Sold Price is at index 4 (5th column = E)
    # Unit Cost is at index 5 (6th column = F)
    # Quantity is at index 3 (4th column = D)
    # Order Status is at index 9 (10th column = J)
    # Shipping Status is at index 10 (11th column = K)
    sold_price_col = chr(64 + start_col + headers.index('Sold Price'))  # Column E
    unit_cost_col = chr(64 + start_col + headers.index('Unit Cost'))    # Column F
    quantity_col = chr(64 + start_col + headers.index('Quantity'))      # Column D
    order_status_col = chr(64 + start_col + headers.index('Order Status'))  # Column J
    shipping_status_col = chr(64 + start_col + headers.index('Shipping Status'))  # Column K
    
    # Calculate last row with data
    last_row = len(orders_output) + 1 if not orders_output.empty else 2  # +1 for header
    
    # Get column letters for summary section
    value_col = chr(64 + summary_start_col + 1)  # Value column in summary (column N)
    
    # Total Revenue formula: Exclude rows where Order Status is "Partially Refunded" 
    # or Shipping Status is "Unfulfilled" or "Partial"
    # Using SUMIFS to exclude these conditions
    total_revenue_formula = f'=SUMIFS({sold_price_col}2:{sold_price_col}{last_row}, {order_status_col}2:{order_status_col}{last_row}, "<>Partially Refunded", {shipping_status_col}2:{shipping_status_col}{last_row}, "<>Unfulfilled", {shipping_status_col}2:{shipping_status_col}{last_row}, "<>Partial")'
    
    # Calculate Shopify Payout from actual Shopify order data
    # Sum up order totals (excluding partially refunded/unfulfilled orders)
    shopify_payout_amount = 0
    num_transactions = 0
    
    for _, row in orders_output.iterrows():
        # Check if order should be excluded
        order_status = str(row.get('Order Status', '')).strip()
        shipping_status = str(row.get('Shipping Status', '')).strip()
        
        # Skip excluded statuses
        if order_status == 'Partially Refunded':
            continue
        if shipping_status in ['Unfulfilled', 'Partial']:
            continue
        
        # Get the sold price from the row
        sold_price = row.get('Sold Price', 0)
        try:
            sold_price = float(sold_price) if sold_price else 0
            if sold_price > 0:
                shopify_payout_amount += sold_price
                num_transactions += 1
        except (ValueError, TypeError):
            pass
    
    # Calculate payout after fees (2.9% + $0.30 per transaction)
    shopify_payout_value = shopify_payout_amount - (shopify_payout_amount * 0.029) - (num_transactions * 0.30)
    
    # Summary data with formulas - ORDER MATTERS!
    # Row 1: Header (Metric, Value)
    # Row 2: Total Revenue (sum of column E - Sold Price, excluding partially refunded/unfulfilled)
    # Row 3: Total Product Costs (sum of column F - Unit Cost)
    # Row 4: TOTAL COSTS (809.32)
    # Row 5: NET PROFIT (Total Revenue - Total Product Costs)
    # Row 6: Profit Per Shirt (Total Revenue - Total Product Costs)
    # Row 7: Total Units Sold (sum of column D - Quantity)
    # Row 8: Shopify Payout (calculated from Shopify order data)
    # Row 9-10: Empty rows
    # Row 11: PSL Backup Reminder Section
    summary_data = [
        ['Metric', 'Value'],
        ['Total Revenue', total_revenue_formula],  # Column E - Sold Price (excluding excluded statuses)
        ['Total Product Costs', f'=SUM({unit_cost_col}2:{unit_cost_col}{last_row})'],  # Column F - Unit Cost
        ['TOTAL COSTS', 809.32],  # Hardcoded value
        ['NET PROFIT', f'={value_col}4-{value_col}2'],  # Row 4 (TOTAL COSTS) - Row 2 (Total Revenue)
        ['Profit Per Shirt (Overall)', f'={value_col}2-{value_col}3'],  # Row 2 (Total Revenue) - Row 3 (Total Product Costs)
        ['Total Units Sold', f'=SUM({quantity_col}2:{quantity_col}{last_row})'],  # Column D - Quantity
        ['Shopify Payout', shopify_payout_value],  # Calculated from Shopify order data (excluding excluded statuses)
        ['', ''],  # Empty row
        ['', ''],  # Empty row
        ['--- PSL BACKUP REMINDER ---', ''],  # Reminder header
        ['1. BACKUP before sync:', 'python src/backup_restore_psl.py backup'],
        ['2. RUN SYNC:', 'python src/update_orders_sheet.py'],
        ['3. RESTORE if needed:', 'python src/backup_restore_psl.py restore'],
        ['', ''],  # Empty row
        ['NOTE: Always backup PSL', 'values before syncing!']
    ]
    
    # Write summary data
    summary_range = f'{chr(64 + summary_start_col)}1'
    logger.info(f"Writing summary section starting at column {chr(64 + summary_start_col)}")
    logger.info(f"Summary formulas: Total Revenue uses column {sold_price_col}, Total Product Costs uses column {unit_cost_col}")
    sheet.update(summary_range, summary_data, value_input_option='USER_ENTERED')
    
    # Format the summary section
    requests = []
    
    # Orange header row
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": summary_col_start_idx,
                "endColumnIndex": summary_col_start_idx + 2
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 1.0, "green": 0.65, "blue": 0.0},  # Orange
                    "textFormat": {
                        "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0},  # Black text
                        "fontSize": 11,
                        "bold": True
                    },
                    "horizontalAlignment": "CENTER"
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
        }
    })
    
    # Bold for specific rows (TOTAL COSTS, NET PROFIT, Profit Per Shirt, Shopify Payout)
    bold_rows = [3, 4, 5, 7]  # Row indices (0-indexed: TOTAL COSTS row 4, NET PROFIT row 5, Profit Per Shirt row 6, Shopify Payout row 8)
    for row_idx in bold_rows:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": row_idx,
                    "endRowIndex": row_idx + 1,
                    "startColumnIndex": summary_col_start_idx,
                    "endColumnIndex": summary_col_start_idx + 2
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "bold": True
                        }
                    }
                },
                "fields": "userEnteredFormat.textFormat.bold"
            }
        })
    
    # Dark red background for TOTAL COSTS entire row (row 4)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 3,  # Row 4 (0-indexed)
                "endRowIndex": 4,
                "startColumnIndex": summary_col_start_idx,  # Both metric and value columns
                "endColumnIndex": summary_col_start_idx + 2
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.8, "green": 0.2, "blue": 0.2}  # Dark red
                }
            },
            "fields": "userEnteredFormat.backgroundColor"
        }
    })
    
    # Bright green background for NET PROFIT entire row (row 5)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 4,  # Row 5 (0-indexed)
                "endRowIndex": 5,
                "startColumnIndex": summary_col_start_idx,  # Both metric and value columns
                "endColumnIndex": summary_col_start_idx + 2
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.5, "green": 1.0, "blue": 0.5}  # Bright green
                }
            },
            "fields": "userEnteredFormat.backgroundColor"
        }
    })
    
    # Light green background for Profit Per Shirt entire row (row 6)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 5,  # Row 6 (0-indexed)
                "endRowIndex": 6,
                "startColumnIndex": summary_col_start_idx,  # Both metric and value columns
                "endColumnIndex": summary_col_start_idx + 2
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.85, "green": 0.95, "blue": 0.85}  # Light green
                }
            },
            "fields": "userEnteredFormat.backgroundColor"
        }
    })
    
    # Orange background for second-to-last empty row
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 8,  # Row 9 (0-indexed)
                "endRowIndex": 9,
                "startColumnIndex": summary_col_start_idx,
                "endColumnIndex": summary_col_start_idx + 2
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 1.0, "green": 0.65, "blue": 0.0}  # Orange
                }
            },
            "fields": "userEnteredFormat.backgroundColor"
        }
    })
    
    # Format currency for value column
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 1,  # Skip header
                "endRowIndex": 8,  # Up to Shopify Payout
                "startColumnIndex": summary_col_start_idx + 1,  # Value column
                "endColumnIndex": summary_col_start_idx + 2
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
    
    # Format Total Units Sold as number (not currency)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 6,  # Total Units Sold row (row 7, 0-indexed)
                "endRowIndex": 7,
                "startColumnIndex": summary_col_start_idx + 1,
                "endColumnIndex": summary_col_start_idx + 2
            },
            "cell": {
                "userEnteredFormat": {
                    "numberFormat": {
                        "type": "NUMBER",
                        "pattern": "0"
                    }
                }
            },
            "fields": "userEnteredFormat.numberFormat"
        }
    })
    
    # Set alignment: Metric column left-aligned, Value column right-aligned
    # Metric column (left-aligned)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": 10,
                "startColumnIndex": summary_col_start_idx,  # Metric column
                "endColumnIndex": summary_col_start_idx + 1
            },
            "cell": {
                "userEnteredFormat": {
                    "horizontalAlignment": "LEFT"
                }
            },
            "fields": "userEnteredFormat.horizontalAlignment"
        }
    })
    
    # Value column (right-aligned)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": 10,
                "startColumnIndex": summary_col_start_idx + 1,  # Value column
                "endColumnIndex": summary_col_start_idx + 2
            },
            "cell": {
                "userEnteredFormat": {
                    "horizontalAlignment": "RIGHT"
                }
            },
            "fields": "userEnteredFormat.horizontalAlignment"
        }
    })
    
    # Format reminder section (rows 11-16)
    reminder_start_row = 10  # Row 11 (0-indexed: 10) where reminder section starts
    reminder_end_row = 15  # Last row of reminder (0-indexed: 15, row 16)
    
    # Yellow background for reminder section header
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": reminder_start_row,
                "endRowIndex": reminder_start_row + 1,
                "startColumnIndex": summary_col_start_idx,
                "endColumnIndex": summary_col_start_idx + 2
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8},  # Light yellow
                    "textFormat": {
                        "bold": True,
                        "fontSize": 11
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat)"
        }
    })
    
    # Light grey background for reminder instructions
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": reminder_start_row + 1,
                "endRowIndex": reminder_end_row,
                "startColumnIndex": summary_col_start_idx,
                "endColumnIndex": summary_col_start_idx + 2
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95},  # Light grey
                    "textFormat": {
                        "fontSize": 10
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat)"
        }
    })
    
    # Borders around reminder section
    requests.append({
        "updateBorders": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": reminder_start_row,
                "endRowIndex": reminder_end_row,
                "startColumnIndex": summary_col_start_idx,
                "endColumnIndex": summary_col_start_idx + 2
            },
            "top": {"style": "SOLID", "width": 2, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
            "bottom": {"style": "SOLID", "width": 2, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
            "left": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
            "right": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
            "innerHorizontal": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
            "innerVertical": {"style": "SOLID", "width": 1, "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}
        }
    })
    
    # Add borders to summary section (metrics only, rows 0-9)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": 9,
                "startColumnIndex": summary_col_start_idx,
                "endColumnIndex": summary_col_start_idx + 2
            },
            "cell": {
                "userEnteredFormat": {
                    "borders": {
                        "top": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "left": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "right": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}}
                    }
                }
            },
            "fields": "userEnteredFormat.borders"
        }
    })
    
    # Set column widths
    requests.append({
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet.id,
                "dimension": "COLUMNS",
                "startIndex": summary_col_start_idx,
                "endIndex": summary_col_start_idx + 2
            },
            "properties": {
                "pixelSize": 150  # Wider columns for summary
            },
            "fields": "pixelSize"
        }
    })
    
    try:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("Added summary section on the right side")
    except Exception as e:
        logger.warning(f"Could not add summary section: {e}")


def cleanup_empty_columns(sheet, start_col: int, num_data_cols: int):
    """Remove borders and formatting from empty columns after the data columns"""
    requests = []
    
    # Remove borders and formatting from columns after the data
    data_end_col = start_col - 1 + num_data_cols  # End of data columns
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": 1000,
                "startColumnIndex": data_end_col,
                "endColumnIndex": 100  # Clear to column Z and beyond
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},  # White
                    "borders": {
                        "top": {"style": "NONE"},
                        "bottom": {"style": "NONE"},
                        "left": {"style": "NONE"},
                        "right": {"style": "NONE"}
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,borders)"
        }
    })
    
    try:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("Cleaned up empty columns (removed borders and formatting)")
    except Exception as e:
        logger.warning(f"Could not clean up empty columns: {e}")


def apply_size_formatting(sheet, headers: list, start_col: int):
    """Apply colors to Size column based on size value"""
    requests = []
    
    # Find Size column index
    if 'Size' not in headers:
        return
    
    col_start = start_col - 1  # Convert to 0-indexed
    size_col = col_start + headers.index('Size')
    
    # Color mapping for sizes
    size_colors = {
        'S': {"red": 0.85, "green": 0.92, "blue": 1.0},      # Light blue
        'M': {"red": 1.0, "green": 0.85, "blue": 0.85},     # Light red
        'L': {"red": 0.85, "green": 1.0, "blue": 0.85},     # Light green
        'XL': {"red": 1.0, "green": 1.0, "blue": 0.85},     # Light yellow
        'XXL': {"red": 1.0, "green": 0.9, "blue": 0.7},      # Light orange
    }
    
    index = 0
    for size, color in size_colors.items():
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet.id,
                        "startRowIndex": 1,  # Skip header
                        "endRowIndex": 1000,
                        "startColumnIndex": size_col,
                        "endColumnIndex": size_col + 1
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": size}]
                        },
                        "format": {
                            "backgroundColor": color
                        }
                    }
                },
                "index": index
            }
        })
        index += 1
    
    try:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("Applied size formatting (colors for S, M, L, XL, XXL)")
    except Exception as e:
        logger.warning(f"Could not apply size formatting: {e}")


def apply_order_status_formatting(sheet, headers: list, start_col: int):
    """Apply color coding to Order Status column"""
    requests = []
    
    if 'Order Status' not in headers:
        return
    
    col_start = start_col - 1
    status_col = col_start + headers.index('Order Status')
    
    # Color mapping for order status
    status_colors = {
        'Paid': {"red": 0.85, "green": 0.92, "blue": 0.85},      # Light green
        'Pending': {"red": 1.0, "green": 0.95, "blue": 0.8},    # Light yellow
        'Refunded': {"red": 1.0, "green": 0.8, "blue": 0.8},    # Light red
        'Partially Refunded': {"red": 1.0, "green": 0.9, "blue": 0.8},  # Light orange
        'Authorized': {"red": 0.9, "green": 0.9, "blue": 1.0},  # Light blue
    }
    
    index = 0
    for status, color in status_colors.items():
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
                            "values": [{"userEnteredValue": status}]
                        },
                        "format": {
                            "backgroundColor": color
                        }
                    }
                },
                "index": index
            }
        })
        index += 1
    
    try:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("Applied order status formatting (color coded)")
    except Exception as e:
        logger.warning(f"Could not apply order status formatting: {e}")


def apply_shipping_status_formatting(sheet, headers: list, start_col: int):
    """Apply color coding to Shipping Status column"""
    requests = []
    
    if 'Shipping Status' not in headers:
        return
    
    col_start = start_col - 1
    shipping_col = col_start + headers.index('Shipping Status')
    
    # Color mapping for shipping status
    shipping_colors = {
        'Shipped': {"red": 0.85, "green": 0.92, "blue": 0.85},      # Light green
        'Delivered': {"red": 0.8, "green": 0.95, "blue": 0.8},    # Darker green
        'Pending': {"red": 1.0, "green": 0.95, "blue": 0.8},      # Light yellow
        'Unfulfilled': {"red": 1.0, "green": 0.85, "blue": 0.85},  # Light red
        'Partial': {"red": 1.0, "green": 0.9, "blue": 0.8},       # Light orange
    }
    
    index = 0
    for status, color in shipping_colors.items():
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": shipping_col,
                        "endColumnIndex": shipping_col + 1
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": status}]
                        },
                        "format": {
                            "backgroundColor": color
                        }
                    }
                },
                "index": index
            }
        })
        index += 1
    
    try:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("Applied shipping status formatting (color coded)")
    except Exception as e:
        logger.warning(f"Could not apply shipping status formatting: {e}")


def create_financial_tracking_sheet(manager: SheetsManager, orders_output: pd.DataFrame, orders_df: pd.DataFrame):
    """Create Financial Tracking sheet with daily/weekly revenue trends and summary data"""
    logger.info("Creating/Updating Financial Tracking sheet...")
    
    try:
        # Get or create Financial Tracking sheet
        tracking_sheet = manager.create_sheet_if_not_exists("Financial Tracking")
        
        # Clear existing data
        try:
            tracking_sheet.clear()
        except:
            pass
        
        # Prepare data for daily and weekly summaries
        if not orders_output.empty and 'Date' in orders_output.columns and 'Sold Price' in orders_output.columns:
            # Filter out excluded orders (same as summary section)
            valid_orders = orders_output[
                (orders_output['Order Status'] != 'Partially Refunded') &
                (~orders_output['Shipping Status'].isin(['Unfulfilled', 'Partial']))
            ].copy()
            
            if 'Date' in valid_orders.columns and len(valid_orders) > 0:
                valid_orders['Date'] = pd.to_datetime(valid_orders['Date'], errors='coerce')
                valid_orders = valid_orders.dropna(subset=['Date'])
                
                if len(valid_orders) > 0:
                    # Daily Revenue Summary
                    daily_revenue = valid_orders.groupby(valid_orders['Date'].dt.date).agg({
                        'Sold Price': 'sum',
                        'Shipping Cost': 'sum',
                        'Quantity': 'sum',
                        'Profit': 'sum'
                    }).reset_index()
                    daily_revenue.columns = ['Date', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit']
                    daily_revenue = daily_revenue.sort_values('Date')
                    
                    # Weekly Revenue Summary
                    valid_orders['Year'] = valid_orders['Date'].dt.year
                    valid_orders['Week'] = valid_orders['Date'].dt.isocalendar().week
                    valid_orders['Week_Start'] = valid_orders['Date'] - pd.to_timedelta(valid_orders['Date'].dt.dayofweek, unit='d')
                    
                    weekly_revenue = valid_orders.groupby(['Year', 'Week', 'Week_Start']).agg({
                        'Sold Price': 'sum',
                        'Shipping Cost': 'sum',
                        'Quantity': 'sum',
                        'Profit': 'sum'
                    }).reset_index()
                    weekly_revenue.columns = ['Year', 'Week', 'Week Start', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit']
                    weekly_revenue = weekly_revenue.sort_values('Week Start')
                    weekly_revenue['Week Start'] = weekly_revenue['Week Start'].dt.date
                    
                    # Monthly Revenue Summary
                    valid_orders['Month'] = valid_orders['Date'].dt.to_period('M')
                    monthly_revenue = valid_orders.groupby('Month').agg({
                        'Sold Price': 'sum',
                        'Shipping Cost': 'sum',
                        'Quantity': 'sum',
                        'Profit': 'sum'
                    }).reset_index()
                    monthly_revenue['Month'] = monthly_revenue['Month'].astype(str)
                    monthly_revenue.columns = ['Month', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit']
                else:
                    daily_revenue = pd.DataFrame(columns=['Date', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit'])
                    weekly_revenue = pd.DataFrame(columns=['Year', 'Week', 'Week Start', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit'])
                    monthly_revenue = pd.DataFrame(columns=['Month', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit'])
            else:
                daily_revenue = pd.DataFrame(columns=['Date', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit'])
                weekly_revenue = pd.DataFrame(columns=['Year', 'Week', 'Week Start', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit'])
                monthly_revenue = pd.DataFrame(columns=['Month', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit'])
        else:
            daily_revenue = pd.DataFrame(columns=['Date', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit'])
            weekly_revenue = pd.DataFrame(columns=['Year', 'Week', 'Week Start', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit'])
            monthly_revenue = pd.DataFrame(columns=['Month', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit'])
        
        # Calculate summary metrics
        if not orders_output.empty:
            valid_orders = orders_output[
                (orders_output['Order Status'] != 'Partially Refunded') &
                (~orders_output['Shipping Status'].isin(['Unfulfilled', 'Partial']))
            ].copy()
            total_revenue = valid_orders['Sold Price'].sum() if not valid_orders.empty else 0
            total_shipping = valid_orders['Shipping Cost'].sum() if not valid_orders.empty else 0
            total_units = valid_orders['Quantity'].sum() if not valid_orders.empty else 0
            total_profit = valid_orders['Profit'].sum() if not valid_orders.empty else 0
            avg_order_value = total_revenue / len(valid_orders) if len(valid_orders) > 0 else 0
            avg_profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        else:
            total_revenue = total_shipping = total_units = total_profit = avg_order_value = avg_profit_margin = 0
        
        # Write summary section at the top
        summary_data = [
            ['FINANCIAL SUMMARY', ''],
            ['Total Revenue', f'${total_revenue:,.2f}'],
            ['Total Shipping Revenue', f'${total_shipping:,.2f}'],
            ['Total Units Sold', f'{int(total_units)}'],
            ['Total Profit', f'${total_profit:,.2f}'],
            ['Average Order Value', f'${avg_order_value:,.2f}'],
            ['Average Profit Margin %', f'{avg_profit_margin:.2f}%'],
            ['', ''],
            ['', '']
        ]
        
        tracking_sheet.update('A1', summary_data, value_input_option='USER_ENTERED')
        
        # Write Daily Revenue Trends
        daily_start_row = len(summary_data) + 2
        daily_headers = [['DAILY REVENUE TRENDS'], ['Date', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit']]
        # Convert dates to strings for JSON serialization
        if not daily_revenue.empty:
            daily_revenue_copy = daily_revenue.copy()
            daily_revenue_copy['Date'] = daily_revenue_copy['Date'].astype(str)
            daily_values = daily_revenue_copy.values.tolist()
        else:
            daily_values = []
        
        tracking_sheet.update(f'A{daily_start_row}', daily_headers + daily_values, value_input_option='USER_ENTERED')
        
        # Write Weekly Revenue Trends
        weekly_start_row = daily_start_row + len(daily_headers) + len(daily_values) + 3
        weekly_headers = [['WEEKLY REVENUE TRENDS'], ['Week Start', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit']]
        # Convert dates to strings for JSON serialization
        if not weekly_revenue.empty:
            weekly_revenue_copy = weekly_revenue[['Week Start', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit']].copy()
            weekly_revenue_copy['Week Start'] = weekly_revenue_copy['Week Start'].astype(str)
            weekly_values = weekly_revenue_copy.values.tolist()
        else:
            weekly_values = []
        
        tracking_sheet.update(f'A{weekly_start_row}', weekly_headers + weekly_values, value_input_option='USER_ENTERED')
        
        # Write Monthly Revenue Trends
        monthly_start_row = weekly_start_row + len(weekly_headers) + len(weekly_values) + 3
        monthly_headers = [['MONTHLY REVENUE TRENDS'], ['Month', 'Revenue', 'Shipping Revenue', 'Units Sold', 'Profit']]
        monthly_values = monthly_revenue.values.tolist() if not monthly_revenue.empty else []
        
        tracking_sheet.update(f'A{monthly_start_row}', monthly_headers + monthly_values, value_input_option='USER_ENTERED')
        
        # Format the sheet
        format_financial_tracking_sheet(tracking_sheet, daily_start_row, weekly_start_row, monthly_start_row, 
                                       len(daily_values), len(weekly_values), len(monthly_values))
        
        logger.info("Financial Tracking sheet created/updated successfully!")
        
    except Exception as e:
        logger.error(f"Error creating Financial Tracking sheet: {e}", exc_info=True)


def format_financial_tracking_sheet(sheet, daily_start: int, weekly_start: int, monthly_start: int,
                                   daily_rows: int, weekly_rows: int, monthly_rows: int):
    """Format the Financial Tracking sheet"""
    requests = []
    
    # Format summary section (rows 1-9)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": 8,
                "startColumnIndex": 0,
                "endColumnIndex": 2
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.26, "green": 0.52, "blue": 0.96},  # Google blue
                    "textFormat": {
                        "bold": True,
                        "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}  # White
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat)"
        }
    })
    
    # Format section headers (bold, larger)
    section_rows = [daily_start - 1, weekly_start - 1, monthly_start - 1]
    for row_idx in section_rows:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": row_idx,
                    "endRowIndex": row_idx + 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 5
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1.0, "green": 0.65, "blue": 0.0},  # Orange
                        "textFormat": {
                            "bold": True,
                            "fontSize": 12,
                            "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)"
            }
        })
    
    # Format table headers (orange background, bold)
    table_header_rows = [daily_start, weekly_start, monthly_start]
    for row_idx in table_header_rows:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": row_idx,
                    "endRowIndex": row_idx + 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 5
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 1.0, "green": 0.65, "blue": 0.0},  # Orange
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        })
    
    # Add borders to all data tables
    all_data_end = monthly_start + monthly_rows + 2
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": all_data_end,
                "startColumnIndex": 0,
                "endColumnIndex": 5
            },
            "cell": {
                "userEnteredFormat": {
                    "borders": {
                        "top": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "left": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "right": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}}
                    }
                }
            },
            "fields": "userEnteredFormat.borders"
        }
    })
    
    # Format currency columns (Revenue, Shipping Revenue, Profit)
    currency_cols = [1, 2, 4]  # Columns B, C, E (0-indexed: 1, 2, 4)
    for col_idx in currency_cols:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 1,  # Skip summary header
                    "endRowIndex": all_data_end,
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
    
    # Center align all data
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": all_data_end,
                "startColumnIndex": 0,
                "endColumnIndex": 5
            },
            "cell": {
                "userEnteredFormat": {
                    "horizontalAlignment": "CENTER"
                }
            },
            "fields": "userEnteredFormat.horizontalAlignment"
        }
    })
    
    try:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("Formatted Financial Tracking sheet")
    except Exception as e:
        logger.warning(f"Could not format Financial Tracking sheet: {e}")


def apply_strikethrough_for_refunded(sheet, orders_output: pd.DataFrame, headers: list, start_col: int):
    """Apply strikethrough formatting to entire rows for Partially Refunded orders"""
    if orders_output.empty:
        return
    
    # Find Order Status column
    if 'Order Status' not in headers:
        return
    
    order_status_col = start_col - 1 + headers.index('Order Status')  # 0-indexed
    
    # Find rows with "Partially Refunded" status
    if 'Order Status' not in orders_output.columns:
        return
    
    refunded_rows = orders_output[orders_output['Order Status'] == 'Partially Refunded'].index
    
    if len(refunded_rows) == 0:
        return
    
    requests = []
    
    # For each refunded row, apply strikethrough to all columns
    for row_idx in refunded_rows:
        # Row index in sheet: row_idx is 0-indexed from DataFrame, row 1 is header in sheet
        # So row 0 in DataFrame = row 2 in sheet (row 1 is header)
        sheet_row_idx = row_idx + 2  # +2 because row 1 is header (1-indexed)
        
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": sheet_row_idx,
                    "endRowIndex": sheet_row_idx + 1,
                    "startColumnIndex": start_col - 1,  # Start from first data column
                    "endColumnIndex": start_col - 1 + len(headers)  # End at last column
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "strikethrough": True
                        }
                    }
                },
                "fields": "userEnteredFormat.textFormat.strikethrough"
            }
        })
    
    try:
        if requests:
            sheet.spreadsheet.batch_update({"requests": requests})
            logger.info(f"Applied strikethrough to {len(refunded_rows)} partially refunded order rows")
    except Exception as e:
        logger.warning(f"Could not apply strikethrough formatting: {e}")


def format_psl_column(sheet, headers: list, start_col: int, num_rows: int):
    """Format the PSL (Private Shipping Label) column to make it clear it's for user input"""
    if 'PSL' not in headers or num_rows == 0:
        return
    
    psl_col = start_col - 1 + headers.index('PSL')
    
    requests = []
    
    # Light yellow background to indicate it's an input field
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 1,  # Skip header
                "endRowIndex": num_rows + 1,
                "startColumnIndex": psl_col,
                "endColumnIndex": psl_col + 1
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.9},  # Light yellow
                    "textFormat": {
                        "italic": True  # Italic to indicate it's for user input
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat)"
        }
    })
    
    try:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("Formatted PSL column")
    except Exception as e:
        logger.warning(f"Could not format PSL column: {e}")


def delete_unused_sheets(manager: SheetsManager):
    """Delete unused sheets (Customers, Products, Inventory) if they exist"""
    logger.info("Checking for unused sheets to delete...")
    
    sheets_to_delete = ['Customers', 'Products', 'Inventory']
    
    try:
        import gspread
        for sheet_name in sheets_to_delete:
            try:
                sheet = manager.spreadsheet.worksheet(sheet_name)
                manager.spreadsheet.del_worksheet(sheet)
                logger.info(f"Deleted sheet: {sheet_name}")
            except gspread.exceptions.WorksheetNotFound:
                logger.info(f"Sheet '{sheet_name}' does not exist, skipping")
            except Exception as e:
                logger.warning(f"Could not delete sheet '{sheet_name}': {e}")
    except Exception as e:
        logger.warning(f"Error deleting unused sheets: {e}")


def create_inventory_sheet(manager: SheetsManager, shopify: ShopifyClient):
    """Create or update Inventory tracking sheet next to Orders sheet"""
    logger.info("Creating/Updating Inventory tracking sheet...")
    
    try:
        # Get or create Inventory sheet
        inventory_sheet = manager.create_sheet_if_not_exists("Inventory")
        
        # Clear existing data
        try:
            inventory_sheet.clear()
        except:
            pass
        
        # Fetch products from Shopify
        logger.info("Fetching products from Shopify...")
        products = shopify.get_products()
        
        # Try to fetch inventory levels (may require special permissions)
        inventory_levels = {}
        try:
            logger.info("Fetching inventory levels from Shopify...")
            inventory_levels = shopify.get_inventory_levels()
        except Exception as e:
            logger.warning(f"Could not fetch inventory levels (may require special permissions): {e}")
            logger.info("Using variant inventory_quantity instead...")
        
        # Build product variant inventory data
        inventory_data = []
        
        # Map product variants to inventory
        for product in products:
            product_title = product.get('title', '')
            variants = product.get('variants', [])
            
            for variant in variants:
                variant_id = variant.get('id', '')
                variant_title = variant.get('title', '') or 'Default'
                sku = variant.get('sku', '')
                inventory_item_id = variant.get('inventory_item_id')
                
                # Get current inventory from Shopify
                # Try inventory_levels API first, fall back to variant inventory_quantity
                current_stock = 0
                if inventory_item_id and inventory_item_id in inventory_levels:
                    current_stock = inventory_levels[inventory_item_id].get('available', 0)
                else:
                    # Fall back to variant's inventory_quantity field
                    current_stock = variant.get('inventory_quantity', 0) or 0
                
                # Normalize size format (match what's used in Orders sheet: S, M, L, XL)
                size = variant_title.strip() if variant_title != 'Default Title' else ''
                
                # Normalize size names to match Orders sheet format
                size_map = {
                    'Small': 'S', 'small': 'S', 'S': 'S',
                    'Medium': 'M', 'medium': 'M', 'M': 'M',
                    'Large': 'L', 'large': 'L', 'L': 'L',
                    'Extra Large': 'XL', 'Extra-Large': 'XL', 'XL': 'XL', 'X-Large': 'XL'
                }
                size = size_map.get(size, size) if size else ''
                
                # Skip if size is empty or not in our list
                if size not in ['S', 'M', 'L', 'XL']:
                    continue
                
                # Use current stock from Shopify (actual inventory levels)
                # This will be the starting stock that gets updated
                starting_stock = current_stock
                
                inventory_data.append({
                    'Product Name': product_title,
                    'Size': size,
                    'SKU': sku,
                    'Variant ID': variant_id,
                    'Starting Stock': starting_stock
                })
        
        if not inventory_data:
            logger.warning("No product variants found")
            return
        
        # Create DataFrame
        inventory_df = pd.DataFrame(inventory_data)
        
        # Define size order for sorting: Small (S), Medium (M), Large (L), XL
        size_order = {'S': 0, 'M': 1, 'L': 2, 'XL': 3}
        inventory_df['Size_Order'] = inventory_df['Size'].map(size_order)
        
        # Sort by Product Name, then by Size order (Small, Medium, Large, XL)
        inventory_df = inventory_df.sort_values(['Product Name', 'Size_Order']).reset_index(drop=True)
        inventory_df = inventory_df.drop('Size_Order', axis=1)
        
        # Headers
        headers = ['Product Name', 'Size', 'Starting Stock', 'Quantity Sold', 'Remaining Stock', 'Low Stock Warning']
        
        # Write headers
        header_range = 'A1'
        inventory_sheet.update(header_range, [headers])
        
        # Prepare data rows with formulas
        data_rows = []
        for idx, row in inventory_df.iterrows():
            product_name = row['Product Name']
            size = row['Size']
            starting_stock = row['Starting Stock']
            
            # Formula to sum quantities sold from Orders sheet
            # Sum quantities where Product Name matches AND Size matches AND Order Status is not Partially Refunded
            # AND Shipping Status is not Unfulfilled/Partial
            sold_formula = f"=SUMIFS(Orders!D:D, Orders!B:B, \"{product_name}\", Orders!C:C, \"{size}\", Orders!J:J, \"<>Partially Refunded\", Orders!K:K, \"<>Unfulfilled\", Orders!K:K, \"<>Partial\")"
            
            # Remaining Stock formula: Starting Stock - Quantity Sold
            remaining_formula = f"=C{idx+2}-D{idx+2}"
            
            # Low Stock Warning formula: Show "LOW" if remaining < 5, else empty
            warning_formula = f"=IF(E{idx+2}<5, \"LOW\", \"\")"
            
            data_rows.append([
                product_name,
                size,
                starting_stock,
                sold_formula,
                remaining_formula,
                warning_formula
            ])
        
        # Write data
        if data_rows:
            data_range = f'A2:F{len(data_rows) + 1}'
            inventory_sheet.update(data_range, data_rows, value_input_option='USER_ENTERED')
        
        # Format the sheet
        format_inventory_sheet(inventory_sheet, len(data_rows), inventory_df)
        
        logger.info("Inventory sheet created/updated successfully!")
        
    except Exception as e:
        logger.error(f"Error creating inventory sheet: {e}", exc_info=True)


def format_inventory_sheet(sheet, num_rows: int, inventory_df: pd.DataFrame):
    """Format the Inventory sheet with borders, colors, and conditional formatting"""
    requests = []
    
    # Header formatting (orange background, bold, centered)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": 0,
                "endColumnIndex": 6
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 1.0, "green": 0.65, "blue": 0.0},  # Orange
                    "textFormat": {
                        "bold": True,
                        "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}
                    },
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE"
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
        }
    })
    
    # Add borders to all data
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 0,
                "endRowIndex": num_rows + 1,
                "startColumnIndex": 0,
                "endColumnIndex": 6
            },
            "cell": {
                "userEnteredFormat": {
                    "borders": {
                        "top": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "left": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}},
                        "right": {"style": "SOLID", "width": 1, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}}
                    }
                }
            },
            "fields": "userEnteredFormat.borders"
        }
    })
    
    # Center align all columns
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet.id,
                "startRowIndex": 1,
                "endRowIndex": num_rows + 1,
                "startColumnIndex": 0,
                "endColumnIndex": 6
            },
            "cell": {
                "userEnteredFormat": {
                    "horizontalAlignment": "CENTER"
                }
            },
            "fields": "userEnteredFormat.horizontalAlignment"
        }
    })
    
    # Format number columns (Starting Stock, Quantity Sold, Remaining Stock)
    for col_idx in [2, 3, 4]:  # Columns C, D, E (0-indexed: 2, 3, 4)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows + 1,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "NUMBER",
                            "pattern": "0"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })
    
    # Conditional formatting: Red background for Low Stock Warning cells with "LOW"
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet.id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows + 1,
                    "startColumnIndex": 5,  # Low Stock Warning column
                    "endColumnIndex": 6
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_EQ",
                        "values": [{"userEnteredValue": "LOW"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 1.0, "green": 0.7, "blue": 0.7}  # Light red
                    }
                }
            },
            "index": 0
        }
    })
    
    # Conditional formatting: Yellow background for Remaining Stock < 10
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet.id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows + 1,
                    "startColumnIndex": 4,  # Remaining Stock column
                    "endColumnIndex": 5
                }],
                "booleanRule": {
                    "condition": {
                        "type": "NUMBER_LESS",
                        "values": [{"userEnteredValue": "10"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.7}  # Light yellow
                    }
                }
            },
            "index": 0
        }
    })
    
    # Conditional formatting: Red background for Remaining Stock < 5
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet.id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows + 1,
                    "startColumnIndex": 4,  # Remaining Stock column
                    "endColumnIndex": 5
                }],
                "booleanRule": {
                    "condition": {
                        "type": "NUMBER_LESS",
                        "values": [{"userEnteredValue": "5"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 1.0, "green": 0.7, "blue": 0.7}  # Light red
                    }
                }
            },
            "index": 1  # Higher priority than yellow
        }
    })
    
    # Apply product name colors (same as Orders sheet)
    # Grey background for Arcus Tee, Purple background for All Paths Tee
    product_name_col = 0  # Column A (0-indexed)
    
    # Grey for Arcus Tee
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet.id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows + 1,
                    "startColumnIndex": product_name_col,
                    "endColumnIndex": product_name_col + 1
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_CONTAINS",
                        "values": [{"userEnteredValue": "Arcus"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 0.7, "green": 0.7, "blue": 0.7}  # Darker grey
                    }
                }
            },
            "index": 0
        }
    })
    
    # Purple for All Paths Tee
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet.id,
                    "startRowIndex": 1,
                    "endRowIndex": num_rows + 1,
                    "startColumnIndex": product_name_col,
                    "endColumnIndex": product_name_col + 1
                }],
                "booleanRule": {
                    "condition": {
                        "type": "TEXT_CONTAINS",
                        "values": [{"userEnteredValue": "All Paths"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 0.8, "green": 0.7, "blue": 0.9}  # Purple
                    }
                }
            },
            "index": 1
        }
    })
    
    # Apply size colors (same as Orders sheet)
    size_col = 1  # Column B (0-indexed)
    size_colors = {
        'S': {"red": 0.85, "green": 0.92, "blue": 1.0},      # Light blue
        'M': {"red": 1.0, "green": 0.85, "blue": 0.85},     # Light red
        'L': {"red": 0.85, "green": 1.0, "blue": 0.85},     # Light green
        'XL': {"red": 1.0, "green": 1.0, "blue": 0.85},     # Light yellow
    }
    
    format_index = 2  # Start after product name rules
    for size, color in size_colors.items():
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": num_rows + 1,
                        "startColumnIndex": size_col,
                        "endColumnIndex": size_col + 1
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": size}]
                        },
                        "format": {
                            "backgroundColor": color
                        }
                    }
                },
                "index": format_index
            }
        })
        format_index += 1
    
    # Set column widths
    requests.append({
        "updateDimensionProperties": {
            "range": {
                "sheetId": sheet.id,
                "dimension": "COLUMNS",
                "startIndex": 0,
                "endIndex": 6
            },
            "properties": {
                "pixelSize": 120
            },
            "fields": "pixelSize"
        }
    })
    
    try:
        sheet.spreadsheet.batch_update({"requests": requests})
        logger.info("Formatted Inventory sheet with product name and size colors")
    except Exception as e:
        logger.warning(f"Could not format Inventory sheet: {e}")


if __name__ == "__main__":
    update_orders_sheet()

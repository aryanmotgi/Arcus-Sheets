"""
One-time migration script to move PSL values from old Orders sheet to MANUAL_OVERRIDES
"""
import logging
from pathlib import Path
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from environment variables or config.yaml"""
    import os
    
    config = {}
    
    if os.getenv('SHOPIFY_STORE_URL'):
        config['shopify'] = {
            'store_url': os.getenv('SHOPIFY_STORE_URL'),
            'client_id': os.getenv('SHOPIFY_CLIENT_ID', ''),
            'client_secret': os.getenv('SHOPIFY_CLIENT_SECRET', '')
        }
    
    if os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'):
        config['google_sheets'] = {
            'spreadsheet_id': os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'),
            'service_account_path': os.getenv('GOOGLE_CREDENTIALS')
        }
    
    if config.get('shopify') and config.get('google_sheets'):
        return config
    
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            file_config = yaml.safe_load(f)
            if file_config:
                return file_config
    
    raise ValueError("Configuration not found!")


def migrate_psl_values():
    """
    Migrate PSL values from old Orders sheet to MANUAL_OVERRIDES
    
    Process:
    1. Read PSL column from Orders sheet (or RAW_ORDERS if exists)
    2. Match by order_number → resolve order_id
    3. Insert into MANUAL_OVERRIDES
    4. Skip rows already present
    """
    logger.info("=" * 60)
    logger.info("PSL Migration Script - Moving PSL values to MANUAL_OVERRIDES")
    logger.info("=" * 60)
    
    config = load_config()
    
    # Initialize sheets manager
    import os
    from sheets_manager import SheetsManager
    
    google_credentials_json = os.getenv('GOOGLE_CREDENTIALS')
    service_account_path = config['google_sheets'].get('service_account_path')
    
    manager = SheetsManager(
        spreadsheet_id=config['google_sheets']['spreadsheet_id'],
        service_account_path=service_account_path if not google_credentials_json else None,
        google_credentials_json=google_credentials_json
    )
    
    # Ensure MANUAL_OVERRIDES exists
    manager.create_manual_overrides_sheet()
    
    # Try to read from old Orders sheet first, then RAW_ORDERS
    source_sheet_name = None
    source_sheet = None
    
    for sheet_name in ["Orders", "RAW_ORDERS"]:
        try:
            source_sheet = manager.create_sheet_if_not_exists(sheet_name)
            source_sheet_name = sheet_name
            logger.info(f"Found source sheet: {sheet_name}")
            break
        except:
            continue
    
    if not source_sheet:
        logger.error("Could not find Orders or RAW_ORDERS sheet!")
        return
    
    # Read source data
    logger.info(f"Reading PSL values from {source_sheet_name}...")
    source_data = source_sheet.get_all_values()
    
    if not source_data or len(source_data) < 2:
        logger.warning(f"{source_sheet_name} is empty, nothing to migrate")
        return
    
    headers = source_data[0]
    
    # Find PSL column
    try:
        psl_col_idx = headers.index("PSL")
    except ValueError:
        try:
            psl_col_idx = headers.index("psl")
        except ValueError:
            logger.error("PSL column not found in source sheet!")
            return
    
    # Find order_number and order_id columns
    try:
        order_num_col_idx = headers.index("Order Number")
    except ValueError:
        try:
            order_num_col_idx = headers.index("order_number")
        except ValueError:
            logger.error("Order Number column not found!")
            return
    
    try:
        order_id_col_idx = headers.index("Order ID")
    except ValueError:
        try:
            order_id_col_idx = headers.index("order_id")
        except ValueError:
            order_id_col_idx = None
            logger.warning("Order ID column not found, will try to resolve from order_number")
    
    # Get existing MANUAL_OVERRIDES to avoid duplicates
    existing_overrides = manager.get_all_manual_overrides()
    existing_order_ids = {o.get('order_id', '') for o in existing_overrides}
    existing_order_nums = {o.get('order_number', '') for o in existing_overrides}
    
    # Migration stats
    migrated = 0
    skipped = 0
    failed = 0
    
    logger.info(f"Found {len(source_data) - 1} rows to process")
    logger.info(f"Existing overrides: {len(existing_overrides)}")
    
    # Process each row
    for row_idx, row in enumerate(source_data[1:], start=2):
        if len(row) <= max(psl_col_idx, order_num_col_idx):
            continue
        
        # Get PSL value
        psl_value = str(row[psl_col_idx]).strip() if len(row) > psl_col_idx else ""
        
        # Skip if PSL is empty
        if not psl_value or psl_value == "" or psl_value == "0":
            skipped += 1
            continue
        
        # Get order_number and order_id
        order_number = str(row[order_num_col_idx]).strip() if len(row) > order_num_col_idx else ""
        order_id = None
        
        if order_id_col_idx and len(row) > order_id_col_idx:
            order_id = str(row[order_id_col_idx]).strip()
        
        if not order_number:
            logger.warning(f"Row {row_idx}: No order_number, skipping")
            failed += 1
            continue
        
        # Check if already exists
        if order_id and order_id in existing_order_ids:
            logger.debug(f"Order {order_number} (ID: {order_id}) already in MANUAL_OVERRIDES, skipping")
            skipped += 1
            continue
        
        if order_number in existing_order_nums:
            logger.debug(f"Order {order_number} already in MANUAL_OVERRIDES, skipping")
            skipped += 1
            continue
        
        # If no order_id, try to find it from RAW_ORDERS or ORDERS
        if not order_id:
            # Try to look it up
            try:
                lookup_sheet = manager.create_sheet_if_not_exists("RAW_ORDERS")
                lookup_data = lookup_sheet.get_all_values()
                if lookup_data and len(lookup_data) > 1:
                    lookup_headers = lookup_data[0]
                    try:
                        lookup_num_col = lookup_headers.index("Order Number")
                        lookup_id_col = lookup_headers.index("Order ID")
                        for lookup_row in lookup_data[1:]:
                            if len(lookup_row) > lookup_num_col and str(lookup_row[lookup_num_col]) == order_number:
                                if len(lookup_row) > lookup_id_col:
                                    order_id = str(lookup_row[lookup_id_col])
                                    break
                    except ValueError:
                        pass
            except:
                pass
        
        # Migrate to MANUAL_OVERRIDES
        try:
            manager.upsert_manual_override(
                order_id=order_id or "",
                order_number=order_number,
                psl=psl_value,
                updated_by="migration"
            )
            migrated += 1
            if migrated % 10 == 0:
                logger.info(f"Migrated {migrated} PSL values...")
        except Exception as e:
            logger.error(f"Error migrating row {row_idx} (order {order_number}): {e}")
            failed += 1
    
    # Summary
    logger.info("=" * 60)
    logger.info("Migration Complete!")
    logger.info(f"✅ Migrated: {migrated}")
    logger.info(f"⏭️  Skipped: {skipped}")
    logger.info(f"❌ Failed: {failed}")
    logger.info("=" * 60)
    
    return {
        'migrated': migrated,
        'skipped': skipped,
        'failed': failed
    }


if __name__ == "__main__":
    migrate_psl_values()

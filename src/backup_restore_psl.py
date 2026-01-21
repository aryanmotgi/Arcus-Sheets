"""
PSL Backup/Restore Tool

This script allows you to backup and restore PSL (Private Shipping Label) values
from your Google Sheets. Use this BEFORE running the main sync to preserve your manual entries.

Usage:
    python src/backup_restore_psl.py backup    - Save PSL values to a file
    python src/backup_restore_psl.py restore   - Restore PSL values from backup file
"""

import json
import sys
import logging
from pathlib import Path
import yaml
from sheets_manager import SheetsManager

def load_config():
    """Load configuration from environment variables or config.yaml"""
    import os
    
    # Try environment variables first
    config = {}
    
    if os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'):
        config['google_sheets'] = {
            'spreadsheet_id': os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'),
            'service_account_path': os.getenv('GOOGLE_CREDENTIALS')  # Will be handled differently
        }
    
    if config.get('google_sheets'):
        return config
    
    # Fall back to config.yaml
    config_path = Path('config/config.yaml')
    if config_path.exists():
        with open(config_path, 'r') as f:
            file_config = yaml.safe_load(f)
            if file_config:
                return file_config
    
    raise ValueError("Configuration not found! Set GOOGLE_SHEETS_SPREADSHEET_ID and GOOGLE_CREDENTIALS")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BACKUP_FILE = Path('config/psl_backup.json')


def backup_psl_values():
    """Backup PSL values from Google Sheets to a JSON file"""
    logger.info("Starting PSL backup...")
    
    config = load_config()
    if not config:
        logger.error("Failed to load config")
        return False
    
    try:
        manager = SheetsManager(
            spreadsheet_id=config['google_sheets']['spreadsheet_id'],
            service_account_path=config['google_sheets']['service_account_path']
        )
        sheet = manager.create_sheet_if_not_exists("Orders")
        
        # Read PSL column (column G) - read up to row 100
        psl_values = {}
        psl_col_letter = 'G'
        
        logger.info(f"Reading PSL values from column {psl_col_letter}...")
        
        # Read range G2:G100 in one call (more efficient)
        try:
            psl_range = f'{psl_col_letter}2:{psl_col_letter}100'
            psl_data = sheet.get_values(psl_range)
            
            for idx, row in enumerate(psl_data, start=2):
                if row and len(row) > 0:
                    psl_val = row[0] if isinstance(row, list) else row
                    if psl_val and str(psl_val).strip() != '':
                        psl_val_str = str(psl_val).strip()
                        psl_val_clean = psl_val_str.replace('$', '').replace(',', '').strip()
                        if psl_val_clean != '' and psl_val_clean != '0':
                            psl_values[idx] = psl_val_str
                            
        except Exception as e:
            logger.warning(f"Range read failed: {e}. Trying individual cells...")
            # Fallback: read individual cells (slower but more reliable)
            for row_num in range(2, 101):
                try:
                    cell_ref = f'{psl_col_letter}{row_num}'
                    cell_value = sheet.acell(cell_ref, value_render_option='FORMATTED_VALUE').value
                    if cell_value and str(cell_value).strip() != '':
                        psl_val_str = str(cell_value).strip()
                        psl_val_clean = psl_val_str.replace('$', '').replace(',', '').strip()
                        if psl_val_clean != '' and psl_val_clean != '0':
                            psl_values[row_num] = psl_val_str
                except Exception:
                    continue
        
        logger.info(f"Found {len(psl_values)} PSL values")
        
        if len(psl_values) == 0:
            logger.warning("No PSL values found in the sheet!")
            return False
        
        # Save to backup file
        BACKUP_FILE.parent.mkdir(exist_ok=True)
        with open(BACKUP_FILE, 'w') as f:
            json.dump(psl_values, f, indent=2)
        
        logger.info(f"✓ Backup saved to {BACKUP_FILE}")
        logger.info(f"  Backed up {len(psl_values)} PSL values:")
        for row_num, value in list(psl_values.items())[:5]:
            logger.info(f"    Row {row_num}: {value}")
        if len(psl_values) > 5:
            logger.info(f"    ... and {len(psl_values) - 5} more")
        
        return True
        
    except Exception as e:
        logger.error(f"Error backing up PSL values: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def restore_psl_values():
    """Restore PSL values from backup file to Google Sheets"""
    logger.info("Starting PSL restore...")
    
    if not BACKUP_FILE.exists():
        logger.error(f"Backup file not found: {BACKUP_FILE}")
        logger.info("Please run 'python src/backup_restore_psl.py backup' first")
        return False
    
    try:
        # Load backup
        with open(BACKUP_FILE, 'r') as f:
            psl_values = json.load(f)
        
        logger.info(f"Loaded {len(psl_values)} PSL values from backup")
        
        config = load_config()
        if not config:
            logger.error("Failed to load config")
            return False
        
        manager = SheetsManager(
            spreadsheet_id=config['google_sheets']['spreadsheet_id'],
            service_account_path=config['google_sheets']['service_account_path']
        )
        sheet = manager.create_sheet_if_not_exists("Orders")
        
        psl_col_letter = 'G'
        restored_count = 0
        
        logger.info(f"Restoring PSL values to column {psl_col_letter}...")
        
        # Restore values using individual cell writes
        for row_num, psl_value in psl_values.items():
            try:
                cell_ref = f'{psl_col_letter}{int(row_num)}'
                sheet.update_acell(cell_ref, str(psl_value))
                restored_count += 1
                if restored_count <= 5:
                    logger.info(f"  Restored row {row_num}: {psl_value}")
            except Exception as e:
                logger.warning(f"Failed to restore row {row_num}: {e}")
        
        logger.info(f"✓ Successfully restored {restored_count} PSL values")
        return True
        
    except Exception as e:
        logger.error(f"Error restoring PSL values: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'backup':
        success = backup_psl_values()
        sys.exit(0 if success else 1)
    elif command == 'restore':
        success = restore_psl_values()
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()

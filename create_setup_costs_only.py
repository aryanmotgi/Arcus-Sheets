"""
Quick script to create Setup and Costs sheet without running full sync
Run this locally to test: python create_setup_costs_only.py
"""
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sheets_manager import SheetsManager
from create_setup_costs_sheet import create_setup_costs_sheet

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from environment variables or config.yaml"""
    import os
    import yaml
    
    # Try to load from environment variables first
    config = {}
    
    # Google Sheets config from env
    if os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'):
        config['google_sheets'] = {
            'spreadsheet_id': os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'),
            'service_account_path': os.getenv('GOOGLE_CREDENTIALS')
        }
    
    # If we have env vars, return config
    if config.get('google_sheets'):
        return config
    
    # Fall back to config.yaml file
    config_path = Path(__file__).parent / "config" / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            file_config = yaml.safe_load(f)
            if file_config:
                return file_config
    
    # If neither exists, raise error
    raise ValueError(
        "Configuration not found! Please set GOOGLE_SHEETS_SPREADSHEET_ID and GOOGLE_CREDENTIALS "
        "or create config/config.yaml"
    )


def main():
    """Create Setup and Costs sheet"""
    logger.info("=" * 60)
    logger.info("Creating Setup and Costs sheet...")
    logger.info("=" * 60)
    
    try:
        config = load_config()
        
        # Initialize sheets manager
        import os
        google_credentials_json = os.getenv('GOOGLE_CREDENTIALS')
        service_account_path = config['google_sheets'].get('service_account_path')
        
        manager = SheetsManager(
            spreadsheet_id=config['google_sheets']['spreadsheet_id'],
            service_account_path=service_account_path if not google_credentials_json else None,
            google_credentials_json=google_credentials_json
        )
        
        # Create the sheet
        create_setup_costs_sheet(manager)
        
        logger.info("=" * 60)
        logger.info("✅ Setup and Costs sheet created successfully!")
        logger.info("=" * 60)
        logger.info("Go check your Google Sheet - you should see a new 'Setup and Costs' tab!")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

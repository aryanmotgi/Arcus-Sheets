import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load env from root
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, '.env'))

from sheets_manager import SheetsManager
from drop2_calculator import Drop2Calculator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ManualTrigger")

def main():
    print("Starting manual trigger for Drop 2 Finance Sheet (Data Type Fix)...")
    spreadsheet_id = "1wK6aA1Sny5Ie3Ef8gU8LMgaBMjpNKW7ol1pxVWmGihE"
    try:
        sheets_manager = SheetsManager(
            spreadsheet_id=spreadsheet_id,
            service_account_path="credentials/service_account.json"
        )
        print("Sheets Manager Initialized")
    except Exception as e:
        print(f"Failed: {e}")
        return

    try:
        calc = Drop2Calculator(sheets_manager)
        result = calc.create_prediction_sheet()
        print(f"RESULT: {result.get('message')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

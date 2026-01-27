"""
Sync Agent - Handles syncing orders from Shopify to Google Sheets
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SyncAgent:
    """Agent specialized in syncing orders from Shopify to Google Sheets"""
    
    def __init__(self, sheets_manager, shopify_client, config):
        """Initialize with SheetsManager, ShopifyClient, and config"""
        self.sheets_manager = sheets_manager
        self.shopify_client = shopify_client
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process sync-related commands
        
        Examples:
            - "sync orders"
            - "update orders from shopify"
            - "refresh orders"
            - "pull orders"
            - "backup PSL"
            - "restore PSL"
        """
        command_lower = command.lower().strip()
        
        # Sync orders
        if any(word in command_lower for word in ['sync order', 'update order', 'refresh order', 'pull order', 'get order']):
            return self._sync_orders()
        
        # Backup/Restore PSL - DEPRECATED (now using MANUAL_OVERRIDES)
        if 'backup psl' in command_lower or 'restore psl' in command_lower:
            return {
                'status': 'info',
                'message': 'ℹ️ **PSL Backup/Restore is no longer needed!**\n\n'
                          'Manual values (PSL, shipping_label_cost, notes) are now stored in the MANUAL_OVERRIDES sheet.\n'
                          'They are automatically preserved during sync and merged into view sheets.\n\n'
                          'Use Ops Agent commands instead:\n'
                          '• "set PSL to XYZ for order 1042"\n'
                          '• "set shipping label cost to 4.85 for order 1042"'
            }
        
        # Create Setup and Costs sheet
        if any(word in command_lower for word in ['create setup costs', 'create setup and costs', 'setup costs sheet']):
            return self._create_setup_costs_sheet()
        
        # General sync help
        return {
            'success': False,
            'message': 'Sync Agent: I can help with:\n'
                      '• "sync orders" - Sync all orders from Shopify to Google Sheets\n'
                      '• "update orders from shopify" - Same as sync orders\n'
                      '• "refresh orders" - Refresh orders from Shopify\n'
                      '• "backup PSL" - Save PSL values to backup\n'
                      '• "restore PSL" - Restore PSL values from backup\n'
                      '• "create setup costs sheet" - Create Setup and Costs tracking sheet'
        }
    
    def _sync_orders(self) -> Dict:
        """Sync ALL orders from Shopify to Google Sheets - pulls fresh data directly from Shopify"""
        from update_orders_sheet import update_orders_sheet
        
        logger.info("🔄 Starting FULL sync from Shopify to Google Sheets...")
        logger.info("📡 Fetching ALL orders directly from Shopify (no cache, no filters)...")
        logger.info("💡 Note: Manual values (PSL, shipping_label_cost, notes) are preserved in MANUAL_OVERRIDES")
        
        try:
            # Ensure MANUAL_OVERRIDES sheet exists
            self.sheets_manager.create_manual_overrides_sheet()
            
            # Get current order count before sync
            try:
                sheet = self.sheets_manager.create_sheet_if_not_exists("RAW_ORDERS")
                existing_data = sheet.get_all_values()
                orders_before = len(existing_data) - 1 if existing_data else 0  # -1 for header
                logger.info(f"📊 Current orders in RAW_ORDERS: {orders_before}")
            except:
                orders_before = 0
                logger.info("📊 Starting fresh - no existing orders found")
            
            # Sync orders - this will fetch ALL orders from Shopify and write to RAW_ORDERS
            logger.info("🔄 Syncing orders from Shopify to RAW_ORDERS...")
            logger.info("⏳ This may take a moment - fetching fresh data from Shopify...")
            
            # Call update_orders_sheet which now writes to RAW_ORDERS and creates view sheets
            update_orders_sheet()
            
            logger.info("✅ Sync completed! View sheets updated with manual overrides merged.")
            
            # Get new order count
            try:
                sheet = self.sheets_manager.create_sheet_if_not_exists("RAW_ORDERS")
                updated_data = sheet.get_all_values()
                orders_after = len(updated_data) - 1 if updated_data else 0
                logger.info(f"📊 Orders in RAW_ORDERS after sync: {orders_after}")
            except Exception as e:
                logger.error(f"Error reading sheet after sync: {e}")
                orders_after = 0
            
            orders_synced = orders_after
            new_orders = orders_after - orders_before
            
            # Build success message
            message = f'✅ **Sync Complete!**\n\n'
            message += f'📊 **Summary:**\n'
            message += f'  • Total orders synced: {orders_synced}\n'
            if new_orders > 0:
                message += f'  • New orders added: {new_orders}\n'
            elif orders_before > 0:
                message += f'  • Sheet refreshed with latest data\n'
            
            message += f'\n💾 **Manual Values:**\n'
            message += f'  • ✅ Preserved in MANUAL_OVERRIDES sheet\n'
            message += f'  • ✅ Merged into ORDERS view automatically\n'
            
            message += f'\n🔄 All orders synced from Shopify to Google Sheets'
            
            return {
                'status': 'success',
                'message': message,
                'data': {
                    'orders_synced': orders_synced,
                    'new_orders': new_orders,
                    'orders_before': orders_before,
                    'orders_after': orders_after
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing orders: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': f"Failed to sync orders: {str(e)}. Please ensure:\n"
                          f"1. Shopify API credentials are correct in Render environment variables.\n"
                          f"2. Google Sheets API credentials are correct and authorized.\n"
                          f"3. Your Render service is running and accessible.",
                'timestamp': datetime.now().isoformat()
            }
    
    
    def _create_setup_costs_sheet(self) -> Dict:
        """Create Setup and Costs sheet"""
        try:
            from create_setup_costs_sheet import create_setup_costs_sheet
            create_setup_costs_sheet(self.sheets_manager)
            return {
                'status': 'success',
                'message': '✅ **Setup and Costs Sheet Created!**\n\n'
                          '📊 A new "Setup and Costs" sheet has been created.\n'
                          '📍 Check your Google Sheet - you should see a new tab!\n\n'
                          '💡 This sheet tracks manufacturing and setup costs.',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating Setup and Costs sheet: {e}")
            return {
                'status': 'error',
                'message': f'Failed to create sheet: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

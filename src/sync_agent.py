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
        
        # Backup PSL
        if 'backup psl' in command_lower:
            return self._backup_psl()
        
        # Restore PSL
        if 'restore psl' in command_lower:
            return self._restore_psl()
        
        # General sync help
        return {
            'success': False,
            'message': 'Sync Agent: I can help with:\n'
                      '• "sync orders" - Sync all orders from Shopify to Google Sheets\n'
                      '• "update orders from shopify" - Same as sync orders\n'
                      '• "refresh orders" - Refresh orders from Shopify\n'
                      '• "backup PSL" - Save PSL values to backup\n'
                      '• "restore PSL" - Restore PSL values from backup'
        }
    
    def _sync_orders(self) -> Dict:
        """Sync ALL orders from Shopify to Google Sheets - pulls fresh data directly from Shopify"""
        from update_orders_sheet import update_orders_sheet
        
        logger.info("🔄 Starting FULL sync from Shopify to Google Sheets...")
        logger.info("📡 Fetching ALL orders directly from Shopify (no cache, no filters)...")
        
        try:
            # Get current order count before sync
            try:
                sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
                existing_data = sheet.get_all_values()
                orders_before = len(existing_data) - 1 if existing_data else 0  # -1 for header
                logger.info(f"📊 Current orders in sheet: {orders_before}")
            except:
                orders_before = 0
                logger.info("📊 Starting fresh - no existing orders found")
            
            # STEP 1: Backup PSL values BEFORE sync
            logger.info("💾 Step 1: Backing up PSL values before sync...")
            backup_result = self._backup_psl()
            if backup_result.get('status') == 'success':
                logger.info(f"✅ PSL backup successful: {backup_result.get('message', '')}")
            else:
                logger.warning(f"⚠️ PSL backup warning: {backup_result.get('message', '')}")
            
            # STEP 2: Sync orders - this will fetch ALL orders from Shopify
            logger.info("🔄 Step 2: Syncing orders from Shopify...")
            logger.info("⏳ This may take a moment - fetching fresh data from Shopify...")
            
            # Call update_orders_sheet which fetches directly from Shopify API
            update_orders_sheet()
            
            logger.info("✅ Sync completed! Restoring PSL values...")
            
            # STEP 3: Automatically restore PSL values AFTER sync
            logger.info("💾 Step 3: Automatically restoring PSL values after sync...")
            restore_result = self._restore_psl()
            if restore_result.get('status') == 'success':
                logger.info(f"✅ PSL restore successful: {restore_result.get('message', '')}")
            else:
                logger.warning(f"⚠️ PSL restore warning: {restore_result.get('message', '')}")
            
            # Get new order count
            try:
                sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
                updated_data = sheet.get_all_values()
                orders_after = len(updated_data) - 1 if updated_data else 0
                logger.info(f"📊 Orders in sheet after sync: {orders_after}")
            except Exception as e:
                logger.error(f"Error reading sheet after sync: {e}")
                orders_after = 0
            
            orders_synced = orders_after
            new_orders = orders_after - orders_before
            
            # Build success message
            message = f'✅ **Sync Complete!**\n\n'
            message += f'📊 **Summary:**\n'
            message += f'  • Total orders in sheet: {orders_synced}\n'
            if new_orders > 0:
                message += f'  • New orders added: {new_orders}\n'
            elif orders_before > 0:
                message += f'  • Sheet refreshed with latest data\n'
            
            # Add PSL restore status
            if restore_result.get('status') == 'success':
                message += f'\n💾 **PSL Values:**\n'
                message += f'  • ✅ Automatically restored after sync\n'
            elif backup_result.get('status') == 'success':
                message += f'\n💾 **PSL Values:**\n'
                message += f'  • ⚠️ Backup saved, but restore had issues\n'
                message += f'  • 💡 Try "restore PSL" manually\n'
            
            message += f'\n🔄 All orders synced from Shopify to Google Sheets'
            
            return {
                'status': 'success',
                'message': message,
                'data': {
                    'orders_synced': orders_synced,
                    'new_orders': new_orders,
                    'orders_before': orders_before,
                    'orders_after': orders_after,
                    'psl_backup_status': backup_result.get('status'),
                    'psl_restore_status': restore_result.get('status')
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
    
    def _backup_psl(self) -> Dict:
        """Backup PSL values"""
        try:
            from backup_restore_psl import backup_psl_values
            success = backup_psl_values()
            return {
                'status': 'success' if success else 'failed',
                'message': f'PSL values backed up successfully' if success else 'Backup failed',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error backing up PSL: {e}")
            return {
                'status': 'error',
                'message': f'Backup failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _restore_psl(self) -> Dict:
        """Restore PSL values"""
        try:
            from backup_restore_psl import restore_psl_values
            success = restore_psl_values()
            return {
                'status': 'success' if success else 'failed',
                'message': f'PSL values restored successfully' if success else 'Restore failed - no backup found',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error restoring PSL: {e}")
            return {
                'status': 'error',
                'message': f'Restore failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

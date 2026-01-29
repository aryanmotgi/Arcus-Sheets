"""
AI Agent for Google Sheets and Shopify Integration

This agent can understand natural language commands and interact with both
Shopify and Google Sheets to provide insights and update data.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml
from pathlib import Path

from shopify_client import ShopifyClient
from sheets_manager import SheetsManager
from data_processor import DataProcessor
from update_orders_sheet import update_orders_sheet
from sheet_manager_agent import SheetManagerAgent
from finance_agent import FinanceAgent
from chart_agent import ChartAgent
from sync_agent import SyncAgent
from costs_agent import CostsAgent
from ops_agent import OpsAgent
from format_agent import FormatAgent
from catalog_agent import CatalogAgent
from simple_orders_sync import SimpleOrdersSync

logger = logging.getLogger(__name__)


class SheetsAIAgent:
    """AI Agent that can interact with Shopify and Google Sheets"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize the AI agent with Shopify and Sheets connections"""
        import os
        
        # Load config from environment variables or file
        self.config = self._load_config(config_path)
        
        # Override with environment variables if they exist
        if os.getenv('SHOPIFY_STORE_URL'):
            self.config.setdefault('shopify', {})['store_url'] = os.getenv('SHOPIFY_STORE_URL')
        if os.getenv('SHOPIFY_CLIENT_ID'):
            self.config.setdefault('shopify', {})['client_id'] = os.getenv('SHOPIFY_CLIENT_ID')
        if os.getenv('SHOPIFY_CLIENT_SECRET'):
            self.config.setdefault('shopify', {})['client_secret'] = os.getenv('SHOPIFY_CLIENT_SECRET')
        if os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'):
            self.config.setdefault('google_sheets', {})['spreadsheet_id'] = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        
        # Initialize Shopify client
        shopify_config = self.config.get('shopify', {})
        self.shopify_client = ShopifyClient(
            store_url=shopify_config.get('store_url'),
            client_id=shopify_config.get('client_id'),
            client_secret=shopify_config.get('client_secret')
        )
        
        # Initialize Sheets manager
        sheets_config = self.config.get('google_sheets', {})
        spreadsheet_id = sheets_config.get('spreadsheet_id')
        
        # Get service account path or use environment variable
        service_account_path = sheets_config.get('service_account_path')
        google_credentials = os.getenv('GOOGLE_CREDENTIALS')
        
        self.sheets_manager = SheetsManager(
            spreadsheet_id=spreadsheet_id,
            service_account_path=service_account_path,
            google_credentials_json=google_credentials
        )
        
        # Initialize specialized agents
        self.sheet_manager_agent = SheetManagerAgent(self.sheets_manager)
        self.finance_agent = FinanceAgent(self.sheets_manager)
        self.chart_agent = ChartAgent(self.sheets_manager)
        self.sync_agent = SyncAgent(self.sheets_manager, self.shopify_client, self.config)
        self.costs_agent = CostsAgent(self.sheets_manager)
        self.ops_agent = OpsAgent(self.sheets_manager, self.shopify_client)
        self.format_agent = FormatAgent(self.sheets_manager)
        self.catalog_agent = CatalogAgent(self.sheets_manager, self.shopify_client)
        
        # Available commands the agent can execute
        self.available_commands = {
            'sync_orders': self._sync_orders,
            'get_revenue': self._get_revenue,
            'get_orders_summary': self._get_orders_summary,
            'update_orders': self._update_orders,
            'get_product_sales': self._get_product_sales,
            'get_customer_insights': self._get_customer_insights,
            'get_profit_breakdown': self._get_profit_breakdown,
            'backup_psl': self._backup_psl,
            'restore_psl': self._restore_psl,
        }
        
        logger.info("AI Agent initialized and ready")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file, return empty dict if file doesn't exist"""
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_path}, using environment variables instead")
            return {}
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config:
            return {}
        
        return config
    
    def process_command(self, command: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Process a natural language command and execute appropriate action
        
        Examples:
            - "sync orders from shopify"
            - "show me total revenue"
            - "update the orders sheet"
            - "what's my profit breakdown?"
            - "backup PSL values"
        """
        command_lower = command.lower().strip()
        logger.info(f"Processing command: {command} (dry_run={dry_run})")
        
        # Ping command (for testing API connection)
        if command_lower == 'ping':
            return {
                'success': True,
                'message': '✅ **Ping Successful!**\n\nAPI is responding correctly.\n\nBackend is connected and ready.',
                'data': {'status': 'ok', 'timestamp': datetime.now().isoformat()}
            }
        
        # Check for "apply" suffix to override dry_run
        if command_lower.endswith(' apply') or command_lower.endswith(' execute'):
            dry_run = False
            command = command.rsplit(' ', 1)[0]  # Remove "apply" suffix
            command_lower = command.lower().strip()
        
        # Simple command matching (can be enhanced with NLP/AI later)
        response = {
            'success': False,
            'message': '',
            'data': None,
            'command': command,
            'dry_run': dry_run
        }
        
        try:
            # Ops Agent - fulfillment & manual overrides (highest priority for write commands)
            if any(word in command_lower for word in ['shipping label cost', 'label cost', 'psl', 'unfulfilled', 
                                                       'missing label', 'negative profit', 'fulfillment']):
                result = self.ops_agent.process_command(command, dry_run)
                response['success'] = result.get('success', False)
                response['message'] = result.get('message', 'Ops command executed')
                response['data'] = result.get('data')
                if result.get('plan'):
                    response['plan'] = result.get('plan')
                return response
            
            # Tab info commands (early routing)
            if any(phrase in command_lower for phrase in ['what is each tab for', 'tab for', 'tab purpose', 'what tabs']):
                from tab_manifest import format_tab_purposes_for_display
                response['success'] = True
                response['message'] = '📋 **Tab Purposes:**\n' + format_tab_purposes_for_display()
                return response
            
            if any(phrase in command_lower for phrase in ['open workflow', 'daily workflow', 'workflow']):
                workflow = (
                    '📋 **Daily Arcus Workflow:**\n\n'
                    '1. **HOME** - Check KPIs and see what needs action\n'
                    '2. **ORDERS** - Review orders, set shipping label costs, add PSL/notes\n'
                    '3. **FINANCE** - Review profit margins and financial health\n'
                    '4. **METRICS** - See all calculated KPIs (auto-updated)\n'
                    '5. **CHARTS** - Visualize trends and performance\n'
                    '6. **PRODUCTS** - Manage catalog, costs, pricing\n'
                    '7. **COSTS** - Track setup and operational costs\n'
                    '8. **SETTINGS** - Configure Arcus theme and defaults\n\n'
                    '💡 **Commands:**\n'
                    '  • "sync orders" - Update from Shopify\n'
                    '  • "apply Arcus theme" - Format all tabs\n'
                    '  • "what is each tab for?" - See tab purposes\n'
                    '  • "cleanup tabs apply" - Remove duplicates'
                )
                response['success'] = True
                response['message'] = workflow
                return response
            
            # Format Agent - UI/branding (includes cleanup/reset)
            if any(word in command_lower for word in ['arcus theme', 'apply theme', 'format home', 'dashboard', 
                                                      'brand', 'branding', 'make it look like arcus', 'cleanup tabs', 'reset arcus ui']):
                result = self.format_agent.process_command(command, apply_changes)
                response['success'] = result.get('success', False)
                response['message'] = result.get('message', 'Format command executed')
                response['data'] = result.get('data')
                return response
            
            # === SIMPLE ORDERS SYNC (ORDERS tab only) ===
            # "init orders" / "init orders apply" - Initialize ORDERS tab
            if 'init order' in command_lower or 'init orders' in command_lower:
                simple_sync = SimpleOrdersSync(self.sheets_manager, self.shopify_client, self.config)
                result = simple_sync.init_orders_apply()
                response['success'] = result.get('success', False)
                response['message'] = result.get('message', 'ORDERS tab initialized')
                response['data'] = result.get('data')
                return response
            
            # "sync orders" - Sync Shopify orders to ORDERS tab
            if any(word in command_lower for word in ['sync order', 'sync orders', 'sync all orders']):
                simple_sync = SimpleOrdersSync(self.sheets_manager, self.shopify_client, self.config)
                result = simple_sync.sync_orders()
                response['success'] = result.get('success', False)
                response['message'] = result.get('message', 'Orders synced!')
                response['data'] = result.get('data')
                return response
            
            # Sync Agent - handles other sync commands (legacy)
            if any(word in command_lower for word in ['sync', 'update', 'refresh', 'pull', 'fetch', 'get orders']):
                if any(word in command_lower for word in ['sheet', 'shopify', 'data', 'everything', 'all']):
                    result = self.sync_agent.process_command(command)
                    response['success'] = result.get('status') == 'success' or result.get('success', False)
                    response['message'] = result.get('message', 'Orders synced!')
                    response['data'] = result
                    return response
            
            # Backup/Restore PSL - handled by Sync Agent
            if 'backup' in command_lower and 'psl' in command_lower:
                result = self.sync_agent.process_command(command)
                response['success'] = result.get('status') == 'success' or result.get('success', False)
                response['message'] = result.get('message', 'PSL backup completed')
                response['data'] = result
                return response
            
            if 'restore' in command_lower and 'psl' in command_lower:
                result = self.sync_agent.process_command(command)
                response['success'] = result.get('status') == 'success' or result.get('success', False)
                response['message'] = result.get('message', 'PSL restore completed')
                response['data'] = result
                return response
            
            # Revenue queries
            if any(word in command_lower for word in ['revenue', 'sales', 'total', 'money']):
                result = self._get_revenue()
                response['success'] = True
                response['message'] = "Revenue information retrieved"
                response['data'] = result
                return response
            
            # Orders summary
            if any(word in command_lower for word in ['order', 'summary', 'list']):
                result = self._get_orders_summary()
                response['success'] = True
                response['message'] = "Orders summary retrieved"
                response['data'] = result
                return response
            
            # Product sales
            if any(word in command_lower for word in ['product', 'item', 'sold']):
                result = self._get_product_sales()
                response['success'] = True
                response['message'] = "Product sales information retrieved"
                response['data'] = result
                return response
            
            # Costs Agent - handles cost-related operations
            if any(word in command_lower for word in ['cost', 'total cost', 'cost per shirt', 'profit per shirt', 'fix profit per shirt', '809']):
                result = self.costs_agent.process_command(command)
                response['success'] = result.get('success', False)
                response['message'] = result.get('message', 'Cost command executed')
                response['data'] = result
                return response
            
            # Profit queries (if not handled by costs agent)
            if any(word in command_lower for word in ['profit', 'margin']):
                # Check if it's profit per shirt (handled by costs agent)
                if 'profit per shirt' in command_lower or 'profitpershirt' in command_lower:
                    result = self.costs_agent.process_command(command)
                    response['success'] = result.get('success', False)
                    response['message'] = result.get('message', 'Profit per shirt command executed')
                    response['data'] = result
                    return response
                else:
                    result = self._get_profit_breakdown()
                    response['success'] = True
                    response['message'] = "Profit breakdown retrieved"
                    response['data'] = result
                    return response
            
            # Top products
            if any(word in command_lower for word in ['top product', 'best selling', 'best seller']):
                result = self._get_top_products()
                response['success'] = True
                response['message'] = "Top products retrieved"
                response['data'] = result
                return response
            
            # Top customers
            if any(word in command_lower for word in ['top customer', 'best customer', 'biggest customer']):
                result = self._get_top_customers()
                response['success'] = True
                response['message'] = "Top customers retrieved"
                response['data'] = result
                return response
            
            # Revenue trends
            if any(word in command_lower for word in ['trend', 'trends', 'over time', 'daily', 'weekly', 'monthly']):
                result = self._get_revenue_trends()
                response['success'] = True
                response['message'] = "Revenue trends retrieved"
                response['data'] = result
                return response
            
            # Low stock alert
            if any(word in command_lower for word in ['low stock', 'out of stock', 'inventory']):
                result = self._get_low_stock_alerts()
                response['success'] = True
                response['message'] = "Low stock alerts retrieved"
                response['data'] = result
                return response
            
            # Date range queries
            if any(word in command_lower for word in ['last week', 'this week', 'last month', 'this month', 'yesterday', 'today']):
                result = self._get_orders_by_date_range(command_lower)
                response['success'] = True
                response['message'] = "Orders by date range retrieved"
                response['data'] = result
                return response
            
            # Catalog Agent - products, costs, pricing
            if any(word in command_lower for word in ['sku', 'product', 'inventory', 'catalog', 'plan new product', 
                                                       'set cost', 'suggest price', 'low stock']):
                result = self.catalog_agent.process_command(command, dry_run)
                response['success'] = result.get('success', False)
                response['message'] = result.get('message', 'Catalog command executed')
                response['data'] = result.get('data')
                if result.get('plan'):
                    response['plan'] = result.get('plan')
                return response
            
            # Chart Agent - handles chart creation
            if any(word in command_lower for word in ['chart', 'graph', 'visualize', 'plot', 'create chart', 'make chart', 'generate chart']):
                result = self.chart_agent.process_command(command)
                response['success'] = result.get('success', False)
                response['message'] = result.get('message', 'Chart command executed')
                response['data'] = result.get('data')
                return response
            
            # Sheet management commands (format, update, modify, organize)
            if any(word in command_lower for word in ['format', 'style', 'color', 'border', 'align', 'wider', 
                                                      'update sheet', 'modify sheet', 'change sheet', 'organize',
                                                      'arrange', 'reorder', 'move', 'swap', 'sort']):
                result = self.sheet_manager_agent.process_sheet_command(command)
                response['success'] = result.get('success', False)
                response['message'] = result.get('message', 'Sheet command executed')
                response['data'] = result
                return response
            
            # Try to understand the intent better
            # If command contains numbers or specific requests, be more helpful
            if any(char.isdigit() for char in command):
                response['message'] = f"I see you're asking about something specific. Try:\n" \
                                    f"- 'sync orders' to update all orders\n" \
                                    f"- 'show revenue' to see sales totals\n" \
                                    f"- 'top 5 products' to see best sellers\n" \
                                    f"- Or ask me to format/modify the sheet\n\n" \
                                    f"Your command: '{command}'"
            else:
                # Default: more helpful error message
                response['message'] = f"🤖 I can help you with:\n\n" \
                                    f"📦 **Ops Agent** - Fulfillment & Manual Data:\n" \
                                    f"  • 'set shipping label cost to 4.85 for order 1042' - Set label cost\n" \
                                    f"  • 'set PSL to XYZ for order 1042' - Set PSL value\n" \
                                    f"  • 'show unfulfilled orders' - List unfulfilled\n" \
                                    f"  • 'show missing shipping label cost' - Find missing costs\n\n" \
                                    f"🔄 **Sync Agent** - Orders & Data:\n" \
                                    f"  • 'sync orders' - Update all orders from Shopify\n" \
                                    f"  • 'create setup costs sheet' - Create cost tracking sheet\n\n" \
                                    f"💵 **Costs Agent** - Cost Operations:\n" \
                                    f"  • 'update total costs to 1000' - Update TOTAL COSTS\n" \
                                    f"  • 'what's the total cost?' - Get total costs\n" \
                                    f"  • 'fix profit per shirt formula' - Fix Profit Per Shirt\n\n" \
                                    f"💰 **Finance Agent** - Financial Calculations:\n" \
                                    f"  • 'fix net profit formula' - Fix NET PROFIT\n" \
                                    f"  • 'what's the total revenue?' - Get revenue\n" \
                                    f"  • 'calculate profit margin' - Get profit margin\n\n" \
                                    f"🎨 **Format Agent** - UI & Branding:\n" \
                                    f"  • 'apply Arcus theme' - Apply Arcus branding\n" \
                                    f"  • 'format HOME dashboard' - Create/format dashboard\n\n" \
                                    f"📝 **Sheets Agent** - Format & Modify:\n" \
                                    f"  • 'format orders sheet' - Style the sheet\n" \
                                    f"  • 'swap shipping cost with PSL' - Move columns\n" \
                                    f"  • 'add borders' - Format cells\n\n" \
                                    f"📊 **Data & Analytics:**\n" \
                                    f"  • 'show revenue' - Get sales totals\n" \
                                    f"  • 'orders summary' - Overview of all orders\n" \
                                    f"  • 'profit breakdown' - Profit analysis\n" \
                                    f"  • 'top products' - Best sellers\n\n" \
                                    f"💡 **Tip:** Add ' apply' to the end of write commands to execute them\n\n" \
                                    f"❓ I didn't understand: '{command}'\n" \
                                    f"Try one of the commands above!"
            
        except Exception as e:
            logger.error(f"Error processing command: {e}", exc_info=True)
            response['message'] = f"Error: {str(e)}"
        
        return response
    
    def _sync_orders(self) -> Dict:
        """Sync ALL orders from Shopify to Google Sheets - pulls fresh data directly from Shopify"""
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
                    'orders_before': orders_before,
                    'orders_after': orders_after,
                    'new_orders': new_orders
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error syncing orders: {e}", exc_info=True)
            error_msg = str(e)
            
            # Better error messages
            if "Shopify" in error_msg or "credentials" in error_msg.lower() or "token" in error_msg.lower():
                error_msg = f"❌ **Shopify Connection Error**\n\n{error_msg}\n\n💡 **Fix:**\n  • Check SHOPIFY_STORE_URL\n  • Check SHOPIFY_CLIENT_ID\n  • Check SHOPIFY_CLIENT_SECRET\n  • Verify credentials in Render environment variables"
            elif "Google" in error_msg or "service_account" in error_msg.lower() or "credentials" in error_msg.lower():
                error_msg = f"❌ **Google Sheets Error**\n\n{error_msg}\n\n💡 **Fix:**\n  • Check GOOGLE_CREDENTIALS in Render\n  • Verify service account has access\n  • Check GOOGLE_SHEETS_SPREADSHEET_ID"
            else:
                error_msg = f"❌ **Sync Error**\n\n{error_msg}\n\n💡 Check Render logs for more details"
            
            return {
                'status': 'error',
                'message': error_msg,
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_revenue(self) -> Dict:
        """Get revenue information from Google Sheets"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Read summary section (column O)
            summary_range = "O2:P9"  # Adjust based on your summary location
            summary_data = sheet.get_values(summary_range)
            
            revenue_info = {}
            if summary_data:
                for row in summary_data:
                    if len(row) >= 2:
                        metric = row[0].strip() if row[0] else ""
                        value = row[1] if len(row) > 1 else ""
                        
                        if 'Revenue' in metric:
                            revenue_info['total_revenue'] = value
                        elif 'Profit' in metric:
                            revenue_info['net_profit'] = value
                        elif 'Units Sold' in metric:
                            revenue_info['units_sold'] = value
                        elif 'Shopify Payout' in metric:
                            revenue_info['shopify_payout'] = value
            
            return {
                'revenue': revenue_info,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting revenue: {e}")
            return {'error': str(e)}
    
    def _get_orders_summary(self) -> Dict:
        """Get summary of orders from Shopify"""
        try:
            orders = self.shopify_client.get_orders(status='any', limit=50)
            
            total_orders = len(orders)
            total_value = sum(float(order.get('total_price', 0)) for order in orders)
            
            # Group by status
            status_counts = {}
            for order in orders:
                status = order.get('financial_status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'total_orders': total_orders,
                'total_value': round(total_value, 2),
                'status_breakdown': status_counts,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting orders summary: {e}")
            return {'error': str(e)}
    
    def _get_product_sales(self) -> Dict:
        """Get product sales breakdown"""
        try:
            orders = self.shopify_client.get_orders(status='any', limit=100)
            processor = DataProcessor(self.config)
            orders_df = processor.process_orders(orders)
            
            if orders_df.empty:
                return {'message': 'No orders found'}
            
            # Product sales breakdown
            product_sales = orders_df.groupby('Product Name').agg({
                'Quantity': 'sum',
                'Unit Price': 'sum'
            }).to_dict('index')
            
            return {
                'product_sales': product_sales,
                'total_products': len(product_sales),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting product sales: {e}")
            return {'error': str(e)}
    
    def _get_profit_breakdown(self) -> Dict:
        """Get profit breakdown from Google Sheets"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("Orders")
            
            # Read summary section
            summary_range = "O2:P9"
            summary_data = sheet.get_values(summary_range)
            
            profit_info = {}
            if summary_data:
                for row in summary_data:
                    if len(row) >= 2:
                        metric = row[0].strip() if row[0] else ""
                        value = row[1] if len(row) > 1 else ""
                        
                        if 'Revenue' in metric:
                            profit_info['total_revenue'] = value
                        elif 'Product Costs' in metric:
                            profit_info['total_product_costs'] = value
                        elif 'TOTAL COSTS' in metric:
                            profit_info['total_costs'] = value
                        elif 'NET PROFIT' in metric:
                            profit_info['net_profit'] = value
                        elif 'Profit Per Shirt' in metric:
                            profit_info['profit_per_shirt'] = value
            
            return {
                'profit_breakdown': profit_info,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting profit breakdown: {e}")
            return {'error': str(e)}
    
    def _update_orders(self) -> Dict:
        """Update orders in Google Sheets"""
        return self._sync_orders()
    
    def _get_customer_insights(self) -> Dict:
        """Get customer insights from orders"""
        try:
            orders = self.shopify_client.get_orders(status='any', limit=100)
            
            # Get unique customers
            customers = {}
            for order in orders:
                customer = order.get('customer', {})
                email = customer.get('email', 'unknown')
                if email not in customers:
                    customers[email] = {
                        'name': customer.get('first_name', '') + ' ' + customer.get('last_name', ''),
                        'orders': 0,
                        'total_spent': 0
                    }
                customers[email]['orders'] += 1
                customers[email]['total_spent'] += float(order.get('total_price', 0))
            
            return {
                'total_customers': len(customers),
                'top_customers': sorted(
                    customers.items(),
                    key=lambda x: x[1]['total_spent'],
                    reverse=True
                )[:10],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting customer insights: {e}")
            return {'error': str(e)}
    
    def _backup_psl(self) -> Dict:
        """Backup PSL values"""
        try:
            from backup_restore_psl import backup_psl_values
            success = backup_psl_values()
            return {
                'status': 'success' if success else 'failed',
                'message': 'PSL values backed up' if success else 'Backup failed',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error backing up PSL: {e}")
            return {'error': str(e)}
    
    def _restore_psl(self) -> Dict:
        """Restore PSL values"""
        try:
            from backup_restore_psl import restore_psl_values
            success = restore_psl_values()
            return {
                'status': 'success' if success else 'failed',
                'message': 'PSL values restored' if success else 'Restore failed',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error restoring PSL: {e}")
            return {'error': str(e)}
    
    def _get_top_products(self) -> Dict:
        """Get top selling products"""
        try:
            orders = self.shopify_client.get_orders(status='any', limit=100)
            processor = DataProcessor(self.config)
            orders_df = processor.process_orders(orders)
            
            if orders_df.empty:
                return {'message': 'No orders found'}
            
            # Group by product and calculate totals
            product_stats = orders_df.groupby('Product Name').agg({
                'Quantity': 'sum',
                'Unit Price': 'sum'
            }).sort_values('Quantity', ascending=False).head(10)
            
            top_products = []
            for product, row in product_stats.iterrows():
                top_products.append({
                    'product': product,
                    'quantity_sold': int(row['Quantity']),
                    'revenue': round(float(row['Unit Price']), 2)
                })
            
            return {
                'top_products': top_products,
                'total_products': len(top_products),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return {'error': str(e)}
    
    def _get_top_customers(self) -> Dict:
        """Get top customers by spending"""
        try:
            orders = self.shopify_client.get_orders(status='any', limit=100)
            
            customers = {}
            for order in orders:
                customer = order.get('customer', {})
                email = customer.get('email', 'unknown')
                name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or 'Unknown'
                
                if email not in customers:
                    customers[email] = {
                        'name': name,
                        'email': email,
                        'orders': 0,
                        'total_spent': 0.0
                    }
                
                customers[email]['orders'] += 1
                customers[email]['total_spent'] += float(order.get('total_price', 0))
            
            # Sort by total spent
            top_customers = sorted(
                customers.values(),
                key=lambda x: x['total_spent'],
                reverse=True
            )[:10]
            
            return {
                'top_customers': top_customers,
                'total_customers': len(top_customers),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting top customers: {e}")
            return {'error': str(e)}
    
    def _get_revenue_trends(self) -> Dict:
        """Get revenue trends over time"""
        try:
            orders = self.shopify_client.get_orders(status='any', limit=100)
            
            # Group by date
            daily_revenue = {}
            for order in orders:
                created_at = order.get('created_at', '')
                if created_at:
                    date = created_at.split('T')[0]  # Get just the date part
                    revenue = float(order.get('total_price', 0))
                    daily_revenue[date] = daily_revenue.get(date, 0) + revenue
            
            # Sort by date
            sorted_dates = sorted(daily_revenue.items())
            
            trends = {
                'daily': [{'date': date, 'revenue': round(revenue, 2)} for date, revenue in sorted_dates[-7:]],  # Last 7 days
                'total_days': len(sorted_dates),
                'average_daily': round(sum(daily_revenue.values()) / len(daily_revenue) if daily_revenue else 0, 2),
                'total_revenue': round(sum(daily_revenue.values()), 2)
            }
            
            return {
                'trends': trends,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting revenue trends: {e}")
            return {'error': str(e)}
    
    def _get_low_stock_alerts(self) -> Dict:
        """Get low stock alerts"""
        try:
            # Get products from Shopify
            products = self.shopify_client.get_products(limit=100)
            
            low_stock_items = []
            for product in products:
                variants = product.get('variants', [])
                for variant in variants:
                    inventory = variant.get('inventory_quantity', 0)
                    if inventory < 10:  # Low stock threshold
                        low_stock_items.append({
                            'product': product.get('title', 'Unknown'),
                            'variant': variant.get('title', 'Default'),
                            'current_stock': inventory,
                            'status': 'Critical' if inventory < 5 else 'Low'
                        })
            
            return {
                'low_stock_items': low_stock_items,
                'total_low_stock': len(low_stock_items),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting low stock alerts: {e}")
            return {'error': str(e)}
    
    def _get_orders_by_date_range(self, command: str) -> Dict:
        """Get orders filtered by date range"""
        try:
            from datetime import datetime, timedelta
            
            # Determine date range from command
            now = datetime.now()
            if 'last week' in command:
                start_date = now - timedelta(days=7)
            elif 'this week' in command:
                start_date = now - timedelta(days=now.weekday())
            elif 'last month' in command:
                start_date = now - timedelta(days=30)
            elif 'this month' in command:
                start_date = now.replace(day=1)
            elif 'yesterday' in command:
                start_date = now - timedelta(days=1)
                now = start_date + timedelta(days=1)
            elif 'today' in command:
                start_date = now.replace(hour=0, minute=0, second=0)
            else:
                start_date = now - timedelta(days=7)  # Default to last week
            
            # Get orders
            orders = self.shopify_client.get_orders(status='any', limit=100)
            
            # Filter by date
            filtered_orders = []
            total_value = 0.0
            
            for order in orders:
                created_at = order.get('created_at', '')
                if created_at:
                    order_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if start_date <= order_date.replace(tzinfo=None) <= now:
                        filtered_orders.append(order)
                        total_value += float(order.get('total_price', 0))
            
            return {
                'orders': len(filtered_orders),
                'total_value': round(total_value, 2),
                'date_range': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': now.strftime('%Y-%m-%d')
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting orders by date range: {e}")
            return {'error': str(e)}


def main():
    """CLI interface for the AI agent"""
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python src/ai_agent.py '<command>'")
        print("\nExample commands:")
        print("  - 'sync orders'")
        print("  - 'show revenue'")
        print("  - 'orders summary'")
        print("  - 'product sales'")
        print("  - 'profit breakdown'")
        print("  - 'backup PSL'")
        sys.exit(1)
    
    command = ' '.join(sys.argv[1:])
    
    try:
        agent = SheetsAIAgent()
        response = agent.process_command(command)
        
        print("\n" + "="*70)
        print(f"Command: {response['command']}")
        print("="*70)
        print(f"Status: {'SUCCESS' if response['success'] else 'FAILED'}")
        print(f"Message: {response['message']}")
        
        if response.get('data'):
            print("\nData:")
            print(json.dumps(response['data'], indent=2))
        
        print("="*70 + "\n")
        
    except Exception as e:
        import traceback
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\nError: {e}\n")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

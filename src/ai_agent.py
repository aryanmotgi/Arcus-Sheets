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

logger = logging.getLogger(__name__)


class SheetsAIAgent:
    """AI Agent that can interact with Shopify and Google Sheets"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize the AI agent with Shopify and Sheets connections"""
        self.config = self._load_config(config_path)
        
        # Initialize Shopify client
        shopify_config = self.config.get('shopify', {})
        self.shopify_client = ShopifyClient(
            store_url=shopify_config.get('store_url'),
            client_id=shopify_config.get('client_id'),
            client_secret=shopify_config.get('client_secret')
        )
        
        # Initialize Sheets manager
        sheets_config = self.config.get('google_sheets', {})
        self.sheets_manager = SheetsManager(
            spreadsheet_id=sheets_config.get('spreadsheet_id'),
            service_account_path=sheets_config.get('service_account_path')
        )
        
        # Initialize Sheet Manager Agent for sheet modifications
        self.sheet_manager_agent = SheetManagerAgent(self.sheets_manager)
        
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
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config:
            raise ValueError("Config file is empty")
        
        return config
    
    def process_command(self, command: str) -> Dict[str, Any]:
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
        logger.info(f"Processing command: {command}")
        
        # Simple command matching (can be enhanced with NLP/AI later)
        response = {
            'success': False,
            'message': '',
            'data': None,
            'command': command
        }
        
        try:
            # Sync/Sync orders
            if any(word in command_lower for word in ['sync', 'update', 'refresh']):
                if 'order' in command_lower or 'sheet' in command_lower:
                    result = self._sync_orders()
                    response['success'] = True
                    response['message'] = "Orders synced successfully!"
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
            
            # Profit queries
            if any(word in command_lower for word in ['profit', 'margin', 'cost']):
                result = self._get_profit_breakdown()
                response['success'] = True
                response['message'] = "Profit breakdown retrieved"
                response['data'] = result
                return response
            
            # PSL backup/restore
            if 'backup' in command_lower and 'psl' in command_lower:
                result = self._backup_psl()
                response['success'] = True
                response['message'] = "PSL values backed up successfully"
                response['data'] = result
                return response
            
            if 'restore' in command_lower and 'psl' in command_lower:
                result = self._restore_psl()
                response['success'] = True
                response['message'] = "PSL values restored successfully"
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
            
            # Sheet management commands (format, update, modify)
            if any(word in command_lower for word in ['format', 'style', 'color', 'border', 'align', 'wider', 'update sheet', 'modify sheet', 'change sheet']):
                result = self.sheet_manager_agent.process_sheet_command(command)
                response['success'] = result.get('success', False)
                response['message'] = result.get('message', 'Sheet command executed')
                response['data'] = result
                return response
            
            # Default: help message
            response['message'] = f"I can help you with:\n" \
                                f"- Syncing orders: 'sync orders' or 'update orders'\n" \
                                f"- Revenue info: 'show revenue' or 'total sales'\n" \
                                f"- Orders summary: 'list orders' or 'orders summary'\n" \
                                f"- Product sales: 'product sales' or 'items sold'\n" \
                                f"- Profit breakdown: 'show profit' or 'profit breakdown'\n" \
                                f"- Top products: 'top products' or 'best selling'\n" \
                                f"- Top customers: 'top customers' or 'best customers'\n" \
                                f"- Revenue trends: 'revenue trends' or 'sales trends'\n" \
                                f"- Low stock: 'low stock alert' or 'inventory'\n" \
                                f"- Date range: 'orders from last week' or 'this month'\n" \
                                f"- Format sheet: 'format orders sheet' or 'style sheet'\n" \
                                f"- Change colors: 'make column A blue' or 'color header red'\n" \
                                f"- Modify columns: 'make column A wider' or 'widen product name'\n" \
                                f"- Borders: 'add borders' or 'remove borders'\n" \
                                f"- Alignment: 'center all text' or 'align left'\n" \
                                f"- PSL backup: 'backup PSL'\n" \
                                f"- PSL restore: 'restore PSL'\n\n" \
                                f"Your command: '{command}'"
            
        except Exception as e:
            logger.error(f"Error processing command: {e}", exc_info=True)
            response['message'] = f"Error: {str(e)}"
        
        return response
    
    def _sync_orders(self) -> Dict:
        """Sync orders from Shopify to Google Sheets"""
        logger.info("Syncing orders from Shopify to Google Sheets...")
        try:
            update_orders_sheet()
            return {
                'status': 'success',
                'message': 'Orders synced successfully',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error syncing orders: {e}")
            return {
                'status': 'error',
                'message': str(e),
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

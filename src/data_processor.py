"""
Data Processing Module for transforming and aggregating Shopify data
"""
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes and transforms raw Shopify data into structured DataFrames"""
    
    def __init__(self):
        """Initialize data processor"""
        self.logger = logging.getLogger(__name__)
    
    def process_orders(self, orders: List[Dict]) -> pd.DataFrame:
        """
        Transform orders data into DataFrame with one row per line item
        
        Args:
            orders: List of order dictionaries from Shopify API
            
        Returns:
            DataFrame with columns matching Orders Detail sheet structure
        """
        self.logger.info(f"Processing {len(orders)} orders...")
        
        rows = []
        
        for order in orders:
            order_id = order.get('id', '')
            order_number = order.get('order_number', '')
            created_at = order.get('created_at', '')
            updated_at = order.get('updated_at', '')
            fulfilled_at = order.get('fulfilled_at', '')
            
            # Parse dates
            try:
                if created_at:
                    created_dt = pd.to_datetime(created_at)
                    created_date = created_dt.strftime('%Y-%m-%d')
                    created_time = created_dt.strftime('%H:%M:%S')
                else:
                    created_date = ''
                    created_time = ''
            except:
                created_date = ''
                created_time = ''
            
            # Customer information
            customer = order.get('customer', {})
            customer_id = customer.get('id', '')
            customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
            if not customer_name:
                customer_name = customer.get('email', '') or order.get('email', '')
            customer_email = customer.get('email', '') or order.get('email', '')
            
            # Addresses
            billing_address = order.get('billing_address', {})
            shipping_address = order.get('shipping_address', {})
            
            billing_addr_str = self._format_address(billing_address)
            shipping_addr_str = self._format_address(shipping_address)
            
            # Order-level fields
            order_status = order.get('financial_status', '')
            fulfillment_status = order.get('fulfillment_status', '')
            payment_method = order.get('gateway', '')
            currency = order.get('currency', 'USD')
            tags = ', '.join(order.get('tags', [])) if isinstance(order.get('tags'), list) else order.get('tags', '')
            notes = order.get('note', '')
            
            # Financial fields
            subtotal_price = self._parse_currency(order.get('subtotal_price', '0'))
            total_tax = self._parse_currency(order.get('total_tax', '0'))
            
            # Get shipping cost from multiple sources
            total_shipping = 0.0
            # Try total_shipping_price_set first
            shipping_price_set = order.get('total_shipping_price_set', {})
            if shipping_price_set and 'shop_money' in shipping_price_set:
                total_shipping = self._parse_currency(shipping_price_set['shop_money'].get('amount', '0'))
            
            # If that's 0, try shipping_lines (sometimes shipping is stored here)
            if total_shipping == 0:
                shipping_lines = order.get('shipping_lines', [])
                if shipping_lines:
                    for shipping_line in shipping_lines:
                        # Try price field
                        if 'price' in shipping_line:
                            total_shipping += self._parse_currency(str(shipping_line['price']))
                        # Try price_set
                        elif 'price_set' in shipping_line:
                            price_set = shipping_line['price_set']
                            if 'shop_money' in price_set:
                                total_shipping += self._parse_currency(price_set['shop_money'].get('amount', '0'))
            
            total_discounts = self._parse_currency(order.get('total_discounts', '0'))
            total_price = self._parse_currency(order.get('total_price', '0'))
            
            # Shipping method
            shipping_lines = order.get('shipping_lines', [])
            shipping_method = shipping_lines[0].get('title', '') if shipping_lines else ''
            tracking_number = ''
            for fulfillment in order.get('fulfillments', []):
                if fulfillment.get('tracking_number'):
                    tracking_number = fulfillment.get('tracking_number', '')
                    break
            
            # Process each line item
            line_items = order.get('line_items', [])
            if not line_items:
                # Create a row even if no line items
                rows.append({
                    'Order ID': order_id,
                    'Order Number': order_number,
                    'Date': created_date,
                    'Time': created_time,
                    'Customer ID': customer_id,
                    'Customer Name': customer_name,
                    'Customer Email': customer_email,
                    'Billing Address': billing_addr_str,
                    'Shipping Address': shipping_addr_str,
                    'Order Status': order_status,
                    'Financial Status': order_status,
                    'Fulfillment Status': fulfillment_status,
                    'Payment Method': payment_method,
                    'Gateway': payment_method,
                    'Line Item ID': '',
                    'Product ID': '',
                    'Variant ID': '',
                    'SKU': '',
                    'Product Name': '',
                    'Variant Title': '',
                    'Quantity': 0,
                    'Unit Price': 0.0,
                    'Line Total': 0.0,
                    'Discount Amount': 0.0,
                    'Tax Amount': 0.0,
                    'Shipping Cost': total_shipping,
                    'Order Subtotal': subtotal_price,
                    'Order Total': total_price,
                    'Currency': currency,
                    'Channel': 'Online' if order.get('source_name') == 'web' else 'Point of Sale',
                    'Source': order.get('source_name', ''),
                    'Tags': tags,
                    'Notes': notes,
                    'Shipping Method': shipping_method,
                    'Tracking Number': tracking_number,
                    'Fulfillment Date': fulfilled_at[:10] if fulfilled_at else ''
                })
            else:
                for item in line_items:
                    product_id = item.get('product_id', '')
                    variant_id = item.get('variant_id', '')
                    sku = item.get('sku', '')
                    product_name = item.get('name', '') or item.get('title', '')
                    variant_title = item.get('variant_title', '')
                    quantity = item.get('quantity', 0)
                    unit_price = self._parse_currency(item.get('price', '0'))
                    line_total = unit_price * quantity
                    
                    # Discounts and taxes for this line item
                    discount_amount = self._parse_currency(item.get('total_discount', '0'))
                    tax_amount = self._parse_currency(item.get('tax_lines', [{}])[0].get('price', '0')) if item.get('tax_lines') else 0.0
                    
                    rows.append({
                        'Order ID': order_id,
                        'Order Number': order_number,
                        'Date': created_date,
                        'Time': created_time,
                        'Customer ID': customer_id,
                        'Customer Name': customer_name,
                        'Customer Email': customer_email,
                        'Billing Address': billing_addr_str,
                        'Shipping Address': shipping_addr_str,
                        'Order Status': order_status,
                        'Financial Status': order_status,
                        'Fulfillment Status': fulfillment_status,
                        'Payment Method': payment_method,
                        'Gateway': payment_method,
                        'Line Item ID': item.get('id', ''),
                        'Product ID': product_id,
                        'Variant ID': variant_id,
                        'SKU': sku,
                        'Product Name': product_name,
                        'Variant Title': variant_title,
                        'Quantity': quantity,
                        'Unit Price': unit_price,
                        'Line Total': line_total,
                        'Discount Amount': discount_amount,
                        'Tax Amount': tax_amount,
                        'Shipping Cost': total_shipping,
                        'Order Subtotal': subtotal_price,
                        'Order Total': total_price,
                        'Currency': currency,
                        'Channel': 'Online' if order.get('source_name') == 'web' else 'Point of Sale',
                        'Source': order.get('source_name', ''),
                        'Tags': tags,
                        'Notes': notes,
                        'Shipping Method': shipping_method,
                        'Tracking Number': tracking_number,
                        'Fulfillment Date': fulfilled_at[:10] if fulfilled_at else ''
                    })
        
        df = pd.DataFrame(rows)
        self.logger.info(f"Processed {len(df)} order line items")
        return df
    
    def calculate_financial_metrics(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate financial metrics from processed orders
        
        Args:
            orders_df: Processed orders DataFrame
            
        Returns:
            DataFrame with financial metrics (one row per order/transaction)
        """
        self.logger.info("Calculating financial metrics...")
        
        # Group by Order ID to get per-order metrics
        financial_rows = []
        
        for order_id, group in orders_df.groupby('Order ID'):
            order_row = group.iloc[0]  # Get first row for order-level data
            
            # Calculate order-level metrics
            gross_sales = group['Line Total'].sum()
            discounts = group['Discount Amount'].sum()
            taxes = group['Tax Amount'].sum() if 'Tax Amount' in group.columns else 0.0
            shipping_cost = group['Shipping Cost'].iloc[0] if len(group) > 0 else 0.0
            
            # For now, assume no COGS data (can be enhanced later)
            cogs = 0.0
            
            net_sales = gross_sales - discounts
            gross_profit = net_sales - cogs
            profit_margin_pct = (gross_profit / net_sales * 100) if net_sales > 0 else 0.0
            
            financial_rows.append({
                'Date': order_row.get('Date', ''),
                'Order ID': order_id,
                'Channel': order_row.get('Channel', ''),
                'Gross Sales': gross_sales,
                'Discounts': discounts,
                'Returns': 0.0,  # Would need refund data
                'Refunds': 0.0,  # Would need refund data
                'Taxes': taxes,
                'Shipping Costs': shipping_cost,
                'COGS': cogs,
                'Net Sales': net_sales,
                'Gross Profit': gross_profit,
                'Profit Margin %': profit_margin_pct,
                'Payment Method': order_row.get('Payment Method', ''),
                'Transaction Fees': 0.0,  # Would need payment gateway data
                'Order Status': order_row.get('Order Status', ''),
                'Fulfillment Status': order_row.get('Fulfillment Status', '')
            })
        
        df = pd.DataFrame(financial_rows)
        self.logger.info(f"Calculated financial metrics for {len(df)} orders")
        return df
    
    def process_products(self, products: List[Dict], inventory_levels: Dict = None) -> pd.DataFrame:
        """
        Transform products data into DataFrame with one row per variant
        
        Args:
            products: List of product dictionaries from Shopify API
            inventory_levels: Dictionary mapping variant_id to inventory data
            
        Returns:
            DataFrame with columns matching Products & Inventory sheet structure
        """
        self.logger.info(f"Processing {len(products)} products...")
        
        rows = []
        
        for product in products:
            product_id = product.get('id', '')
            product_name = product.get('title', '')
            product_type = product.get('product_type', '')
            vendor = product.get('vendor', '')
            tags = ', '.join(product.get('tags', [])) if isinstance(product.get('tags'), list) else product.get('tags', '')
            status = product.get('status', '')
            created_at = product.get('created_at', '')
            updated_at = product.get('updated_at', '')
            
            variants = product.get('variants', [])
            
            if not variants:
                # Create row for product without variants
                rows.append({
                    'Product ID': product_id,
                    'Variant ID': '',
                    'SKU': '',
                    'Product Name': product_name,
                    'Variant Title': '',
                    'Product Type': product_type,
                    'Vendor': vendor,
                    'Category/Tags': tags,
                    'Price': 0.0,
                    'Cost (COGS)': 0.0,
                    'Current Stock (all locations)': 0,
                    'Total Stock': 0,
                    'Location Details': '',
                    'Last Restock Date': '',
                    'Units Sold (30 days)': 0,
                    'Units Sold (60 days)': 0,
                    'Units Sold (90 days)': 0,
                    'Revenue (30 days)': 0.0,
                    'Revenue (60 days)': 0.0,
                    'Revenue (90 days)': 0.0,
                    'Profit (30 days)': 0.0,
                    'Profit (60 days)': 0.0,
                    'Profit (90 days)': 0.0,
                    'Margin %': 0.0,
                    'Turnover Rate': 0.0,
                    'Days of Inventory Remaining': 0.0,
                    'Low Stock Alert': 'N',
                    'Status': status,
                    'Created Date': created_at[:10] if created_at else '',
                    'Updated Date': updated_at[:10] if updated_at else ''
                })
            else:
                for variant in variants:
                    variant_id = variant.get('id', '')
                    sku = variant.get('sku', '')
                    variant_title = variant.get('title', '')
                    price = self._parse_currency(variant.get('price', '0'))
                    cost = 0.0  # COGS not available from Shopify API directly
                    
                    # Get inventory levels
                    inventory_item_id = variant.get('inventory_item_id', '')
                    total_stock = variant.get('inventory_quantity', 0)
                    
                    # If inventory_levels dict provided, use it
                    if inventory_levels and inventory_item_id in inventory_levels:
                        inv_data = inventory_levels[inventory_item_id]
                        total_stock = inv_data.get('available', total_stock)
                    
                    rows.append({
                        'Product ID': product_id,
                        'Variant ID': variant_id,
                        'SKU': sku,
                        'Product Name': product_name,
                        'Variant Title': variant_title,
                        'Product Type': product_type,
                        'Vendor': vendor,
                        'Category/Tags': tags,
                        'Price': price,
                        'Cost (COGS)': cost,
                        'Current Stock (all locations)': total_stock,
                        'Total Stock': total_stock,
                        'Location Details': '',
                        'Last Restock Date': '',
                        'Units Sold (30 days)': 0,
                        'Units Sold (60 days)': 0,
                        'Units Sold (90 days)': 0,
                        'Revenue (30 days)': 0.0,
                        'Revenue (60 days)': 0.0,
                        'Revenue (90 days)': 0.0,
                        'Profit (30 days)': 0.0,
                        'Profit (60 days)': 0.0,
                        'Profit (90 days)': 0.0,
                        'Margin %': 0.0,
                        'Turnover Rate': 0.0,
                        'Days of Inventory Remaining': 0.0,
                        'Low Stock Alert': 'Y' if total_stock < 10 else 'N',
                        'Status': status,
                        'Created Date': created_at[:10] if created_at else '',
                        'Updated Date': updated_at[:10] if updated_at else ''
                    })
        
        df = pd.DataFrame(rows)
        self.logger.info(f"Processed {len(df)} product variants")
        return df
    
    def calculate_product_performance(self, products_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate product performance metrics (units sold, revenue, profit by time period)
        
        Args:
            products_df: Processed products DataFrame
            orders_df: Processed orders DataFrame
            
        Returns:
            Enhanced products DataFrame with performance metrics
        """
        self.logger.info("Calculating product performance metrics...")
        
        if orders_df.empty or products_df.empty:
            return products_df
        
        # Get current date
        now = datetime.now()
        date_30d = now - timedelta(days=30)
        date_60d = now - timedelta(days=60)
        date_90d = now - timedelta(days=90)
        
        # Convert Date column to datetime
        orders_df['Date'] = pd.to_datetime(orders_df['Date'], errors='coerce')
        
        # Calculate metrics for each variant
        for idx, row in products_df.iterrows():
            variant_id = row.get('Variant ID', '')
            sku = row.get('SKU', '')
            
            if not variant_id and not sku:
                continue
            
            # Filter orders for this variant
            if variant_id:
                variant_orders = orders_df[orders_df['Variant ID'] == variant_id]
            else:
                variant_orders = orders_df[orders_df['SKU'] == sku]
            
            if variant_orders.empty:
                continue
            
            # Calculate for different time periods
            for days, suffix in [(30, '30 days'), (60, '60 days'), (90, '90 days')]:
                cutoff_date = now - timedelta(days=days)
                period_orders = variant_orders[variant_orders['Date'] >= cutoff_date]
                
                units_sold = period_orders['Quantity'].sum()
                revenue = period_orders['Line Total'].sum()
                cost = row.get('Cost (COGS)', 0.0) * units_sold
                profit = revenue - cost
                margin = (profit / revenue * 100) if revenue > 0 else 0.0
                
                products_df.at[idx, f'Units Sold ({suffix})'] = int(units_sold)
                products_df.at[idx, f'Revenue ({suffix})'] = float(revenue)
                products_df.at[idx, f'Profit ({suffix})'] = float(profit)
            
            # Calculate margin
            price = row.get('Price', 0.0)
            cost = row.get('Cost (COGS)', 0.0)
            if price > 0:
                margin = ((price - cost) / price * 100) if cost > 0 else 0.0
                products_df.at[idx, 'Margin %'] = float(margin)
            
            # Calculate turnover rate (units sold 90 days / average inventory)
            units_90d = products_df.at[idx, 'Units Sold (90 days)']
            avg_inventory = row.get('Total Stock', 0)
            if avg_inventory > 0:
                turnover = (units_90d / 90) / avg_inventory * 90  # Annualized
                products_df.at[idx, 'Turnover Rate'] = float(turnover)
            
            # Calculate days of inventory remaining
            daily_sales = units_90d / 90 if units_90d > 0 else 0
            if daily_sales > 0:
                days_remaining = avg_inventory / daily_sales
                products_df.at[idx, 'Days of Inventory Remaining'] = float(days_remaining)
        
        self.logger.info("Product performance metrics calculated")
        return products_df
    
    def process_customers(self, customers: List[Dict], orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform customers data into DataFrame with customer metrics
        
        Args:
            customers: List of customer dictionaries from Shopify API
            orders_df: Processed orders DataFrame
            
        Returns:
            DataFrame with columns matching Customer Analytics sheet structure
        """
        self.logger.info(f"Processing {len(customers)} customers...")
        
        # Build customer order summary from orders_df
        customer_orders = {}
        if not orders_df.empty:
            for _, order_row in orders_df.groupby('Order ID').first().iterrows():
                customer_id = order_row.get('Customer ID', '')
                customer_email = order_row.get('Customer Email', '')
                
                if customer_id or customer_email:
                    key = str(customer_id) if customer_id else customer_email
                    if key not in customer_orders:
                        customer_orders[key] = {
                            'order_totals': [],
                            'order_dates': [],
                            'order_ids': [],
                            'items_purchased': 0
                        }
                    
                    customer_orders[key]['order_totals'].append(order_row.get('Order Total', 0.0))
                    customer_orders[key]['order_dates'].append(order_row.get('Date', ''))
                    customer_orders[key]['order_ids'].append(order_row.get('Order ID', ''))
            
            # Count items per customer
            for _, row in orders_df.iterrows():
                customer_id = row.get('Customer ID', '')
                customer_email = row.get('Customer Email', '')
                key = str(customer_id) if customer_id else customer_email
                if key in customer_orders:
                    customer_orders[key]['items_purchased'] += row.get('Quantity', 0)
        
        rows = []
        
        for customer in customers:
            customer_id = customer.get('id', '')
            first_name = customer.get('first_name', '')
            last_name = customer.get('last_name', '')
            full_name = f"{first_name} {last_name}".strip()
            email = customer.get('email', '')
            phone = customer.get('phone', '')
            
            # Address
            default_address = customer.get('default_address', {})
            address = self._format_address(default_address)
            city = default_address.get('city', '')
            state = default_address.get('province', '')
            country = default_address.get('country', '')
            zip_code = default_address.get('zip', '')
            
            # Customer metadata
            tags = ', '.join(customer.get('tags', [])) if isinstance(customer.get('tags'), list) else customer.get('tags', '')
            accepts_marketing = 'Yes' if customer.get('accepts_marketing', False) else 'No'
            
            # Get order history
            key = str(customer_id) if customer_id else email
            order_history = customer_orders.get(key, {})
            
            order_totals = order_history.get('order_totals', [])
            order_dates = [d for d in order_history.get('order_dates', []) if d]
            total_orders = len(order_totals)
            lifetime_value = sum(order_totals) if order_totals else 0.0
            average_order_value = lifetime_value / total_orders if total_orders > 0 else 0.0
            largest_order_value = max(order_totals) if order_totals else 0.0
            
            first_purchase_date = min(order_dates) if order_dates else ''
            last_purchase_date = max(order_dates) if order_dates else ''
            
            # Calculate days since last purchase
            days_since_last = ''
            if last_purchase_date:
                try:
                    now = datetime.now()
                    last_dt = pd.to_datetime(last_purchase_date)
                    days_since_last = (now - last_dt).days
                except:
                    days_since_last = ''
            
            total_items = order_history.get('items_purchased', 0)
            average_items_per_order = total_items / total_orders if total_orders > 0 else 0.0
            
            # Determine customer segment
            if total_orders == 0:
                segment = 'New'
            elif lifetime_value >= 500:  # VIP threshold
                segment = 'VIP'
            elif total_orders > 1:
                segment = 'Returning'
            else:
                segment = 'New'
            
            # Get favorite product (most purchased)
            customer_orders_df = orders_df[
                (orders_df['Customer ID'] == customer_id) | (orders_df['Customer Email'] == email)
            ] if not orders_df.empty else pd.DataFrame()
            
            favorite_category = ''
            favorite_product = ''
            if not customer_orders_df.empty:
                product_counts = customer_orders_df['Product Name'].value_counts()
                if not product_counts.empty:
                    favorite_product = product_counts.index[0]
            
            rows.append({
                'Customer ID': customer_id,
                'First Name': first_name,
                'Last Name': last_name,
                'Full Name': full_name,
                'Email': email,
                'Phone': phone,
                'Address': address,
                'City': city,
                'State': state,
                'Country': country,
                'ZIP': zip_code,
                'Customer Tags': tags,
                'Accepts Marketing': accepts_marketing,
                'First Purchase Date': first_purchase_date,
                'Last Purchase Date': last_purchase_date,
                'Total Orders': total_orders,
                'Total Spent (Lifetime Value)': lifetime_value,
                'Average Order Value': average_order_value,
                'Largest Order Value': largest_order_value,
                'Favorite Product Category': favorite_category,
                'Favorite Product': favorite_product,
                'Customer Segment': segment,
                'Days Since Last Purchase': days_since_last,
                'Total Items Purchased': total_items,
                'Average Items Per Order': average_items_per_order,
                'Preferred Payment Method': '',  # Would need to analyze orders
                'Preferred Shipping Method': '',  # Would need to analyze orders
                'Account Status': 'Active'
            })
        
        df = pd.DataFrame(rows)
        self.logger.info(f"Processed {len(df)} customers")
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate data
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        # Fill NaN values
        df = df.fillna('')
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Trim whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        
        return df
    
    def _parse_currency(self, value: str) -> float:
        """Parse currency string to float"""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            value = value.replace('$', '').replace(',', '').strip()
            try:
                return float(value)
            except:
                return 0.0
        return 0.0
    
    def _format_address(self, address: Dict) -> str:
        """Format address dictionary to string"""
        if not address:
            return ''
        
        parts = [
            address.get('address1', ''),
            address.get('address2', ''),
            address.get('city', ''),
            address.get('province', ''),
            address.get('zip', ''),
            address.get('country', '')
        ]
        return ', '.join([p for p in parts if p])


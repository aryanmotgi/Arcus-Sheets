"""
Shopify API Client for fetching store data
"""
import requests
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ShopifyClient:
    """Client for interacting with Shopify Admin API"""
    
    def __init__(self, store_url: str, api_key: Optional[str] = None, 
                 client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize Shopify client
        
        Args:
            store_url: Shopify store URL (e.g., 'your-store.myshopify.com')
            api_key: Shopify Admin API access token (preferred method)
            client_id: Client ID for Client Credentials Grant (alternative method)
            client_secret: Client Secret for Client Credentials Grant (alternative method)
        """
        self.logger = logging.getLogger(__name__)
        self.store_url = store_url.rstrip('/')
        if not self.store_url.startswith('https://'):
            self.store_url = f"https://{self.store_url}"
        
        # Use direct API key if provided, otherwise generate token
        if api_key:
            self.api_key = api_key
        elif client_id and client_secret:
            self.api_key = self._generate_token(client_id, client_secret)
        else:
            raise ValueError("Either 'api_key' or both 'client_id' and 'client_secret' must be provided")
        
        self.headers = {
            'X-Shopify-Access-Token': self.api_key,
            'Content-Type': 'application/json'
        }
        self.base_url = f"{self.store_url}/admin/api/2024-01"
        
        # Rate limiting: Shopify allows 2 requests per second
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests
    
    def _generate_token(self, client_id: str, client_secret: str) -> str:
        """
        Generate Admin API access token using Client Credentials Grant
        
        Args:
            client_id: Client ID from Shopify app
            client_secret: Client Secret from Shopify app
            
        Returns:
            Access token string
        """
        url = f"{self.store_url}/admin/oauth/access_token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()
        
        access_token = result.get('access_token')
        if not access_token:
            raise ValueError(f"Failed to generate token: {result}")
        
        return access_token
    
    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None, max_retries: int = 3) -> List[Dict]:
        """
        Make API request and handle pagination with rate limiting and retry logic
        
        Args:
            endpoint: API endpoint (e.g., '/orders.json')
            params: Query parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of all items across all pages
        """
        url = f"{self.base_url}{endpoint}"
        all_items = []
        params = params or {}
        page_count = 0
        
        while url:
            # Rate limiting
            self._rate_limit()
            
            # Retry logic
            retries = 0
            while retries < max_retries:
                try:
                    start_time = time.time()
                    response = requests.get(url, headers=self.headers, params=params, timeout=30)
                    response_time = time.time() - start_time
                    
                    # Handle rate limiting (429 status)
                    if response.status_code == 429:
                        retry_after = int(response.headers.get('Retry-After', 2))
                        self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                        time.sleep(retry_after)
                        retries += 1
                        continue
                    
                    # Handle server errors (5xx)
                    if response.status_code >= 500:
                        self.logger.warning(f"Server error {response.status_code}. Retrying...")
                        time.sleep(2 ** retries)  # Exponential backoff
                        retries += 1
                        continue
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    page_count += 1
                    self.logger.debug(f"Fetched page {page_count} from {endpoint} in {response_time:.2f}s")
                    
                    # Extract items (structure varies by endpoint)
                    if 'orders' in data:
                        items = data['orders']
                        all_items.extend(items)
                        self.logger.debug(f"Found {len(items)} orders on this page")
                    elif 'products' in data:
                        items = data['products']
                        all_items.extend(items)
                        self.logger.debug(f"Found {len(items)} products on this page")
                    elif 'customers' in data:
                        items = data['customers']
                        all_items.extend(items)
                        self.logger.debug(f"Found {len(items)} customers on this page")
                    elif 'inventory_levels' in data:
                        items = data['inventory_levels']
                        all_items.extend(items)
                        self.logger.debug(f"Found {len(items)} inventory levels on this page")
                    else:
                        items = data.get('data', [])
                        all_items.extend(items)
                    
                    break  # Success, exit retry loop
                    
                except requests.exceptions.RequestException as e:
                    retries += 1
                    if retries >= max_retries:
                        self.logger.error(f"Failed to fetch {endpoint} after {max_retries} retries: {e}")
                        raise
                    self.logger.warning(f"Request failed: {e}. Retrying ({retries}/{max_retries})...")
                    time.sleep(2 ** retries)  # Exponential backoff
            
            # Handle pagination via Link header
            link_header = response.headers.get('Link', '')
            if 'rel="next"' in link_header:
                # Extract next URL from Link header
                for link in link_header.split(','):
                    if 'rel="next"' in link:
                        url = link.split(';')[0].strip('<>')
                        params = None  # URL contains full query string
                        break
                else:
                    url = None
            else:
                url = None
        
        self.logger.info(f"Fetched {len(all_items)} total items from {endpoint}")
        return all_items
    
    def get_orders(self, limit: int = 250, since_id: Optional[int] = None, 
                   created_at_min: Optional[str] = None, status: str = 'any') -> List[Dict]:
        """
        Fetch all orders from Shopify
        
        Args:
            limit: Number of orders per page (max 250)
            since_id: Fetch orders with ID greater than this value
            created_at_min: Fetch orders created at or after this date (ISO 8601 format)
            status: Order status filter ('any', 'open', 'closed', 'cancelled')
            
        Returns:
            List of order dictionaries
        """
        params = {'limit': limit, 'status': status}
        if since_id:
            params['since_id'] = since_id
        if created_at_min:
            params['created_at_min'] = created_at_min
        
        self.logger.info(f"Fetching orders (status={status}, since_id={since_id}, created_at_min={created_at_min})...")
        return self._make_request('/orders.json', params=params)
    
    def get_products(self, limit: int = 250, since_id: Optional[int] = None, 
                    status: str = 'active') -> List[Dict]:
        """
        Fetch all products from Shopify
        
        Args:
            limit: Number of products per page (max 250)
            since_id: Fetch products with ID greater than this value
            status: Product status filter ('active', 'archived', 'draft', 'all')
            
        Returns:
            List of product dictionaries
        """
        params = {'limit': limit}
        if since_id:
            params['since_id'] = since_id
        if status != 'all':
            params['status'] = status
        
        self.logger.info(f"Fetching products (status={status}, since_id={since_id})...")
        return self._make_request('/products.json', params=params)
    
    def get_customers(self, limit: int = 250, since_id: Optional[int] = None) -> List[Dict]:
        """
        Fetch all customers from Shopify
        
        Args:
            limit: Number of customers per page (max 250)
            since_id: Fetch customers with ID greater than this value
            
        Returns:
            List of customer dictionaries
        """
        params = {'limit': limit}
        if since_id:
            params['since_id'] = since_id
        
        self.logger.info(f"Fetching customers (since_id={since_id})...")
        return self._make_request('/customers.json', params=params)
    
    def get_inventory_levels(self, location_ids: Optional[List[int]] = None) -> Dict:
        """
        Fetch inventory levels from Shopify
        
        Args:
            location_ids: Optional list of location IDs to filter by
            
        Returns:
            Dictionary mapping inventory_item_id to inventory data
        """
        params = {'limit': 250}
        if location_ids:
            params['location_ids'] = ','.join(map(str, location_ids))
        
        self.logger.info("Fetching inventory levels...")
        inventory_levels = self._make_request('/inventory_levels.json', params=params)
        
        # Convert to dictionary keyed by inventory_item_id
        inventory_dict = {}
        for inv in inventory_levels:
            item_id = inv.get('inventory_item_id')
            if item_id:
                if item_id not in inventory_dict:
                    inventory_dict[item_id] = {
                        'available': 0,
                        'locations': []
                    }
                available = inv.get('available', 0)
                inventory_dict[item_id]['available'] += available
                inventory_dict[item_id]['locations'].append({
                    'location_id': inv.get('location_id'),
                    'available': available
                })
        
        self.logger.info(f"Fetched inventory levels for {len(inventory_dict)} items")
        return inventory_dict


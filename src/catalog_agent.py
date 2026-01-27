"""
Catalog Agent - Handles products, costs, pricing, and new product planning
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class CatalogAgent:
    """Agent specialized in product catalog management and pricing"""
    
    def __init__(self, sheets_manager, shopify_client=None):
        """Initialize with SheetsManager and optional ShopifyClient"""
        self.sheets_manager = sheets_manager
        self.shopify_client = shopify_client
        self.logger = logging.getLogger(__name__)
    
    def process_command(self, command: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Process catalog-related commands
        
        Examples:
            - "set cost for SKU ARCUS-TEE to 12.26"
            - "suggest price for target margin 65%"
            - "show low inventory"
            - "plan new product hoodie at 46 cost"
        """
        command_lower = command.lower().strip()
        
        # Set cost for SKU
        if any(phrase in command_lower for phrase in ['set cost', 'update cost', 'cost for sku']):
            return self._set_cost_for_sku(command, dry_run)
        
        # Suggest price
        if any(phrase in command_lower for phrase in ['suggest price', 'price for margin', 'target margin']):
            return self._suggest_price(command)
        
        # Low inventory
        if any(phrase in command_lower for phrase in ['low inventory', 'low stock', 'out of stock']):
            return self._show_low_inventory()
        
        # New product planning
        if any(phrase in command_lower for phrase in ['plan new product', 'new product', 'plan product']):
            return self._plan_new_product(command, dry_run)
        
        # Get product info
        if any(phrase in command_lower for phrase in ['product info', 'show product', 'get product']):
            return self._get_product_info(command)
        
        return {
            'success': False,
            'message': 'Catalog Agent: I can help with:\n'
                      '• "set cost for SKU ARCUS-TEE to 12.26" - Update product cost\n'
                      '• "suggest price for target margin 65%" - Calculate price\n'
                      '• "show low inventory" - List low stock items\n'
                      '• "plan new product hoodie at 46 cost" - Plan new product'
        }
    
    def _set_cost_for_sku(self, command: str, dry_run: bool = False) -> Dict[str, Any]:
        """Set unit cost for a SKU"""
        # Extract SKU
        sku_match = re.search(r'sku\s+([A-Z0-9\-]+)', command, re.IGNORECASE)
        if not sku_match:
            return {'success': False, 'message': 'Please specify a SKU, e.g., "set cost for SKU ARCUS-TEE to 12.26"'}
        
        sku = sku_match.group(1).upper()
        
        # Extract cost
        cost_match = re.search(r'to\s+(\d+\.?\d*)', command, re.IGNORECASE)
        if not cost_match:
            return {'success': False, 'message': 'Please specify a cost value'}
        
        cost = float(cost_match.group(1))
        
        plan = {
            'action': 'set_cost',
            'sku': sku,
            'cost': cost,
            'dry_run': dry_run
        }
        
        if dry_run:
            return {
                'success': True,
                'message': f'📋 **Plan:** Set cost for SKU {sku} to ${cost:.2f}\n\n'
                          f'Add " apply" to execute.',
                'plan': plan
            }
        
        # Execute - update PRODUCTS sheet
        try:
            products_sheet = self.sheets_manager.create_sheet_if_not_exists("PRODUCTS")
            all_data = products_sheet.get_all_values()
            
            if not all_data or len(all_data) < 2:
                return {'success': False, 'message': 'PRODUCTS sheet is empty. Create products first.'}
            
            headers = all_data[0]
            try:
                sku_col_idx = headers.index("sku")
                cost_col_idx = headers.index("unit_cost")
            except ValueError:
                return {'success': False, 'message': 'PRODUCTS sheet missing required columns'}
            
            # Find row with matching SKU
            updated = False
            for idx, row in enumerate(all_data[1:], start=2):
                if len(row) > sku_col_idx and str(row[sku_col_idx]).upper() == sku:
                    # Update cost
                    products_sheet.update(f'{chr(64 + cost_col_idx + 1)}{idx}', cost)
                    updated = True
                    break
            
            if not updated:
                return {'success': False, 'message': f'SKU {sku} not found in PRODUCTS sheet'}
            
            return {
                'success': True,
                'message': f'✅ **Cost Updated!**\n\n'
                          f'📦 SKU: {sku}\n'
                          f'💵 Cost: ${cost:.2f}\n\n'
                          f'✅ Updated in PRODUCTS sheet',
                'data': {'sku': sku, 'cost': cost}
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _suggest_price(self, command: str) -> Dict[str, Any]:
        """Suggest price based on target margin"""
        # Extract target margin
        margin_match = re.search(r'(\d+)%', command)
        if not margin_match:
            return {'success': False, 'message': 'Please specify target margin, e.g., "suggest price for target margin 65%"'}
        
        target_margin = float(margin_match.group(1)) / 100
        
        # Extract cost if provided
        cost_match = re.search(r'cost\s+(\d+\.?\d*)', command, re.IGNORECASE)
        if cost_match:
            cost = float(cost_match.group(1))
            suggested_price = cost / (1 - target_margin)
            
            return {
                'success': True,
                'message': f'💰 **Price Suggestion**\n\n'
                          f'💵 Cost: ${cost:.2f}\n'
                          f'📊 Target Margin: {target_margin*100:.1f}%\n'
                          f'💲 Suggested Price: ${suggested_price:.2f}\n\n'
                          f'Formula: Cost / (1 - Margin)',
                'data': {
                    'cost': cost,
                    'target_margin': target_margin,
                    'suggested_price': suggested_price
                }
            }
        
        return {
            'success': False,
            'message': 'Please provide a cost value, e.g., "suggest price for cost 12.26 with target margin 65%"'
        }
    
    def _show_low_inventory(self) -> Dict[str, Any]:
        """Show products with low inventory"""
        try:
            products_sheet = self.sheets_manager.create_sheet_if_not_exists("PRODUCTS")
            all_data = products_sheet.get_all_values()
            
            if not all_data or len(all_data) < 2:
                return {'success': True, 'message': 'No products found', 'data': {'count': 0}}
            
            headers = all_data[0]
            try:
                inventory_col_idx = headers.index("inventory_qty")
                product_col_idx = headers.index("product_name")
                sku_col_idx = headers.index("sku")
            except ValueError:
                return {'success': False, 'message': 'PRODUCTS sheet missing required columns'}
            
            low_inventory = []
            for row in all_data[1:]:
                if len(row) > inventory_col_idx:
                    try:
                        qty = int(float(str(row[inventory_col_idx]).replace(',', '')))
                        if qty < 10:  # Low inventory threshold
                            product = {
                                'product_name': row[product_col_idx] if len(row) > product_col_idx else 'N/A',
                                'sku': row[sku_col_idx] if len(row) > sku_col_idx else 'N/A',
                                'inventory_qty': qty
                            }
                            low_inventory.append(product)
                    except:
                        pass
            
            if not low_inventory:
                return {
                    'success': True,
                    'message': '✅ **All products have sufficient inventory!**',
                    'data': {'count': 0}
                }
            
            message = f'⚠️ **Low Inventory: {len(low_inventory)} products**\n\n'
            for idx, product in enumerate(low_inventory[:10], 1):
                message += f'{idx}. {product["product_name"]} ({product["sku"]}): {product["inventory_qty"]} units\n'
            
            if len(low_inventory) > 10:
                message += f'\n... and {len(low_inventory) - 10} more'
            
            return {
                'success': True,
                'message': message,
                'data': {'count': len(low_inventory), 'products': low_inventory}
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _plan_new_product(self, command: str, dry_run: bool = False) -> Dict[str, Any]:
        """Plan a new product"""
        # Extract product name
        name_match = re.search(r'product\s+([^at]+?)(?:\s+at|\s+cost|$)', command, re.IGNORECASE)
        if not name_match:
            return {'success': False, 'message': 'Please specify product name, e.g., "plan new product hoodie at 46 cost"'}
        
        product_name = name_match.group(1).strip()
        
        # Extract cost
        cost_match = re.search(r'(\d+\.?\d*)\s+cost', command, re.IGNORECASE)
        if not cost_match:
            cost_match = re.search(r'at\s+(\d+\.?\d*)', command, re.IGNORECASE)
        
        if not cost_match:
            return {'success': False, 'message': 'Please specify cost, e.g., "at 46 cost"'}
        
        cost = float(cost_match.group(1))
        
        # Extract target margin if provided
        margin_match = re.search(r'(\d+)%', command)
        target_margin = 0.65  # Default 65%
        if margin_match:
            target_margin = float(margin_match.group(1)) / 100
        
        suggested_price = cost / (1 - target_margin)
        
        plan = {
            'action': 'plan_product',
            'product_name': product_name,
            'estimated_unit_cost': cost,
            'target_margin': target_margin,
            'suggested_price': suggested_price,
            'dry_run': dry_run
        }
        
        if dry_run:
            return {
                'success': True,
                'message': f'📋 **New Product Plan:**\n\n'
                          f'📦 Product: {product_name}\n'
                          f'💵 Estimated Cost: ${cost:.2f}\n'
                          f'📊 Target Margin: {target_margin*100:.1f}%\n'
                          f'💲 Suggested Price: ${suggested_price:.2f}\n\n'
                          f'Add " apply" to add to NEW_PRODUCT_PLANNING sheet.',
                'plan': plan
            }
        
        # Execute - add to NEW_PRODUCT_PLANNING sheet
        try:
            planning_sheet = self.sheets_manager.create_sheet_if_not_exists("NEW_PRODUCT_PLANNING")
            
            # Ensure headers exist
            all_data = planning_sheet.get_all_values()
            if not all_data or len(all_data) < 1:
                headers = ["product_name", "estimated_unit_cost", "target_margin", "suggested_price", "break_even_units", "notes"]
                planning_sheet.update('A1', [headers])
            
            # Calculate break-even (simplified: assume fixed costs spread)
            break_even = 100  # Placeholder
            
            row_data = [
                product_name,
                cost,
                f"{target_margin*100:.1f}%",
                suggested_price,
                break_even,
                ""
            ]
            
            planning_sheet.append_row(row_data)
            
            return {
                'success': True,
                'message': f'✅ **Product Plan Added!**\n\n'
                          f'📦 Product: {product_name}\n'
                          f'💵 Cost: ${cost:.2f}\n'
                          f'💲 Suggested Price: ${suggested_price:.2f}\n\n'
                          f'✅ Added to NEW_PRODUCT_PLANNING sheet',
                'data': plan
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _get_product_info(self, command: str) -> Dict[str, Any]:
        """Get product information"""
        # Extract product name or SKU
        product_match = re.search(r'(?:product|sku)\s+([A-Z0-9\-\s]+)', command, re.IGNORECASE)
        if not product_match:
            return {'success': False, 'message': 'Please specify a product name or SKU'}
        
        search_term = product_match.group(1).strip().upper()
        
        try:
            products_sheet = self.sheets_manager.create_sheet_if_not_exists("PRODUCTS")
            all_data = products_sheet.get_all_values()
            
            if not all_data or len(all_data) < 2:
                return {'success': False, 'message': 'PRODUCTS sheet is empty'}
            
            headers = all_data[0]
            
            # Find matching product
            for row in all_data[1:]:
                product_name = str(row[0] if len(row) > 0 else '').upper()
                sku = str(row[1] if len(row) > 1 else '').upper()
                
                if search_term in product_name or search_term in sku:
                    return {
                        'success': True,
                        'message': f'📦 **Product Found:**\n\n'
                                  f'Name: {row[0] if len(row) > 0 else "N/A"}\n'
                                  f'SKU: {row[1] if len(row) > 1 else "N/A"}\n'
                                  f'Cost: {row[2] if len(row) > 2 else "N/A"}\n'
                                  f'Price: {row[3] if len(row) > 3 else "N/A"}',
                        'data': dict(zip(headers, row))
                    }
            
            return {'success': False, 'message': f'Product "{search_term}" not found'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

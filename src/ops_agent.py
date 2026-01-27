"""
Ops Agent - Handles fulfillment operations and manual overrides
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class OpsAgent:
    """Agent specialized in fulfillment operations and manual data entry"""
    
    def __init__(self, sheets_manager, shopify_client=None):
        """Initialize with SheetsManager and optional ShopifyClient"""
        self.sheets_manager = sheets_manager
        self.shopify_client = shopify_client
        self.logger = logging.getLogger(__name__)
    
    def process_command(self, command: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Process ops-related commands with plan→apply pattern
        
        Examples:
            - "set shipping label cost to 4.85 for order 1042"
            - "set PSL to XYZ for order 1042"
            - "add note 'USPS ground' to order 1042"
            - "show unfulfilled orders"
            - "show missing shipping label cost"
            - "set shipping label cost to 4.12 for the last 6 unfulfilled orders"
        """
        command_lower = command.lower().strip()
        
        # Shipping label cost operations
        if any(phrase in command_lower for phrase in ['shipping label cost', 'label cost', 'set cost']):
            if 'show' in command_lower or 'list' in command_lower or 'missing' in command_lower:
                return self._show_missing_label_costs()
            else:
                return self._set_shipping_label_cost(command, dry_run)
        
        # PSL operations
        if 'psl' in command_lower:
            if 'set' in command_lower or 'update' in command_lower:
                return self._set_psl(command, dry_run)
            else:
                return self._get_psl(command)
        
        # Notes operations
        if 'note' in command_lower:
            if 'add' in command_lower or 'set' in command_lower or 'update' in command_lower:
                return self._add_note(command, dry_run)
            else:
                return self._get_note(command)
        
        # Unfulfilled orders
        if any(phrase in command_lower for phrase in ['unfulfilled', 'not fulfilled', 'pending fulfillment']):
            return self._show_unfulfilled_orders()
        
        # Negative profit orders
        if any(phrase in command_lower for phrase in ['negative profit', 'losing money', 'unprofitable']):
            return self._show_negative_profit_orders()
        
        # General ops help
        return {
            'success': False,
            'message': 'Ops Agent: I can help with:\n'
                      '• "set shipping label cost to 4.85 for order 1042" - Set label cost\n'
                      '• "set PSL to XYZ for order 1042" - Set PSL value\n'
                      '• "add note \'USPS ground\' to order 1042" - Add note\n'
                      '• "show unfulfilled orders" - List unfulfilled\n'
                      '• "show missing shipping label cost" - List missing costs\n'
                      '• "show negative profit orders" - List unprofitable orders'
        }
    
    def _parse_order_identifier(self, command: str) -> tuple:
        """Extract order_id or order_number from command"""
        # Try to find order number (e.g., "order 1042", "#1042", "1042")
        order_number_match = re.search(r'(?:order|#)?\s*(\d+)', command, re.IGNORECASE)
        if order_number_match:
            order_number = order_number_match.group(1)
            # Try to find order_id from RAW_ORDERS or ORDERS sheet
            order_id = self._get_order_id_from_number(order_number)
            return order_id, order_number
        
        return None, None
    
    def _get_order_id_from_number(self, order_number: str) -> Optional[str]:
        """Look up order_id from order_number in RAW_ORDERS or ORDERS sheet"""
        try:
            # Try RAW_ORDERS first
            try:
                sheet = self.sheets_manager.create_sheet_if_not_exists("RAW_ORDERS")
            except:
                # Fall back to ORDERS
                sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            
            all_data = sheet.get_all_values()
            if not all_data or len(all_data) < 2:
                return None
            
            # Find order_number column index
            headers = all_data[0]
            try:
                order_num_col = headers.index("Order Number")
            except ValueError:
                try:
                    order_num_col = headers.index("order_number")
                except ValueError:
                    return None
            
            # Find order_id column
            try:
                order_id_col = headers.index("Order ID")
            except ValueError:
                try:
                    order_id_col = headers.index("order_id")
                except ValueError:
                    return None
            
            # Search for matching order_number
            for row in all_data[1:]:
                if len(row) > order_num_col and str(row[order_num_col]) == str(order_number):
                    if len(row) > order_id_col:
                        return str(row[order_id_col])
            
            return None
        except Exception as e:
            self.logger.error(f"Error looking up order_id: {e}")
            return None
    
    def _set_shipping_label_cost(self, command: str, dry_run: bool = False) -> Dict[str, Any]:
        """Set shipping label cost for an order"""
        # Extract cost value
        cost_match = re.search(r'(\d+\.?\d*)', command)
        if not cost_match:
            return {'success': False, 'message': 'Please specify a cost value, e.g., "set shipping label cost to 4.85 for order 1042"'}
        
        cost = float(cost_match.group(1))
        
        # Extract order identifier
        order_id, order_number = self._parse_order_identifier(command)
        
        if not order_id and not order_number:
            # Try to find "last N orders" pattern
            last_match = re.search(r'last\s+(\d+)', command, re.IGNORECASE)
            if last_match:
                n = int(last_match.group(1))
                return self._set_label_cost_for_unfulfilled(command, cost, n, dry_run)
            
            return {'success': False, 'message': 'Please specify an order number, e.g., "order 1042"'}
        
        # Create plan
        plan = {
            'action': 'set_shipping_label_cost',
            'order_id': order_id,
            'order_number': order_number,
            'cost': cost,
            'dry_run': dry_run
        }
        
        if dry_run:
            return {
                'success': True,
                'message': f'📋 **Plan:** Set shipping label cost to ${cost:.2f} for order {order_number or order_id}\n\n'
                          f'Add " apply" to execute this change.',
                'plan': plan
            }
        
        # Execute
        try:
            override = self.sheets_manager.get_manual_override(order_id=order_id, order_number=order_number)
            if override:
                # Update existing
                self.sheets_manager.upsert_manual_override(
                    order_id=order_id or override.get('order_id', ''),
                    order_number=order_number or override.get('order_number', ''),
                    shipping_label_cost=cost,
                    updated_by="ops_agent"
                )
            else:
                # Create new
                self.sheets_manager.upsert_manual_override(
                    order_id=order_id or '',
                    order_number=order_number or '',
                    shipping_label_cost=cost,
                    updated_by="ops_agent"
                )
            
            return {
                'success': True,
                'message': f'✅ **Shipping Label Cost Set!**\n\n'
                          f'💰 Cost: ${cost:.2f}\n'
                          f'📦 Order: {order_number or order_id}\n\n'
                          f'✅ Saved to MANUAL_OVERRIDES',
                'data': {'order_id': order_id, 'order_number': order_number, 'cost': cost}
            }
        except Exception as e:
            self.logger.error(f"Error setting shipping label cost: {e}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _set_label_cost_for_unfulfilled(self, command: str, cost: float, n: int, dry_run: bool) -> Dict[str, Any]:
        """Set label cost for last N unfulfilled orders"""
        unfulfilled = self._get_unfulfilled_orders_list()
        
        if not unfulfilled:
            return {'success': False, 'message': 'No unfulfilled orders found'}
        
        # Get last N
        target_orders = unfulfilled[:n] if len(unfulfilled) >= n else unfulfilled
        
        plan = {
            'action': 'set_label_cost_batch',
            'orders': target_orders,
            'cost': cost,
            'count': len(target_orders)
        }
        
        if dry_run:
            order_list = ', '.join([o.get('order_number', o.get('order_id', '')) for o in target_orders])
            return {
                'success': True,
                'message': f'📋 **Plan:** Set shipping label cost to ${cost:.2f} for {len(target_orders)} orders:\n'
                          f'{order_list}\n\n'
                          f'Add " apply" to execute.',
                'plan': plan
            }
        
        # Execute
        updated = 0
        for order in target_orders:
            try:
                self.sheets_manager.upsert_manual_override(
                    order_id=order.get('order_id', ''),
                    order_number=order.get('order_number', ''),
                    shipping_label_cost=cost,
                    updated_by="ops_agent"
                )
                updated += 1
            except Exception as e:
                self.logger.error(f"Error updating order {order.get('order_number')}: {e}")
        
        return {
            'success': True,
            'message': f'✅ **Updated {updated} orders!**\n\n'
                      f'💰 Cost: ${cost:.2f}\n'
                      f'📦 Orders: {updated}',
            'data': {'updated': updated, 'cost': cost}
        }
    
    def _set_psl(self, command: str, dry_run: bool = False) -> Dict[str, Any]:
        """Set PSL value for an order"""
        # Extract PSL value (text after "to" or "=")
        psl_match = re.search(r'(?:to|is|=)\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s+for|\s*$)', command, re.IGNORECASE)
        if not psl_match:
            # Try simpler pattern
            psl_match = re.search(r'psl\s+(?:to|is|=)\s*([^\s]+)', command, re.IGNORECASE)
        
        if not psl_match:
            return {'success': False, 'message': 'Please specify a PSL value, e.g., "set PSL to XYZ123 for order 1042"'}
        
        psl = psl_match.group(1).strip()
        
        # Extract order identifier
        order_id, order_number = self._parse_order_identifier(command)
        
        if not order_id and not order_number:
            return {'success': False, 'message': 'Please specify an order number'}
        
        plan = {
            'action': 'set_psl',
            'order_id': order_id,
            'order_number': order_number,
            'psl': psl,
            'dry_run': dry_run
        }
        
        if dry_run:
            return {
                'success': True,
                'message': f'📋 **Plan:** Set PSL to "{psl}" for order {order_number or order_id}\n\n'
                          f'Add " apply" to execute.',
                'plan': plan
            }
        
        # Execute
        try:
            self.sheets_manager.upsert_manual_override(
                order_id=order_id or '',
                order_number=order_number or '',
                psl=psl,
                updated_by="ops_agent"
            )
            
            return {
                'success': True,
                'message': f'✅ **PSL Set!**\n\n'
                          f'📦 Order: {order_number or order_id}\n'
                          f'🏷️ PSL: {psl}\n\n'
                          f'✅ Saved to MANUAL_OVERRIDES',
                'data': {'order_id': order_id, 'order_number': order_number, 'psl': psl}
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _add_note(self, command: str, dry_run: bool = False) -> Dict[str, Any]:
        """Add note to an order"""
        # Extract note text (between quotes or after "note")
        note_match = re.search(r"note\s+['\"]([^'\"]+)['\"]", command, re.IGNORECASE)
        if not note_match:
            note_match = re.search(r"note\s+([^for]+?)(?:\s+for|$)", command, re.IGNORECASE)
        
        if not note_match:
            return {'success': False, 'message': 'Please specify a note, e.g., "add note \'USPS ground\' to order 1042"'}
        
        note = note_match.group(1).strip()
        
        # Extract order identifier
        order_id, order_number = self._parse_order_identifier(command)
        
        if not order_id and not order_number:
            return {'success': False, 'message': 'Please specify an order number'}
        
        plan = {
            'action': 'add_note',
            'order_id': order_id,
            'order_number': order_number,
            'note': note,
            'dry_run': dry_run
        }
        
        if dry_run:
            return {
                'success': True,
                'message': f'📋 **Plan:** Add note "{note}" to order {order_number or order_id}\n\n'
                          f'Add " apply" to execute.',
                'plan': plan
            }
        
        # Execute - append to existing note if present
        try:
            override = self.sheets_manager.get_manual_override(order_id=order_id, order_number=order_number)
            existing_note = override.get('notes', '') if override else ''
            
            if existing_note:
                new_note = f"{existing_note}\n{note}"
            else:
                new_note = note
            
            self.sheets_manager.upsert_manual_override(
                order_id=order_id or (override.get('order_id', '') if override else ''),
                order_number=order_number or (override.get('order_number', '') if override else ''),
                notes=new_note,
                updated_by="ops_agent"
            )
            
            return {
                'success': True,
                'message': f'✅ **Note Added!**\n\n'
                          f'📦 Order: {order_number or order_id}\n'
                          f'📝 Note: {note}\n\n'
                          f'✅ Saved to MANUAL_OVERRIDES',
                'data': {'order_id': order_id, 'order_number': order_number, 'note': note}
            }
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _show_unfulfilled_orders(self) -> Dict[str, Any]:
        """Show unfulfilled orders"""
        orders = self._get_unfulfilled_orders_list()
        
        if not orders:
            return {
                'success': True,
                'message': '✅ **All orders are fulfilled!**\n\nNo unfulfilled orders found.',
                'data': {'count': 0, 'orders': []}
            }
        
        # Format message
        message = f'📦 **Unfulfilled Orders: {len(orders)}**\n\n'
        for idx, order in enumerate(orders[:10], 1):  # Show first 10
            order_num = order.get('order_number', order.get('order_id', 'N/A'))
            message += f'{idx}. Order {order_num}\n'
        
        if len(orders) > 10:
            message += f'\n... and {len(orders) - 10} more'
        
        return {
            'success': True,
            'message': message,
            'data': {'count': len(orders), 'orders': orders}
        }
    
    def _get_unfulfilled_orders_list(self) -> List[Dict]:
        """Get list of unfulfilled orders"""
        try:
            # Try FULFILLMENT sheet first, then RAW_ORDERS or ORDERS
            try:
                sheet = self.sheets_manager.create_sheet_if_not_exists("FULFILLMENT")
            except:
                try:
                    sheet = self.sheets_manager.create_sheet_if_not_exists("RAW_ORDERS")
                except:
                    sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            
            all_data = sheet.get_all_values()
            if not all_data or len(all_data) < 2:
                return []
            
            headers = all_data[0]
            
            # Find fulfillment status column
            try:
                status_col = headers.index("Fulfillment Status")
            except ValueError:
                try:
                    status_col = headers.index("fulfillment_status")
                except ValueError:
                    # If no status column, return empty
                    return []
            
            # Find order_id and order_number columns
            try:
                order_id_col = headers.index("Order ID")
            except ValueError:
                try:
                    order_id_col = headers.index("order_id")
                except ValueError:
                    order_id_col = None
            
            try:
                order_num_col = headers.index("Order Number")
            except ValueError:
                try:
                    order_num_col = headers.index("order_number")
                except ValueError:
                    order_num_col = None
            
            unfulfilled = []
            for row in all_data[1:]:
                if len(row) > status_col:
                    status = str(row[status_col]).lower()
                    if 'unfulfilled' in status or status == '' or 'pending' in status:
                        order = {}
                        if order_id_col and len(row) > order_id_col:
                            order['order_id'] = str(row[order_id_col])
                        if order_num_col and len(row) > order_num_col:
                            order['order_number'] = str(row[order_num_col])
                        if order:
                            unfulfilled.append(order)
            
            return unfulfilled
        except Exception as e:
            self.logger.error(f"Error getting unfulfilled orders: {e}")
            return []
    
    def _show_missing_label_costs(self) -> Dict[str, Any]:
        """Show orders missing shipping label cost"""
        try:
            # Get all orders
            try:
                sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            except:
                sheet = self.sheets_manager.create_sheet_if_not_exists("RAW_ORDERS")
            
            all_data = sheet.get_all_values()
            if not all_data or len(all_data) < 2:
                return {'success': True, 'message': 'No orders found', 'data': {'count': 0}}
            
            headers = all_data[0]
            
            # Get all manual overrides
            overrides = self.sheets_manager.get_all_manual_overrides()
            override_map = {o.get('order_id', ''): o for o in overrides}
            
            # Find order columns
            try:
                order_id_col = headers.index("Order ID")
            except ValueError:
                try:
                    order_id_col = headers.index("order_id")
                except ValueError:
                    return {'success': False, 'message': 'Order ID column not found'}
            
            try:
                order_num_col = headers.index("Order Number")
            except ValueError:
                try:
                    order_num_col = headers.index("order_number")
                except ValueError:
                    order_num_col = None
            
            missing = []
            for row in all_data[1:]:
                if len(row) > order_id_col:
                    order_id = str(row[order_id_col])
                    override = override_map.get(order_id)
                    
                    if not override or not override.get('shipping_label_cost'):
                        order = {'order_id': order_id}
                        if order_num_col and len(row) > order_num_col:
                            order['order_number'] = str(row[order_num_col])
                        missing.append(order)
            
            if not missing:
                return {
                    'success': True,
                    'message': '✅ **All orders have shipping label costs!**',
                    'data': {'count': 0}
                }
            
            message = f'⚠️ **Missing Shipping Label Costs: {len(missing)}**\n\n'
            for idx, order in enumerate(missing[:10], 1):
                order_num = order.get('order_number', order.get('order_id', 'N/A'))
                message += f'{idx}. Order {order_num}\n'
            
            if len(missing) > 10:
                message += f'\n... and {len(missing) - 10} more'
            
            return {
                'success': True,
                'message': message,
                'data': {'count': len(missing), 'orders': missing}
            }
        except Exception as e:
            self.logger.error(f"Error finding missing label costs: {e}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _show_negative_profit_orders(self) -> Dict[str, Any]:
        """Show orders with negative profit"""
        try:
            sheet = self.sheets_manager.create_sheet_if_not_exists("ORDERS")
            all_data = sheet.get_all_values()
            
            if not all_data or len(all_data) < 2:
                return {'success': True, 'message': 'No orders found', 'data': {'count': 0}}
            
            headers = all_data[0]
            
            # Find profit column
            try:
                profit_col = headers.index("Profit")
            except ValueError:
                try:
                    profit_col = headers.index("profit")
                except ValueError:
                    return {'success': False, 'message': 'Profit column not found'}
            
            # Find order columns
            try:
                order_num_col = headers.index("Order Number")
            except ValueError:
                order_num_col = None
            
            negative = []
            for row in all_data[1:]:
                if len(row) > profit_col:
                    try:
                        profit = float(str(row[profit_col]).replace('$', '').replace(',', ''))
                        if profit < 0:
                            order = {'profit': profit}
                            if order_num_col and len(row) > order_num_col:
                                order['order_number'] = str(row[order_num_col])
                            negative.append(order)
                    except:
                        pass
            
            if not negative:
                return {
                    'success': True,
                    'message': '✅ **All orders are profitable!**',
                    'data': {'count': 0}
                }
            
            message = f'⚠️ **Negative Profit Orders: {len(negative)}**\n\n'
            for idx, order in enumerate(negative[:10], 1):
                order_num = order.get('order_number', 'N/A')
                profit = order.get('profit', 0)
                message += f'{idx}. Order {order_num}: ${profit:.2f}\n'
            
            if len(negative) > 10:
                message += f'\n... and {len(negative) - 10} more'
            
            return {
                'success': True,
                'message': message,
                'data': {'count': len(negative), 'orders': negative}
            }
        except Exception as e:
            self.logger.error(f"Error finding negative profit orders: {e}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def _get_psl(self, command: str) -> Dict[str, Any]:
        """Get PSL value for an order"""
        order_id, order_number = self._parse_order_identifier(command)
        
        if not order_id and not order_number:
            return {'success': False, 'message': 'Please specify an order number'}
        
        override = self.sheets_manager.get_manual_override(order_id=order_id, order_number=order_number)
        
        if override and override.get('psl'):
            return {
                'success': True,
                'message': f'🏷️ **PSL for Order {order_number or order_id}:** {override["psl"]}',
                'data': override
            }
        else:
            return {
                'success': True,
                'message': f'📦 Order {order_number or order_id} has no PSL set yet.',
                'data': None
            }
    
    def _get_note(self, command: str) -> Dict[str, Any]:
        """Get notes for an order"""
        order_id, order_number = self._parse_order_identifier(command)
        
        if not order_id and not order_number:
            return {'success': False, 'message': 'Please specify an order number'}
        
        override = self.sheets_manager.get_manual_override(order_id=order_id, order_number=order_number)
        
        if override and override.get('notes'):
            return {
                'success': True,
                'message': f'📝 **Notes for Order {order_number or order_id}:**\n\n{override["notes"]}',
                'data': override
            }
        else:
            return {
                'success': True,
                'message': f'📦 Order {order_number or order_id} has no notes yet.',
                'data': None
            }

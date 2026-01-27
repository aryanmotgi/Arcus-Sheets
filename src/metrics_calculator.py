"""
Metrics Calculator - Calculates and updates all KPIs in METRICS table
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def calculate_and_update_metrics(sheets_manager):
    """
    Calculate all metrics from ORDERS and MANUAL_OVERRIDES, then update METRICS table
    
    Metrics calculated:
    - total_revenue: Sum of Total Revenue from ORDERS
    - total_units: Sum of Quantity from ORDERS
    - total_cogs: Sum of (Unit Cost * Quantity) from ORDERS
    - total_shipping_label_cost: Sum from MANUAL_OVERRIDES
    - gross_profit: total_revenue - total_cogs
    - contribution_profit: total_revenue - total_cogs - total_shipping_label_cost
    - setup_costs: Fixed value (809.32) from METRICS
    - net_profit_after_setup: contribution_profit - setup_costs
    - unfulfilled_count: Count from FULFILLMENT sheet
    - missing_label_cost_count: Count orders without shipping_label_cost
    """
    logger.info("Calculating metrics from ORDERS and MANUAL_OVERRIDES...")
    
    try:
        # Ensure METRICS sheet exists
        sheets_manager.create_metrics_sheet()
        
        # Get ORDERS data
        try:
            orders_sheet = sheets_manager.create_sheet_if_not_exists("ORDERS")
            orders_data = orders_sheet.get_all_values()
        except:
            logger.warning("ORDERS sheet not found, using empty data")
            orders_data = []
        
        # Get MANUAL_OVERRIDES
        manual_overrides = sheets_manager.get_all_manual_overrides()
        
        # Initialize metrics
        total_revenue = 0.0
        total_units = 0.0
        total_cogs = 0.0
        total_shipping_label_cost = 0.0
        
        if orders_data and len(orders_data) > 1:
            headers = orders_data[0]
            
            # Find column indices
            try:
                revenue_col = headers.index("Total Revenue") if "Total Revenue" in headers else headers.index("Sold Price")
            except ValueError:
                revenue_col = None
            
            try:
                quantity_col = headers.index("Quantity")
            except ValueError:
                quantity_col = None
            
            try:
                unit_cost_col = headers.index("Unit Cost")
            except ValueError:
                unit_cost_col = None
            
            # Calculate from ORDERS
            for row in orders_data[1:]:
                if len(row) > 0:
                    # Revenue
                    if revenue_col and len(row) > revenue_col:
                        try:
                            revenue_val = str(row[revenue_col]).replace('$', '').replace(',', '').strip()
                            if revenue_val:
                                total_revenue += float(revenue_val)
                        except:
                            pass
                    
                    # Units
                    if quantity_col and len(row) > quantity_col:
                        try:
                            qty_val = str(row[quantity_col]).replace(',', '').strip()
                            if qty_val:
                                total_units += float(qty_val)
                        except:
                            pass
                    
                    # COGS (Unit Cost * Quantity)
                    if unit_cost_col and quantity_col and len(row) > max(unit_cost_col, quantity_col):
                        try:
                            cost_val = str(row[unit_cost_col]).replace('$', '').replace(',', '').strip()
                            qty_val = str(row[quantity_col]).replace(',', '').strip()
                            if cost_val and qty_val:
                                total_cogs += float(cost_val) * float(qty_val)
                        except:
                            pass
        
        # Calculate shipping label costs from MANUAL_OVERRIDES
        for override in manual_overrides:
            if override.get('shipping_label_cost'):
                try:
                    total_shipping_label_cost += float(override['shipping_label_cost'])
                except:
                    pass
        
        # Calculate derived metrics
        gross_profit = total_revenue - total_cogs
        contribution_profit = total_revenue - total_cogs - total_shipping_label_cost
        
        # Get setup_costs from METRICS (or use default)
        setup_costs = sheets_manager.get_metric("setup_costs")
        if setup_costs is None:
            setup_costs = 809.32
            sheets_manager.set_metric("setup_costs", setup_costs, "Setup Costs")
        
        net_profit_after_setup = contribution_profit - setup_costs
        
        # Count unfulfilled orders
        try:
            fulfillment_sheet = sheets_manager.create_sheet_if_not_exists("FULFILLMENT")
            fulfillment_data = fulfillment_sheet.get_all_values()
            unfulfilled_count = len(fulfillment_data) - 1 if fulfillment_data and len(fulfillment_data) > 1 else 0
        except:
            unfulfilled_count = 0
        
        # Count missing label costs
        missing_label_cost_count = 0
        if orders_data and len(orders_data) > 1:
            headers = orders_data[0]
            try:
                order_id_col = headers.index("Order ID") if "Order ID" in headers else headers.index("order_id")
            except ValueError:
                order_id_col = None
            
            if order_id_col:
                override_map = {o.get('order_id', ''): o for o in manual_overrides}
                for row in orders_data[1:]:
                    if len(row) > order_id_col:
                        order_id = str(row[order_id_col])
                        override = override_map.get(order_id)
                        if not override or not override.get('shipping_label_cost'):
                            missing_label_cost_count += 1
        
        # Update METRICS table
        metrics_to_update = {
            "total_revenue": (total_revenue, "Total Revenue"),
            "total_units": (total_units, "Total Units Sold"),
            "total_cogs": (total_cogs, "Total COGS"),
            "total_shipping_label_cost": (total_shipping_label_cost, "Total Shipping Label Cost"),
            "gross_profit": (gross_profit, "Gross Profit"),
            "contribution_profit": (contribution_profit, "Contribution Profit"),
            "net_profit_after_setup": (net_profit_after_setup, "Net Profit After Setup"),
            "unfulfilled_count": (unfulfilled_count, "Unfulfilled Orders"),
            "missing_label_cost_count": (missing_label_cost_count, "Missing Label Cost"),
        }
        
        for metric_key, (value, label) in metrics_to_update.items():
            sheets_manager.set_metric(metric_key, value, label)
        
        logger.info(f"✅ Metrics updated: Revenue=${total_revenue:.2f}, Profit=${net_profit_after_setup:.2f}")
        
        return {
            "total_revenue": total_revenue,
            "total_units": total_units,
            "total_cogs": total_cogs,
            "total_shipping_label_cost": total_shipping_label_cost,
            "gross_profit": gross_profit,
            "contribution_profit": contribution_profit,
            "setup_costs": setup_costs,
            "net_profit_after_setup": net_profit_after_setup,
            "unfulfilled_count": unfulfilled_count,
            "missing_label_cost_count": missing_label_cost_count
        }
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}", exc_info=True)
        raise

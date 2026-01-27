"""
Helper module to build view sheets that merge RAW_ORDERS with MANUAL_OVERRIDES
"""
import logging
from typing import List, Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def build_orders_view(manager, raw_sheet_name: str = "RAW_ORDERS", view_sheet_name: str = "ORDERS"):
    """
    Build ORDERS view sheet that merges RAW_ORDERS with MANUAL_OVERRIDES
    
    Uses XLOOKUP formulas to pull manual values from MANUAL_OVERRIDES
    """
    logger.info(f"Building {view_sheet_name} view from {raw_sheet_name}...")
    
    try:
        # OPTIMIZED: Get headers using cached method
        raw_sheet = manager.create_sheet_if_not_exists(raw_sheet_name)
        raw_headers, _ = manager.get_headers_cached(raw_sheet_name)
        
        if not raw_headers:
            logger.warning(f"{raw_sheet_name} has no headers, cannot build view")
            return
        
        # OPTIMIZED: Get data using batch (read only used range, not full sheet)
        # First, get row count by reading a small range
        try:
            sample_data = raw_sheet.get_values('A2:A1000')  # Sample to find last row
            num_data_rows = len([r for r in sample_data if r and r[0]]) if sample_data else 0
        except:
            num_data_rows = 0
        
        if num_data_rows == 0:
            logger.warning(f"{raw_sheet_name} is empty, cannot build view")
            return
        
        # OPTIMIZED: Read only needed columns in one batch
        # Read all data rows for key columns only
        last_row = num_data_rows + 1
        raw_data = raw_sheet.get_values(f'A2:{chr(64 + len(raw_headers))}{last_row}')
        if not raw_data:
            raw_data = []
        
        # Find key columns in RAW_ORDERS
        try:
            order_id_col_idx = raw_headers.index("Order ID")
        except ValueError:
            try:
                order_id_col_idx = raw_headers.index("order_id")
            except ValueError:
                logger.error("Order ID column not found in RAW_ORDERS")
                return
        
        # Create view sheet
        view_sheet = manager.create_sheet_if_not_exists(view_sheet_name)
        view_sheet.clear()
        
        # Build headers - start with RAW_ORDERS headers, add manual columns
        view_headers = raw_headers.copy()
        
        # Add manual columns if not present
        manual_cols = {
            'PSL': 'PSL',
            'Shipping Label Cost': 'shipping_label_cost',
            'Notes': 'notes'
        }
        
        for col_name, override_key in manual_cols.items():
            if col_name not in view_headers:
                view_headers.append(col_name)
        
        # Write headers
        view_sheet.update('A1', [view_headers])
        
        # Build formulas for each row
        num_data_rows = len(raw_data) - 1  # Exclude header
        
        if num_data_rows > 0:
            # Get column letters
            def col_letter(idx):
                return chr(64 + idx + 1) if idx < 26 else chr(64 + (idx // 26)) + chr(65 + (idx % 26))
            
            order_id_col_letter = col_letter(order_id_col_idx)
            
            # Find where to insert manual columns
            psl_col_idx = len(raw_headers)
            label_cost_col_idx = len(raw_headers) + 1
            notes_col_idx = len(raw_headers) + 2
            
            psl_col_letter = col_letter(psl_col_idx)
            label_cost_col_letter = col_letter(label_cost_col_idx)
            notes_col_letter = col_letter(notes_col_idx)
            
            # Build formulas for manual columns
            formulas = []
            for row_num in range(2, num_data_rows + 2):  # Start at row 2 (after header)
                # PSL formula: XLOOKUP(order_id, MANUAL_OVERRIDES!A:A, MANUAL_OVERRIDES!C:C, "")
                psl_formula = f'=IFERROR(XLOOKUP({order_id_col_letter}{row_num},MANUAL_OVERRIDES!A:A,MANUAL_OVERRIDES!C:C,""),"")'
                
                # Shipping Label Cost formula
                label_cost_formula = f'=IFERROR(XLOOKUP({order_id_col_letter}{row_num},MANUAL_OVERRIDES!A:A,MANUAL_OVERRIDES!D:D,0),0)'
                
                # Notes formula
                notes_formula = f'=IFERROR(XLOOKUP({order_id_col_letter}{row_num},MANUAL_OVERRIDES!A:A,MANUAL_OVERRIDES!E:E,""),"")'
                
                formulas.append([psl_formula, label_cost_formula, notes_formula])
            
            # Write formulas
            if formulas:
                formula_range = f'{psl_col_letter}2:{notes_col_letter}{num_data_rows + 1}'
                view_sheet.update(formula_range, formulas, value_input_option='USER_ENTERED')
            
            # Copy raw data (excluding manual columns if they exist in raw)
            raw_data_rows = []
            for row in raw_data[1:]:
                # Extend row to match view headers
                while len(row) < len(raw_headers):
                    row.append('')
                raw_data_rows.append(row[:len(raw_headers)])  # Only take raw columns
            
            # Write raw data
            if raw_data_rows:
                data_range = f'A2:{col_letter(len(raw_headers)-1)}{num_data_rows + 1}'
                view_sheet.update(data_range, raw_data_rows)
        
        # Update profit formulas to use shipping_label_cost from manual overrides
        _update_profit_formulas(view_sheet, view_headers, label_cost_col_idx)
        
        logger.info(f"✅ {view_sheet_name} view built successfully")
        
        # Update METRICS after building view
        try:
            from metrics_calculator import calculate_and_update_metrics
            calculate_and_update_metrics(manager)
            logger.info("✅ METRICS table updated after view build")
        except Exception as e:
            logger.warning(f"Could not update METRICS: {e}")
        
    except Exception as e:
        logger.error(f"Error building {view_sheet_name} view: {e}", exc_info=True)


def _update_profit_formulas(sheet, headers: List[str], label_cost_col_idx: int):
    """Update profit formulas to subtract shipping_label_cost from MANUAL_OVERRIDES"""
    try:
        # Find profit column
        try:
            profit_col_idx = headers.index("Profit")
        except ValueError:
            try:
                profit_col_idx = headers.index("profit")
            except ValueError:
                logger.warning("Profit column not found, skipping profit formula update")
                return
        
        # Find required columns for profit calculation
        try:
            revenue_col_idx = headers.index("Total Revenue")
        except ValueError:
            try:
                revenue_col_idx = headers.index("Sold Price")
            except ValueError:
                logger.warning("Revenue column not found")
                return
        
        try:
            unit_cost_col_idx = headers.index("Unit Cost")
        except ValueError:
            try:
                unit_cost_col_idx = headers.index("unit_cost")
            except ValueError:
                logger.warning("Unit Cost column not found")
                return
        
        try:
            quantity_col_idx = headers.index("Quantity")
        except ValueError:
            logger.warning("Quantity column not found")
            return
        
        # Get all data to find last row
        all_data = sheet.get_all_values()
        if not all_data or len(all_data) < 2:
            return
        
        last_row = len(all_data)
        
        # Build profit formula: Total Revenue - (Unit Cost * Quantity) - Shipping Label Cost
        def col_letter(idx):
            return chr(64 + idx + 1) if idx < 26 else chr(64 + (idx // 26)) + chr(65 + (idx % 26))
        
        revenue_col = col_letter(revenue_col_idx)
        unit_cost_col = col_letter(unit_cost_col_idx)
        quantity_col = col_letter(quantity_col_idx)
        label_cost_col = col_letter(label_cost_col_idx)
        profit_col = col_letter(profit_col_idx)
        
        # Update profit formulas
        formulas = []
        for row_num in range(2, last_row + 1):
            formula = f'={revenue_col}{row_num}-({unit_cost_col}{row_num}*{quantity_col}{row_num})-{label_cost_col}{row_num}'
            formulas.append([formula])
        
        if formulas:
            formula_range = f'{profit_col}2:{profit_col}{last_row}'
            sheet.update(formula_range, formulas, value_input_option='USER_ENTERED')
        
        logger.info("Updated profit formulas to include shipping_label_cost")
        
    except Exception as e:
        logger.error(f"Error updating profit formulas: {e}")


def build_fulfillment_view(manager, raw_sheet_name: str = "RAW_ORDERS", view_sheet_name: str = "FULFILLMENT"):
    """
    Build FULFILLMENT view sheet filtered to unfulfilled orders
    """
    logger.info(f"Building {view_sheet_name} view...")
    
    try:
        # Get ORDERS view (which already has manual overrides merged)
        orders_sheet = manager.create_sheet_if_not_exists("ORDERS")
        orders_data = orders_sheet.get_all_values()
        
        if not orders_data or len(orders_data) < 2:
            logger.warning("ORDERS view is empty, cannot build FULFILLMENT view")
            return
        
        headers = orders_data[0]
        
        # Find fulfillment status column
        try:
            status_col_idx = headers.index("Fulfillment Status")
        except ValueError:
            try:
                status_col_idx = headers.index("Shipping Status")
            except ValueError:
                try:
                    status_col_idx = headers.index("Order Status")
                except ValueError:
                    logger.warning("Fulfillment status column not found")
                    return
        
        # Filter to unfulfilled
        unfulfilled_rows = [headers]  # Start with header
        for row in orders_data[1:]:
            if len(row) > status_col_idx:
                status = str(row[status_col_idx]).lower()
                if 'unfulfilled' in status or status == '' or 'pending' in status or 'partial' in status:
                    unfulfilled_rows.append(row)
        
        # Create FULFILLMENT sheet
        fulfillment_sheet = manager.create_sheet_if_not_exists(view_sheet_name)
        fulfillment_sheet.clear()
        
        if unfulfilled_rows:
            fulfillment_sheet.update('A1', unfulfilled_rows)
        
        logger.info(f"✅ {view_sheet_name} view built with {len(unfulfilled_rows)-1} unfulfilled orders")
        
    except Exception as e:
        logger.error(f"Error building {view_sheet_name} view: {e}", exc_info=True)

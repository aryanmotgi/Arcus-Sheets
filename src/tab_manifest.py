"""
Tab Manifest - Defines the ONLY allowed tabs in the Arcus spreadsheet
"""
from typing import Dict, List

# The ONLY tabs that should exist in the spreadsheet
TAB_MANIFEST = {
    "visible": [
        "HOME",
        "ORDERS",
        "FINANCE",
        "METRICS",
        "CHARTS",
        "PRODUCTS",
        "COSTS",
        "SETTINGS"
    ],
    "hidden": [
        "RAW_ORDERS",
        "MANUAL_OVERRIDES"
    ]
}

# All tabs (visible + hidden)
ALL_TABS = TAB_MANIFEST["visible"] + TAB_MANIFEST["hidden"]

# Tab purposes - what each tab is for
TAB_PURPOSES = {
    "HOME": {
        "title": "HOME - Arcus Command Center",
        "purpose": "Arcus command center dashboard (read-only KPIs + quick actions)",
        "use_for": [
            "Seeing current performance + what needs action today",
            "Quick access to key metrics",
            "Navigation to other tabs"
        ],
        "dont": [
            "Edit order data here",
            "Store raw data"
        ],
        "data_source": "METRICS, FULFILLMENT (via formulas)"
    },
    "ORDERS": {
        "title": "ORDERS - Main Order View",
        "purpose": "Main order view (cleaned merged view of Shopify + manual overrides)",
        "use_for": [
            "Reviewing orders",
            "Profit per order",
            "PSL, label cost, notes",
            "Order status tracking"
        ],
        "dont": [
            "Manually type directly into synced columns",
            "Store raw Shopify data"
        ],
        "data_source": "RAW_ORDERS + MANUAL_OVERRIDES (via XLOOKUP formulas)"
    },
    "FINANCE": {
        "title": "FINANCE - Financial Breakdown",
        "purpose": "Financial breakdown and summaries (profit definitions, margins, trends)",
        "use_for": [
            "Business decisions (pricing, targets, profitability)",
            "Financial analysis",
            "Profit margin calculations"
        ],
        "dont": [
            "Store raw orders here",
            "Hardcode summary values"
        ],
        "data_source": "METRICS + ORDERS (via formulas)"
    },
    "METRICS": {
        "title": "METRICS - Single Source of Truth",
        "purpose": "Single source of truth for KPIs used everywhere",
        "use_for": [
            "Dashboard KPIs",
            "Chart references",
            "Finance calculations"
        ],
        "dont": [
            "Hardcode summary cells elsewhere",
            "Manual edits (values calculated automatically)"
        ],
        "data_source": "Formulas from ORDERS/RAW + fixed values (setup_costs)"
    },
    "CHARTS": {
        "title": "CHARTS - Visualizations",
        "purpose": "Visualization-only page",
        "use_for": [
            "Revenue/profit trends",
            "Units by product",
            "Top products analysis"
        ],
        "dont": [
            "Manual data entry",
            "Store raw data"
        ],
        "data_source": "ORDERS + METRICS (charts auto-update)"
    },
    "PRODUCTS": {
        "title": "PRODUCTS - Product Catalog",
        "purpose": "Product catalog + pricing + costs + inventory planning",
        "use_for": [
            "Setting unit costs",
            "Prices, margins",
            "Low inventory tracking"
        ],
        "dont": [
            "Mix order-level data here",
            "Store fulfillment status"
        ],
        "data_source": "Shopify products (optional) + manual inputs"
    },
    "COSTS": {
        "title": "COSTS - Setup & Operational Costs",
        "purpose": "Setup + operational cost ledger (manufacturing/supplies/samples/etc)",
        "use_for": [
            "Tracking fixed costs + ongoing expenses",
            "Feeds setup_costs metric"
        ],
        "dont": [
            "Overwrite with sync",
            "Store order-level costs"
        ],
        "data_source": "Manual entry + summaries"
    },
    "SETTINGS": {
        "title": "SETTINGS - Configuration",
        "purpose": "Configuration + Arcus theme settings",
        "use_for": [
            "Logo URL",
            "Brand colors",
            "Defaults, last_sync_at, toggles"
        ],
        "dont": [
            "Store operational data here",
            "Edit during sync"
        ],
        "data_source": "Manual config only"
    },
    "RAW_ORDERS": {
        "title": "RAW_ORDERS - Raw Synced Data (HIDDEN)",
        "purpose": "Raw synced Shopify order data (write-only)",
        "use_for": [
            "System backend source for views"
        ],
        "dont": [
            "Humans should not edit or view regularly",
            "Store manual overrides here"
        ],
        "data_source": "Shopify API (auto-synced)"
    },
    "MANUAL_OVERRIDES": {
        "title": "MANUAL_OVERRIDES - Persistent Manual Edits (HIDDEN)",
        "purpose": "Persistent manual edits per order (PSL, shipping label cost, notes)",
        "use_for": [
            "Anything user-entered that must survive sync"
        ],
        "dont": [
            "Store derived formulas here",
            "Edit synced columns"
        ],
        "data_source": "AI writes / user edits"
    }
}


def get_all_tab_names() -> List[str]:
    """Get all tab names (visible + hidden)"""
    return ALL_TABS.copy()


def get_visible_tab_names() -> List[str]:
    """Get visible tab names"""
    return TAB_MANIFEST["visible"].copy()


def get_hidden_tab_names() -> List[str]:
    """Get hidden tab names"""
    return TAB_MANIFEST["hidden"].copy()


def is_manifest_tab(tab_name: str) -> bool:
    """Check if a tab name is in the manifest"""
    return tab_name in ALL_TABS


def get_tab_purpose(tab_name: str) -> Dict:
    """Get purpose information for a tab"""
    return TAB_PURPOSES.get(tab_name, {})


def format_tab_purposes_for_display() -> str:
    """Format all tab purposes for display"""
    lines = []
    for tab_name in ALL_TABS:
        purpose = TAB_PURPOSES.get(tab_name, {})
        lines.append(f"\n**{purpose.get('title', tab_name)}**")
        lines.append(f"Purpose: {purpose.get('purpose', 'N/A')}")
        lines.append(f"Use for: {', '.join(purpose.get('use_for', []))}")
        lines.append(f"Don't: {', '.join(purpose.get('dont', []))}")
        lines.append(f"Data source: {purpose.get('data_source', 'N/A')}")
    return "\n".join(lines)

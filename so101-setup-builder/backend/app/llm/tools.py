"""Function calling tools for Gemini."""

from typing import Any

# Tool definitions for Gemini function calling
SEARCH_COMPONENTS_TOOL = {
    "name": "search_components",
    "description": "Search for components in the database by category, price, or specifications",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Component category (motors, cameras, compute, cables, power)",
            },
            "max_price": {
                "type": "number",
                "description": "Maximum price in USD",
            },
            "specifications": {
                "type": "object",
                "description": "Required specifications as key-value pairs",
            },
        },
        "required": [],
    },
}

GET_COMPONENT_DETAILS_TOOL = {
    "name": "get_component_details",
    "description": "Get detailed information about a specific component",
    "parameters": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "The component ID",
            },
        },
        "required": ["component_id"],
    },
}

CHECK_COMPATIBILITY_TOOL = {
    "name": "check_compatibility",
    "description": "Check if components are compatible with each other",
    "parameters": {
        "type": "object",
        "properties": {
            "component_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of component IDs to check",
            },
        },
        "required": ["component_ids"],
    },
}

GET_CURRENT_PRICES_TOOL = {
    "name": "get_current_prices",
    "description": "Get current prices for a component from all vendors",
    "parameters": {
        "type": "object",
        "properties": {
            "component_id": {
                "type": "integer",
                "description": "The component ID",
            },
        },
        "required": ["component_id"],
    },
}

SEARCH_WEB_PRICES_TOOL = {
    "name": "search_web_prices",
    "description": "Search the web for current prices of a component",
    "parameters": {
        "type": "object",
        "properties": {
            "component_name": {
                "type": "string",
                "description": "Name of the component to search for",
            },
            "vendor_preference": {
                "type": "string",
                "description": "Preferred vendor (aliexpress, amazon, waveshare, robotshop)",
            },
        },
        "required": ["component_name"],
    },
}

# All tools for easy access
ALL_TOOLS = [
    SEARCH_COMPONENTS_TOOL,
    GET_COMPONENT_DETAILS_TOOL,
    CHECK_COMPATIBILITY_TOOL,
    GET_CURRENT_PRICES_TOOL,
    SEARCH_WEB_PRICES_TOOL,
]


def get_tools_for_gemini() -> list[dict[str, Any]]:
    """Get tools formatted for Gemini API."""
    return [
        {
            "function_declarations": ALL_TOOLS,
        }
    ]

"""
State management helper functions for Send Money Agent

Provides utilities for:
- Country data lookup
- Field validation
- Amount calculations
- Completion checking
"""

from typing import Optional, Dict
from google.adk.tools import ToolContext


def get_country_data(country: str) -> Optional[Dict]:
    """
    Retrieve country configuration from mock data
    
    Args:
        country: Country name (case-insensitive)
    
    Returns:
        dict with country data if found, None otherwise
    """
    from .mock_data import SUPPORTED_COUNTRIES
    
    country_lower = country.lower()
    for country_config in SUPPORTED_COUNTRIES:
        if country_config['country_name'].lower() == country_lower:
            return country_config
    
    return None


def calculate_receive_amount(tool_context: ToolContext) -> None:
    """
    Calculate and update receive_amount based on send_amount and exchange_rate
    
    Updates tool_context.state['receive_amount'] in-place.
    Requires send_amount and exchange_rate to be present in state.
    """
    send_amount = tool_context.state.get('send_amount')
    exchange_rate = tool_context.state.get('exchange_rate')
    
    if send_amount and exchange_rate:
        tool_context.state['receive_amount'] = round(send_amount * exchange_rate, 2)


def all_fields_complete(state: dict) -> bool:
    """
    Check if all required fields for confirmation are collected
    
    Required fields:
    - destination_country
    - send_amount
    - beneficiary
    - delivery_method
    
    Args:
        state: The agent's state dictionary
    
    Returns:
        True if all required fields are present and truthy
    """
    required_fields = [
        'destination_country',
        'send_amount',
        'beneficiary',
        'delivery_method'
    ]
    
    return all(state.get(field) for field in required_fields)


def get_missing_fields(state: dict) -> list[str]:
    """
    Get list of required fields that are still missing.
    
    Args:
        state: Current session state dictionary
        
    Returns:
        List of missing field names
    """
    required_fields = [
        'destination_country',
        'send_amount',
        'beneficiary',
        'delivery_method'
    ]
    return [field for field in required_fields if not state.get(field)]

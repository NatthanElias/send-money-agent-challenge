"""
ADK Tools for the Send Money Bot.
4 focused tools with single responsibilities.
"""

import uuid
from typing import Optional
from google.adk.tools import ToolContext

from .mock_data import get_supported_country_names
from .transfer_state import get_country_data, calculate_receive_amount


def set_destination(country: str, tool_context: ToolContext) -> dict:
    """
    Set destination country and load its configuration
    
    Updates state with:
    - destination_country
    - destination_currency_code
    - exchange_rate
    - available_methods
    
    Also recalculates receive_amount if send_amount exists.
    
    Args:
        country: Destination country name
        tool_context: ToolContext with access to state
        
    Returns:
        Success dict with country config, or error dict if invalid
    """
    country_data = get_country_data(country)
    
    if not country_data:
        supported = get_supported_country_names()
        return {
            "success": False,
            "error": f"Country '{country}' not supported",
            "supported_countries": supported
        }
    
    # Update state with country information
    tool_context.state['destination_country'] = country_data['country_name']
    tool_context.state['destination_currency_code'] = country_data['currency_code']
    tool_context.state['exchange_rate'] = country_data['exchange_rate']
    tool_context.state['available_methods'] = country_data['delivery_methods']
    
    # If method was previously set but not available in new country, clear it
    current_method = tool_context.state.get('delivery_method')
    if current_method and current_method not in country_data['delivery_methods']:
        tool_context.state['delivery_method'] = None
    
    # Recalculate receive_amount if send_amount already exists
    if tool_context.state.get('send_amount'):
        calculate_receive_amount(tool_context)
    
    # Tool does NOT check completion or set stage - callback handles that
    return {
        "success": True,
        "country": country_data['country_name'],
        "currency_code": country_data['currency_code'],
        "exchange_rate": country_data['exchange_rate'],
        "available_methods": country_data['delivery_methods']
    }


def set_amount(amount: float, tool_context: ToolContext) -> dict:
    """
    Set the amount to send and calculate receive amount.
    
    Updates state with:
    - send_amount
    - receive_amount (calculated if country/rate available)
    
    Args:
        amount: USD amount to send (must be positive)
        tool_context: ToolContext with access to state
        
    Returns:
        Success dict with amount details, or error dict if invalid
    """
    if amount <= 0:
        return {
            "success": False,
            "error": "Amount must be greater than 0"
        }
    
    tool_context.state['send_amount'] = amount
    
    # Calculate receive_amount if we have exchange rate
    if tool_context.state.get('exchange_rate'):
        calculate_receive_amount(tool_context)
        return {
            "success": True,
            "send_amount": amount,
            "receive_amount": tool_context.state['receive_amount'],
            "currency_code": tool_context.state.get('destination_currency_code')
        }
    
    # Tool does NOT check completion or set stage
    return {
        "success": True,
        "send_amount": amount,
        "receive_amount": None,
        "currency_code": None
    }


def set_transfer_details(
    tool_context: ToolContext,
    beneficiary: Optional[str] = None,
    delivery_method: Optional[str] = None
) -> dict:
    """
    Set beneficiary name and/or delivery method.
    
    Both parameters are optional - can be called to set either or both.
    Validates delivery_method against available methods if country is set.
    
    Args:
        tool_context: ToolContext with access to state
        beneficiary: Recipient's full name (optional)
        delivery_method: Delivery method choice (optional)
        
    Returns:
        Success dict with updated details, or error dict if method invalid
    """
    updates = {}
    
    if beneficiary:
        tool_context.state['beneficiary'] = beneficiary
        updates['beneficiary'] = beneficiary
    
    if delivery_method:
        # Validate method if country is already set
        available_methods = tool_context.state.get('available_methods', [])
        if available_methods and delivery_method not in available_methods:
            return {
                "success": False,
                "error": f"Method '{delivery_method}' not available",
                "available_methods": available_methods
            }
        tool_context.state['delivery_method'] = delivery_method
        updates['delivery_method'] = delivery_method
    
    # Tool does NOT check completion or set stage
    return {
        "success": True,
        **updates
    }


def confirm_transfer(confirmed: bool, tool_context: ToolContext) -> dict:
    """
    Finalize or restart the transfer flow.
    
    Args:
        confirmed: True to complete transfer, False to restart/modify
        tool_context: ToolContext with access to state
        
    Returns:
        Success dict with transaction ID if confirmed, or restart message
    """
    if confirmed:
        # Generate transaction ID and complete
        transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        
        tool_context.state['stage'] = 'completed'
        tool_context.state['transaction_id'] = transaction_id
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "message": f"Transfer confirmed! Transaction ID: {transaction_id}"
        }
    else:
        # User wants to make changes - go back to collecting
        tool_context.state['stage'] = 'collecting'
        return {
            "success": True,
            "message": "No problem! What would you like to change?"
        }

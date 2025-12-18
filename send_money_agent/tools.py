import uuid
from typing import Optional
from google.adk.tools import ToolContext

from .mock_data import get_supported_country_names, get_country_data
from .helpers import (
    calculate_receive_amount,
    clear_validation_state,
    validate_amount,
    check_beneficiary_clarification
)


def set_destination(country: str, tool_context: ToolContext) -> dict:
    """
    Set destination country and load its configuration.
    
    Validates country is supported and updates state with country config.
    """
    # Clear previous validation state
    clear_validation_state(tool_context)
    
    country_data = get_country_data(country)
    
    if not country_data:
        supported = get_supported_country_names()
        tool_context.state['validation_errors'] = f"Country '{country}' is not supported. We currently support: {', '.join(supported)}."
        return {
            "success": False,
            "error": "country_not_supported",
            "message": f"Country '{country}' is not supported",
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
        tool_context.state['delivery_method'] = ""
    
    # Recalculate receive_amount if send_amount already exists
    if tool_context.state.get('send_amount'):
        calculate_receive_amount(tool_context)
    
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
    
    Validates amount is positive and within limits.
    """
    # Clear previous validation state
    clear_validation_state(tool_context)
    
    # Validate amount
    is_valid, error_message = validate_amount(amount)
    if not is_valid:
        tool_context.state['validation_errors'] = error_message
        return {
            "success": False,
            "error": "invalid_amount",
            "message": error_message
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
    
    Validates delivery method and checks beneficiary for clarification needs.
    """
    # Clear previous validation state
    clear_validation_state(tool_context)
    
    updates = {}
    
    if beneficiary:
        tool_context.state['beneficiary'] = beneficiary
        updates['beneficiary'] = beneficiary
        
        # Check if beneficiary needs clarification (soft flag, doesn't block)
        clarification_needed, clarification_reason = check_beneficiary_clarification(beneficiary)
        if clarification_needed:
            tool_context.state['clarification_needed'] = clarification_needed
            tool_context.state['clarification_reason'] = clarification_reason
    
    if delivery_method:
        # Validate method against available methods
        available_methods = tool_context.state.get('available_methods', [])
        if available_methods and delivery_method not in available_methods:
            tool_context.state['validation_errors'] = f"'{delivery_method}' is not available for {tool_context.state.get('destination_country', 'this country')}. Available methods: {', '.join(available_methods)}."
            return {
                "success": False,
                "error": "invalid_method_for_country",
                "message": f"Method '{delivery_method}' not available",
                "available_methods": available_methods
            }
        tool_context.state['delivery_method'] = delivery_method
        updates['delivery_method'] = delivery_method
    
    return {
        "success": True,
        **updates
    }


def confirm_transfer(confirmed: bool, tool_context: ToolContext) -> dict:
    """
    Finalize or restart the transfer flow.
    
    Blocks confirmation if there are validation errors.
    """
    # Check for blocking errors before confirming
    if confirmed and tool_context.state.get('validation_errors'):
        return {
            "success": False,
            "error": "cannot_confirm_with_errors",
            "message": "Cannot confirm transfer while there are validation errors. Please fix the errors first."
        }
    
    if confirmed:
        # Generate transaction ID and complete
        transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        
        tool_context.state['stage'] = 'completed'
        tool_context.state['transaction_id'] = transaction_id
        
        # Clear validation state on success
        clear_validation_state(tool_context)
        
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

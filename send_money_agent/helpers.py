from google.adk.tools import ToolContext

# Constants for validation
MAX_TRANSFER_AMOUNT = 10000
PLACEHOLDER_NAMES = {"me", "myself", "test", "friend", "self", "user", "nobody", "someone"}


def get_initial_state(country_data: dict = None) -> dict:
    """
    Generate initial state for a new session.
    
    Args:
        country_data: Optional dict with country config. If None, returns empty defaults.
        
    Returns:
        Dict with all state keys initialized.
    """
    if country_data:
        return {
            # Pre-populated with country defaults
            "destination_country": country_data['country_name'],
            "destination_currency_code": country_data['currency_code'],
            "exchange_rate": country_data['exchange_rate'],
            "available_methods": country_data['delivery_methods'],
            # Empty user inputs
            "send_amount": "",
            "receive_amount": "",
            "beneficiary": "",
            "delivery_method": "",
            "transaction_id": "",
            # Control state
            "stage": "initial",
            # Validation state
            "validation_errors": "",
            "clarification_needed": "",
            "clarification_reason": ""
        }
    else:
        # Empty template for reset
        return {
            "destination_country": "",
            "destination_currency_code": "",
            "exchange_rate": "",
            "available_methods": [],
            "send_amount": "",
            "receive_amount": "",
            "beneficiary": "",
            "delivery_method": "",
            "transaction_id": "",
            "stage": "initial",
            "validation_errors": "",
            "clarification_needed": "",
            "clarification_reason": ""
        }


def clear_validation_state(tool_context: ToolContext) -> None:
    """Clear validation errors and clarification flags before re-evaluating."""
    tool_context.state['validation_errors'] = ""
    tool_context.state['clarification_needed'] = ""
    tool_context.state['clarification_reason'] = ""


def calculate_receive_amount(tool_context: ToolContext) -> None:
    """Calculate and update receive_amount based on send_amount and exchange_rate."""
    send_amount = tool_context.state.get('send_amount')
    exchange_rate = tool_context.state.get('exchange_rate')
    
    if send_amount and exchange_rate:
        tool_context.state['receive_amount'] = round(send_amount * exchange_rate, 2)


def validate_amount(amount: float) -> tuple[bool, str]:
    """Validate transfer amount."""
    if amount <= 0:
        return False, "Amount must be greater than $0"
    if amount > MAX_TRANSFER_AMOUNT:
        return False, f"Amount exceeds the maximum limit of ${MAX_TRANSFER_AMOUNT:,}. Please reduce the amount."
    return True, ""


def check_beneficiary_clarification(name: str) -> tuple[str, str]:
    """Check if beneficiary name needs clarification."""
    if not name:
        return "", ""
    
    name_lower = name.strip().lower()
    
    if name_lower in PLACEHOLDER_NAMES:
        return "beneficiary", "is_placeholder"
    
    words = name.strip().split()
    if len(words) < 2:
        return "beneficiary", "needs_full_name"
    
    return "", ""


def all_fields_complete(state: dict) -> bool:
    """Check if all required fields are collected and no validation errors."""
    required_fields = ['destination_country', 'send_amount', 'beneficiary', 'delivery_method']
    fields_present = all(state.get(field) for field in required_fields)
    no_errors = not state.get('validation_errors')
    return fields_present and no_errors


def get_missing_fields(state: dict) -> list[str]:
    """Get list of required fields that are still missing."""
    required_fields = ['destination_country', 'send_amount', 'beneficiary', 'delivery_method']
    return [field for field in required_fields if not state.get(field)]

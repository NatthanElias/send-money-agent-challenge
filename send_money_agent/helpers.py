from google.adk.tools import ToolContext

# Constants for validation
MAX_TRANSFER_AMOUNT = 10000
PLACEHOLDER_NAMES = {"me", "myself", "test", "friend", "self", "user", "nobody", "someone"}


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
    """
    Validate transfer amount.
    
    Returns:
        (is_valid, error_message)
    """
    if amount <= 0:
        return False, "Amount must be greater than $0"
    if amount > MAX_TRANSFER_AMOUNT:
        return False, f"Amount exceeds the maximum limit of ${MAX_TRANSFER_AMOUNT:,}. Please reduce the amount."
    return True, ""


def check_beneficiary_clarification(name: str) -> tuple[str, str]:
    """
    Check if beneficiary name needs clarification.
    
    Returns:
        (clarification_needed, clarification_reason)
        Empty strings if no clarification needed.
    """
    if not name:
        return "", ""
    
    name_lower = name.strip().lower()
    
    # Check for placeholder names (e.g., "me", "myself", "test")
    if name_lower in PLACEHOLDER_NAMES:
        return "beneficiary", "is_placeholder"
    
    # Check for single-word names (need full legal name)
    words = name.strip().split()
    if len(words) < 2:
        return "beneficiary", "needs_full_name"
    
    return "", ""


def all_fields_complete(state: dict) -> bool:
    """
    Check if all required fields for confirmation are collected.
    Also checks that there are no validation errors.
    """
    required_fields = [
        'destination_country',
        'send_amount',
        'beneficiary',
        'delivery_method'
    ]
    
    # All fields must be present
    fields_present = all(state.get(field) for field in required_fields)
    
    # No blocking validation errors
    no_errors = not state.get('validation_errors')
    
    return fields_present and no_errors


def get_missing_fields(state: dict) -> list[str]:
    """Get list of required fields that are still missing."""
    required_fields = [
        'destination_country',
        'send_amount',
        'beneficiary',
        'delivery_method'
    ]
    return [field for field in required_fields if not state.get(field)]

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext, BaseTool
from google.genai import types
from typing import Optional, Any

from .tools import (
    set_destination,
    set_amount,
    set_transfer_details,
    confirm_transfer
)
from .prompts.prompt_v2 import get_system_instruction
from .helpers import all_fields_complete, get_missing_fields
from .mock_data import get_country_data


# Get default country data for initialization
_default_country = get_country_data("Brazil")

# Default initial state
INITIAL_STATE = {
    # Required fields
    "destination_country": _default_country['country_name'],
    "destination_currency_code": _default_country['currency_code'],
    "exchange_rate": _default_country['exchange_rate'],
    "send_amount": "",
    "beneficiary": "",
    "delivery_method": "",
    # Calculated fields
    "receive_amount": "",
    "transaction_id": "",
    # Control state flow
    "available_methods": _default_country['delivery_methods'],
    "stage": "collecting",
    # Validation and clarification state
    "validation_errors": "",
    "clarification_needed": "",
    "clarification_reason": ""
}


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Initialize state before agent runs."""
    for key, default_value in INITIAL_STATE.items():
        if key not in callback_context.state:
            callback_context.state[key] = default_value
    return None


def after_tool_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: Any
) -> Optional[dict]:
    """
    Centralized stage management callback.
    
    Advances from 'collecting' → 'confirming' when all fields complete
    and there are no validation errors.
    """
    current_stage = tool_context.state.get('stage', 'collecting')
    
    # Only check for advancement if we're in collecting stage
    if current_stage == 'collecting':
        # Don't advance if there are validation errors
        if tool_context.state.get('validation_errors'):
            print(f"[Callback] Blocked by validation errors")
            return None
            
        if all_fields_complete(tool_context.state):
            tool_context.state['stage'] = 'confirming'
            print(f"[Callback] Stage advanced: collecting → confirming")
        else:
            missing = get_missing_fields(tool_context.state)
            print(f"[Callback] Still collecting. Missing: {missing}")
    
    return None


# Create the agent with callbacks attached
root_agent = LlmAgent(
    name="send_money_bot",
    model="gemini-2.0-flash",
    instruction=get_system_instruction(),
    description="Helps users send money internationally by collecting transfer details",
    tools=[
        set_destination,
        set_amount,
        set_transfer_details,
        confirm_transfer
    ],
    before_agent_callback=before_agent_callback,
    after_tool_callback=after_tool_callback
)

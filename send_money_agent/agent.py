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
from .prompts.prompt_v1 import get_system_instruction
from .helpers import all_fields_complete, get_missing_fields


# Default initial state
INITIAL_STATE = {
    "destination_country": "Brazil",
    "destination_currency_code": "BRL",
    "exchange_rate": 5.36,
    "send_amount": "",
    "receive_amount": "",
    "beneficiary": "",
    "delivery_method": "",
    "available_methods": ["Pix", "Bank Transfer"],
    "stage": "collecting",
    "transaction_id": ""
}


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Initialize state before agent runs.

    Args:
        callback_context: CallbackContext with access to agent state
        
    Returns:
        None to proceed with agent execution
    """
    # Initialize any missing state keys with defaults
    for key, default_value in INITIAL_STATE.items():
        if key not in callback_context.state:
            callback_context.state[key] = default_value
    
    # Return None to proceed with normal agent execution
    return None


def after_tool_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
    tool_response: Any
) -> Optional[dict]:
    """
    Centralized stage management callback.
    
    Runs after ANY tool completes. Checks if all required fields are
    collected and automatically advances from 'collecting' → 'confirming'.
    
    Args:
        tool: The tool that was executed
        args: Arguments passed to the tool
        tool_context: ToolContext with access to state
        tool_response: The response from the tool
    
    Returns:
        None: Use original tool_response unchanged
    """
    current_stage = tool_context.state.get('stage', 'collecting')
    
    # Only check for advancement if we're in collecting stage
    if current_stage == 'collecting':
        if all_fields_complete(tool_context.state):
            # All required fields are present - advance to confirmation
            tool_context.state['stage'] = 'confirming'
            print(f"[Callback] Stage advanced: collecting → confirming")
        else:
            # Still collecting - log what's missing for debugging
            missing = get_missing_fields(tool_context.state)
            print(f"[Callback] Still collecting. Missing: {missing}")
    
    # Return None to use the original tool_response unchanged
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

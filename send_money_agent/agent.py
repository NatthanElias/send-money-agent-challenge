from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext, BaseTool
from google.genai import types
from typing import Optional, Any

from .tools import (
    set_destination,
    set_amount,
    set_transfer_details,
    confirm_transfer,
    calculate_usd_from_target,
    cancel_transfer_session
)
from .prompts.prompt_v3 import get_system_instruction
from .helpers import all_fields_complete, get_missing_fields, get_initial_state
from .mock_data import get_country_data


# Generate initial state with Brazil defaults
INITIAL_STATE = get_initial_state(get_country_data("Brazil"))


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
    current_stage = tool_context.state.get('stage', 'initial')
    
    if current_stage == 'collecting':
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


root_agent = LlmAgent(
    name="send_money_bot",
    model="gemini-2.0-flash",
    instruction=get_system_instruction(),
    description="Helps users send money internationally by collecting transfer details",
    tools=[
        set_destination,
        set_amount,
        set_transfer_details,
        confirm_transfer,
        calculate_usd_from_target,
        cancel_transfer_session
    ],
    before_agent_callback=before_agent_callback,
    after_tool_callback=after_tool_callback
)

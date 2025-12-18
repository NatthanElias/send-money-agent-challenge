# Send Money Agent - Google ADK Challenge

A conversational AI agent built with Google ADK that guides users through international money transfers in a natural, human-like manner.

## 🎯 Overview

This agent handles the complete money transfer flow, from initial user intent ("I want to send money") to final confirmation, managing state transitions, validations, and conversational clarifications seamlessly.

**Key Features:**
- ✅ Natural conversation flow with out-of-order input handling
- ✅ Comprehensive validation (amount limits, country support, delivery methods)
- ✅ Smart clarification for ambiguous inputs (e.g., single-word names, placeholders)
- ✅ Reverse calculation support (specify target amount → calculates USD needed)
- ✅ Exit intent handling with session reset
- ✅ Multi-stage state management (`initial` → `collecting` → `confirming` → `completed`)

## 🏗️ Architecture

```
LlmAgent (root_agent)
    ├── Tools (6 total)
    │   ├── set_destination()          # Country selection & config
    │   ├── set_amount()                # USD amount (forward calc)
    │   ├── calculate_usd_from_target() # Reverse calculation
    │   ├── set_transfer_details()      # Beneficiary + delivery method
    │   ├── confirm_transfer()          # Finalize or restart
    │   └── cancel_transfer_session()   # Exit & reset
    │
    ├── Callbacks
        ├── before_agent_callback       # State initialization
        └── after_tool_callback         # Stage advancement logic

```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Key

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key
3. Copy `.env.example` to `.env`:
   ```bash
   cp send_money_agent/.env.example send_money_agent/.env
   ```
4. Add your key to `send_money_agent/.env`:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=0
   GOOGLE_API_KEY=your_key_here
   ```

### 3. Run the Agent

**Web UI Mode (recommended):**
```bash
adk web --port 8002
```
Access http://127.0.0.1:8002

**CLI Mode:**
```bash
adk run send_money_agent
```

## 💬 Example Interactions

### Happy Path
```
User:  I want to send $100 to Maria Lopes via Pix in Brazil
Agent: Got it, that's 536 BRL. Here's your summary:
       • Country: Brazil
       • Amount: 100 USD
       • Recipient: Maria Lopes
       • Delivery Method: Pix
       • Receive Amount: 536.0 BRL
       Ready to send?
User:  Yes
Agent: All set! Your transaction ID is TXN-A3F2B8C1.
```

### Reverse Calculation
```
User:  I want Maria to receive 500 Reais in Brazil
Agent: To send 500 BRL to Brazil, you need to send $93.28 USD. Who should receive this transfer?
User:  Maria Gonzalez
Agent: Okay! Which delivery method would you prefer: Pix or Bank Transfer?
```

### Clarification Flow
```
User:  Send $50 to me
Agent: I see you'd like to send money to yourself! To process this, I'll need your full legal name as it appears on your ID.
User:  John Marcus Silva
Agent: Perfect! Which delivery method: Pix or Bank Transfer?
```

### Out-of-Order Input
```
User:  I want to use Pix
Agent: Okay! To use Pix, who should receive the money?
User:  Amount is 200
Agent: Got it, that's 1072 BRL. And who is the beneficiary?
User:  Juan Perez
Agent: Here's your summary... Ready to send?
```

## ⚙️ Configuration

### Supported Countries
- **Brazil** 🇧🇷: Pix, Bank Transfer (BRL)
- **Mexico** 🇲🇽: SPEI, Cash Pickup, Bank Transfer (MXN)
- **Argentina** 🇦🇷: Bank Transfer, Cash Pickup (ARS)

### Validation Rules
- **Amount Range:** $0.01 - $10,000 USD
- **Beneficiary:** Full legal name required (2+ words)
- **Delivery Method:** Must match country's available methods

### Models Used
- **Gemini 2.0 Flash** (default)
- Configurable in `agent.py` line 63

## 🔧 Troubleshooting

**API key not found:**
- Check `send_money_agent/.env` contains `GOOGLE_API_KEY`
- Ensure `GOOGLE_GENAI_USE_VERTEXAI=0` (for AI Studio API)

**Error 503 (Service Overloaded):**
- Gemini API temporarily unavailable, retry in a few moments

## 📚 References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Gemini API](https://ai.google.dev/api)

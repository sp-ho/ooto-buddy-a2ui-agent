"""FastAPI A2A / A2UI Server for OOTO-Buddy"""

import os
import uuid
from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ooto_template import COMPOSITE_CATALOG_ID, get_ooto_a2ui_payload

app = FastAPI(title="OOTO-Buddu A2UI Agent")

PORT = int(os.environ.get("PORT", 8080))
SERVICE_URL = os.environ.get("AGENT_URL", "http://localhost:8080")


@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """Return the A2A AgentCard with A2UI v0.9 extension declared."""
    return {
        "protocolVersion": "0.3.0",
        "name": "OOTO-Buddy",
        "description": (
            "Smart Out-of-Office and coverage planner assistant with interactive"
            " A2UI forms."
        ),
        "url": SERVICE_URL,
        "version": "1.0.0",
        "capabilities": {
            "streaming": False,
            "preferredTransport": "JSONRPC",
            "extensions": [{
                "uri": "https://a2ui.org/a2a-extension/a2ui/v0.9",
                "description": "Ability to render A2UI v0.9 surfaces",
                "required": False,
                "params": {"supportedCatalogIds": [COMPOSITE_CATALOG_ID]},
            }],
        },
        "skills": [{
            "id": "ooto_planner",
            "name": "Out of Office Setup",
            "description": (
                "Configure Out-of-Office dates, coverage contacts, and message"
                " auto-responders."
            ),
        }],
        "defaultInputModes": ["text/plain", "application/json+a2ui"],
        "defaultOutputModes": ["text/plain", "application/json+a2ui"],
    }

@app.post("/")
async def handle_a2a_rpc(request: Request):
    body: Dict[str, Any] = await request.json()
    rpc_id = body.get("id", 1)
    params = body.get("params", {})
    message = params.get("message", {})
    parts = message.get("parts", [])

    context_id = message.get("contextId", "default-context")
    incoming_msg_id = message.get("messageId", str(uuid.uuid4()))
    response_msg_id = f"resp-{incoming_msg_id}"

    # 1. Detect if this turn is an interactive button action
    user_action = None
    action_surface_id = None
    for part in parts:
        data_payload = part.get("data")
        if isinstance(data_payload, dict):
            if "userAction" in data_payload:
                user_action = data_payload["userAction"]
            elif "action" in data_payload:
                user_action = data_payload["action"]

    if user_action:
        # Button action: preserve the surface that originated the event
        action_surface_id = user_action.get("surfaceId")

    # If it's a button click, update the existing surface;
    # If it's a new user prompt, generate a brand-new surfaceId for the new turn
    action_surface_id = (
        action_surface_id or f"ooto_surface_{incoming_msg_id[ :8]}"
    )

    # Default form values
    is_confirmed = False
    start_date = "2026-12-14"
    end_date = "2026-12-23" 
    contact = "sarah_jenkins"
    draft_text = (
        "Hi, I am currently out of office with no access to email. "
        "For urgent matters, please contact Sarah Jenkins (sarahj@example.com)."
    )
    reply_text = (
        "Here is your Out-of-Office & Coverage workspace. Adjust your dates and"
        " coverage contact below:"
    )

    # 2. Process action events
    if user_action:
        event_name = user_action.get("name")
        event_ctx = user_action.get("context", {})

        start_date = event_ctx.get("startDate", start_date)
        end_date = event_ctx.get("endDate", end_date)
        contact = event_ctx.get("coverageContact", contact)
        draft_text = event_ctx.get("draftMessage", draft_text)

        if event_name == "regenerate_draft":
            contact_label = "Sarah Jenkins" if contact == "sarah_jenkins" else contact
            draft_text = (
                "Greetings! I am away on vacation. During my absence, "
                f"{contact_label} is covering all critical escalations. Thanks!"
            )
            reply_text = (
                "I've regenarted your auto-reply draft with a more casual tone."
            )

        elif event_name == "submit_ooo":
            is_confirmed = True
            reply_text = (
                "✅ Your Out-of-Office plan has been confirmed and activated across"
                " your workspace!"
            )

    # 3. Build A2UI messages with the resolved active_surface_id
    a2ui_messages = get_ooto_a2ui_payload(
        surface_id=action_surface_id,
        start_date=start_date,
        end_date=end_date,
        contact=contact,
        draft_msg=draft_text,
        is_confirmed=is_confirmed,
    )

    # 4. Return separate DataParts
    response_parts = [{"kind": "text", "text": reply_text}]
    for a2ui_msg in a2ui_messages:
        response_parts.append({
            "kind": "data",
            "data": a2ui_msg,
            "metadata": {"mimeType": "application/json+a2ui"},
        })

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {
            "kind": "message",
            "messageId": response_msg_id,
            "contextId": context_id,
            "role": "agent",
            "parts": response_parts,
        },
    })

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
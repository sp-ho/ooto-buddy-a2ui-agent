"""A2UI v0.9 Declarative Template for OOTO-Buddy."""

COMPOSITE_CATALOG_ID = (
    "https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json"
)

def get_ooto_a2ui_payload(
        surface_id: str = "ooto_planner_surface",
        start_date: str = "2026-12-14",
        end_date: str = "2026-12-23",
        contact: str = "sarah_jenkins",
        draft_msg: str = (
            "Hi, I am currently out of office with no access to email. "
            "For urgent escalations, please contact Sarah Jenkins"
            " (sarahj@example.com)."
        ),
        is_confirmed: bool = False,
        is_update: bool = False,
) -> list[dict]:
    """Builds A2UI v0.9 sequence. Omits createSurface if updating an existing surface."""

    contact_display_names = {
        "sarah_jenkins": "Sarah Jenkins (Staff Eng Lead)",
        "dave_miller": "Dave Miller (Lead Product Manager)",
        "elena_rostova": "Elena Rostova (Engineering Manager)",
    }
    contact_name = contact_display_names.get(contact, contact)

    # 1. Choose components depending on confirmation state
    if is_confirmed:
        components = [
            {
                "id": "root",
                "component": "MaterialCard",
                "appearance": "outlined",
                "children": ["confirmation_column"],
            },
            {
                "id": "confirmation_column",
                "component": "MaterialColumn",
                "justify": "start",
                "align": "stretch",
                "style": {"gap": "12px", "padding": "16px"},
                "children": [
                    "confirm_header",
                    "confirm_dates",
                    "confirm_contact",
                    "confirm_msg_label",
                    "confirm_msg_body",
                ],
            },
            {
                "id": "confirm_header",
                "component": "MaterialText",
                "text": "✅ Out-of-Office Scheduled & Active",
                "usageHint": "h2",
            },
            {
                "id": "confirm_dates",
                "component": "MaterialText",
                "text": f"📆 **Dates:** {start_date} to {end_date}",
                "usageHint": "body1",
            },
            {
                "id": "confirm_contact",
                "component": "MaterialText",
                "text": f"👤 **Coverage Contact:** {contact_name}",
                "usageHint": "body1",
            },
            {
                "id": "confirm_msg_label",
                "component": "MaterialText",
                "text": "📝 **Auto-Responder Draft:**",
                "usageHint": "subtitle2",
            },
            {
                "id": "confirm_msg_body",
                "component": "MaterialText",
                "text": f"> {draft_msg}",
                "usageHint": "body2",
            },
        ]
    else:
        # Render the interactive planner form
        components = [
            {
                "id": "root",
                "component": "MaterialCard",
                "appearance": "outlined",
                "children": ["main_column"],
            },
            {
                "id": "main_column",
                "component": "MaterialColumn",
                "justify": "start",
                "align": "stretch",
                "style":  {"gap": "16px", "padding": "16px"},
                "children": [
                    "header_text",
                    "dates_rows",
                    "contact_select",
                    "channels_row",
                    "draft_label",
                    "draft_input",
                    "actions_row",
                ],
            },
            {
                "id": "header_text",
                "component": "MaterialText",
                "text": "📆 Out-of_office & Coverage Planner",
                "usageHint": "h2",
            },
            {
                "id": "dates_rows",
                "component": "MaterialRow",
                "justify": "spaceBetween",
                "align": "start",
                "style":  {"gap": "12px"},
                "children": [
                    "start_date_picker",
                    "end_date_picker",
                ],
            },
            {
                "id": "start_date_picker",
                "component": "MaterialDatepicker",
                "label": "Start Date",
                "placeholder": "YYYY-MM-DD",
                "value":  {"path": "/form/startDate"},
                "weight": 1,
            },
            {
                "id": "end_date_picker",
                "component": "MaterialDatepicker",
                "label": "End Date",
                "placeholder": "YYYY-MM-DD",
                "value":  {"path": "/form/endDate"},
                "weight": 1,
            },
            {
                "id": "contact_select",
                "component": "MaterialSelect",
                "label": "Primary Converage Contact",
                "placeholder": "Select colleague...",
                "value":  {"path": "/form/coverageContact"},
                "options": [
                    {
                        "label": "Sarah Jenkins (Staff Eng Lead)",
                        "value": "sarah_jenkins",
                    },
                    {
                        "label": "Dave Miller (Lead Product Manager)",
                        "value": "dave_miller",
                    },
                    {
                        "label": "Elena Rostova (Engineering Manager)",
                        "value": "elena_rostova",
                    },
                ],
            },
            {
                "id": "channels_row",
                "component": "MaterialRow",
                "justify": "start",
                "align": "center",
                "style":  {"gap": "16px"},
                "children": [
                    "gmail_checkbox",
                    "chat_checkbox",
                ],
            },
            {
                "id": "gmail_checkbox",
                "component": "MaterialCheckbox",
                "label": "Gmail Auto-Responder",
                "checked": {"path": "/form/enableGmail"},
                "color":  "primary",
            },
            {
                "id": "chat_checkbox",
                "component": "MaterialCheckbox",
                "label": "Google Chat Status",
                "checked": {"path": "/form/enableChat"},
                "color":  "primary",
            },
            {
                "id": "draft_label",
                "component": "MaterialText",
                "text": "Out-of-Office Response Preview:",
                "usageHint": "subtitle2",
            },
            {
                "id": "draft_input",
                "component": "MaterialInput",
                "text": "Auto-response Body",
                "value": {"path": "/form/draftMessage"},
                "type": "text",
            },
            {
                "id": "actions_row",
                "component": "MaterialRow",
                "justify": "spaceBetween",
                "align": "center",
                "children": [
                    "btn_regenerate",
                    "btn_confirm",
                ],
            },
            {
                "id": "btn_regenerate",
                "component": "MaterialButton",
                "label": "Regenerate Draft",
                "variant": "stroked",
                "action": {
                    "event": {
                        "name": "regenerate_draft",
                        "context": {
                            "coverageContact": {"path": "/form/coverageContact"}
                        },
                    }
                },
            },
             {
                "id": "btn_confirm",
                "component": "MaterialButton",
                "label": "Confirm & Activate OOO",
                "variant": "raised",
                "appearance": "filled",
                "action": {
                    "event": {
                        "name": "submit_ooo",
                        "context": {
                            "startDate": {"path": "/form/startDate"},
                            "endDate": {"path": "/form/endDate"},
                            "coverageContact": {"path": "/form/coverageContact"},
                            "draftMessage": {"path": "/form/draftMessage"},
                        },
                    }
                },
            },
        ]

    messages = []

    # 2. Only prepend createSurface if this is a brand-new surface
    if not is_update:
        messages.append({
            "version": "v0.9",
            "createSurface": {
                "surfaceId": surface_id,
                "catalogId": COMPOSITE_CATALOG_ID,
            },
        })

    # 3. Always send updateComponents and updateDataModel
    messages.extend([
        {
            "version": "v0.9",
            "updateComponents": {
                "surfaceId": surface_id,
                "components": components,
            },
        },
        {
            "version": "v0.9",
            "updateDataModel": {
                "surfaceId": surface_id,
                "path": "/",
                "value": {
                    "form": {
                        "startDate": start_date,
                        "endDate": end_date,
                        "coverageContact": contact,
                        "enableGmail": True,
                        "enableChat": True,
                        "draftMessage": draft_msg,
                    },
                    "isConfirmed": is_confirmed,
                },
            },
        }
    ])
    
    return messages
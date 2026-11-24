# OOTO-Buddy — A2UI Custom Agent

OOTO-Buddy is a lightweight **FastAPI A2A agent** that serves an interactive **A2UI v0.9 Out-of-Office (OOO) and coverage-planning form**. It is designed to run on Google Cloud Run and to be registered as a custom A2A agent in a Google Cloud Gemini Enterprise app.

The agent returns an A2A Agent Card and responds to JSON-RPC requests with text plus A2UI data parts. The A2UI surface lets a user review OOO dates, choose a coverage contact, edit an auto-reply draft, regenerate the draft, and submit a confirmation view.

> **Important:** This is a demonstration/prototype. The current code renders a confirmation state; it does not actually configure Gmail auto-replies, Google Chat status, calendar events, or notify the coverage contact.

## Features

- A2A Agent Card at `/.well-known/agent-card.json`
- A2A JSON-RPC message handling at `/`
- A2UI v0.9 surface using the Gemini Enterprise composite catalog
- Interactive form fields:
  - OOO start and end dates
  - Coverage contact
  - Gmail auto-responder and Google Chat status checkboxes
  - Editable auto-response draft
- Button actions:
  - **Regenerate Draft** — returns a revised sample message
  - **Confirm & Activate OOO** — displays a confirmation surface
- Cloud Run-compatible server, using the `PORT` environment variable

## Project structure

```text
.
├── main.py             # FastAPI app, A2A Agent Card and JSON-RPC handler
├── ooto_template.py    # A2UI v0.9 component and data-model payload
├── Dockerfile          # Container image definition
├── requirements.txt     # Python dependencies
└── README.md            # This documentation
```

Make sure the template filename is exactly **`ooto_template.py`**. The import in `main.py` uses that spelling.

## Architecture

```text
User
  │
  ▼
Gemini Enterprise app
  │  A2A / JSON-RPC request
  ▼
Cloud Run service
  ├── GET /.well-known/agent-card.json
  │      └── Advertises the agent and A2UI v0.9 extension
  │
  └── POST /
         ├── Reads the incoming A2A message and action data
         ├── Resolves the active A2UI surface ID
         ├── Processes regenerate_draft or submit_ooo
         ├── Calls get_ooto_a2ui_payload(...)
         └── Returns text + application/json+a2ui data parts
                  │
                  ▼
          Gemini Enterprise renders the A2UI surface
```

### A2A / A2UI details

The Agent Card declares:

- A2A protocol version: `0.3.0`
- Preferred transport: `JSONRPC`
- A2UI extension URI: `https://a2ui.org/a2a-extension/a2ui/v0.9`
- Supported catalog: the Gemini Enterprise composite catalog defined by `COMPOSITE_CATALOG_ID`
- Input and output modes: `text/plain` and `application/json+a2ui`

The template returns the A2UI v0.9 message sequence:

1. `createSurface`
2. `updateComponents`
3. `updateDataModel`

The action names currently handled by the server are `regenerate_draft` and `submit_ooo`.

## Requirements

- Python 3.11 (for local execution)
- Docker (for container build)
- A Google Cloud project with billing enabled
- Cloud Run and Artifact Registry permissions
- Access to a Gemini Enterprise app where custom A2A agents can be registered

## Run locally

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   macOS / Linux:

   ```bash
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:

   ```bash
   python main.py
   ```

   The service listens on `http://localhost:8080` by default.

4. Check the Agent Card:

   ```bash
   curl http://localhost:8080/.well-known/agent-card.json
   ```

   The root endpoint (`POST /`) expects an A2A JSON-RPC request; opening it in a browser is not a health check.

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `PORT` | `8080` | Port on which the FastAPI server listens |
| `AGENT_URL` | `http://localhost:8080` | Public base URL advertised in the Agent Card |

For deployment, set `AGENT_URL` to the deployed Cloud Run service URL so the Agent Card advertises a reachable endpoint.

## Build and deploy to Cloud Run

The following is an example deployment flow. Replace the project, region, and service names with your own.

```bash
gcloud config set project YOUR_PROJECT_ID

gcloud builds submit \
  --tag REGION-docker.pkg.dev/YOUR_PROJECT_ID/YOUR_REPOSITORY/ooto-buddy:latest

gcloud run deploy ooto-buddy \
  --image REGION-docker.pkg.dev/YOUR_PROJECT_ID/YOUR_REPOSITORY/ooto-buddy:latest \
  --region YOUR_REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars AGENT_URL=https://YOUR_CLOUD_RUN_SERVICE_URL
```

Create the Artifact Registry Docker repository before building if it does not already exist. For example:

```bash
gcloud artifacts repositories create YOUR_REPOSITORY \
  --repository-format=docker \
  --location=REGION \
  --description="Container images for OOTO-Buddy"
```

After deployment, copy the actual Cloud Run service URL and use it as `AGENT_URL`. If you update this variable after the first deployment, redeploy the service with the corrected value.

> **Security note:** `--allow-unauthenticated` is shown as a convenient setup for a Gemini Enterprise integration that needs to reach the endpoint. Confirm the authentication and network-access requirements of your environment before exposing the service publicly. Do not put secrets in the image or source code.

## Register in Gemini Enterprise

1. Deploy the service to Cloud Run and copy its HTTPS service URL.
2. Verify that the Agent Card is reachable:

   ```text
   https://YOUR_CLOUD_RUN_SERVICE_URL/.well-known/agent-card.json
   ```

3. In the Gemini Enterprise app's agent management interface, add/register a custom **A2A agent**.
4. Provide the deployed service endpoint according to the registration UI's requirements.
5. Confirm that the agent card is discovered and that the A2UI v0.9 extension/catalog is accepted.
6. Save the registration and test OOTO-Buddy from the app.

The exact menu labels and registration workflow can vary by Gemini Enterprise edition and UI version.

## Interaction behavior

### Initial prompt

For a new user turn, the server creates a surface ID based on the incoming message ID and returns the planner form with default values.

### Regenerate Draft

When the `regenerate_draft` action is received, the server reads the coverage contact from the action context and returns a sample casual-tone message. The existing surface ID is retained so the surface can be updated.

### Confirm & Activate OOO

When the `submit_ooo` action is received, the server reads the dates, contact, and draft from the action context, sets `is_confirmed=True`, and returns a confirmation surface.

The current implementation does **not** persist the plan or call external Gmail/Chat APIs. The checkboxes are represented in the A2UI data model, but the server does not currently process their values as activation settings.

## Troubleshooting

| Symptom | Check |
|---|---|
| Agent Card cannot be loaded | Confirm Cloud Run URL, service access settings, and `AGENT_URL` |
| Agent is registered but does not render a surface | Check A2A response structure, `application/json+a2ui` metadata, A2UI v0.9 extension, and catalog ID |
| Button action does not update the form | Inspect incoming `message.parts[].data` and ensure the event includes `userAction` or `action`, with the expected action name and context |
| Import error for template module | Ensure the file is named `ooto_template.py` and is included in the container |
| Container fails to build | Validate the `COPY` instructions in the Dockerfile and installable dependency names in `requirements.txt` |
| Wrong endpoint appears in Agent Card | Set `AGENT_URL` to the actual Cloud Run HTTPS URL and redeploy |


## Future enhancements

- Validate date ranges and required fields
- Persist OOO plans and confirmation status
- Integrate Gmail vacation responder and Google Chat status APIs
- Add authorization, identity validation, and audit logging
- Add automated tests for Agent Card, JSON-RPC requests, and A2UI action handling
- Add structured logging and error handling for malformed requests
- Replace sample contacts and default dates with configurable or directory-backed values

## License

Add the license and usage terms appropriate for your repository before publishing it.

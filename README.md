# Travel Planner AI Agent

A comprehensive, stateful travel planning assistant powered by the **Google Agent Development Kit (ADK)** and **Gemini 2.5 Flash**. The agent features real-time weather integration, destination search, trip budgeting, location geocoding, stateful memory persistence, interactive UI rendering (A2UI), AI image & video generation, and a custom web interface.

![Travel Planner AI Demo](demo.gif)

---

## 🌟 Key Features & Tool Audit

Based on the codebase in `app/` and `agents-cli-manifest.yaml`, the following tools and Google Cloud services are fully implemented:

### 1. 🗺️ Firestore Destination Database (`app/firestore_tools.py`)
- **`search_destinations`**: Search for travel destinations in Google Cloud Firestore by query term or category (e.g., Beaches, Culture, Nature, Foodie).
- **`get_destination_details`**: Retrieve full destination metadata, descriptions, and recommended activities from Firestore.
- **`add_destination`**: Persist new travel destinations and tags directly to the Firestore collection.

### 2. 🎨 AI Media Generation & Cloud Storage (`app/image_tools.py` & `app/video_tools.py`)
- **`generate_destination_postcard`**: Generates high-quality AI travel postcards using **Imagen 3** (`imagen-3.0-generate-002`).
- **`generate_destination_video`**: Generates short 3-second travel video previews using **Gemini Omni** (`gemini-omni-flash-preview`) in the `global` region via `client.interactions.create`.
- **Google Cloud Storage Bucket Integration**: Media bytes are directly uploaded in-memory to public Cloud Storage (`travel-planner-media-6a88f0f4`) and returned as public HTTPS URLs.
- **ADK Artifacts Panel**: Saves media artifacts via `ToolContext.save_artifact` so generated assets appear automatically in the ADK Playground Artifacts panel.

### 3. 📍 Google Maps & Location Services (`app/maps_tools.py`)
- **`geocode_address`**: Converts address strings into geographic latitude and longitude coordinates using the Google Maps Geocoding API.
- **`find_nearby_places`**: Discovers nearby tourist attractions, restaurants, and points of interest using the Google Maps Places API.

### 4. ☀️ Weather & Utilities (`app/agent.py`)
- **`get_weather`**: Retrieves live temperature, wind speed, and weather condition metrics for any destination via the Open-Meteo API.
- **`get_current_time`**: Looks up the current time and timestamp for any city or region.

### 5. 💰 Trip Budget & Currency Converter (`app/agent.py`)
- **`calculate_trip_budget`**: Calculates estimated total travel costs based on daily budget, duration, and number of travelers.
- **`convert_currency`**: Performs real-time currency conversions between standard ISO currency codes.

### 6. 🧠 Stateful Memory Bank (`app/agent.py`)
- **`PreloadMemoryTool` & `generate_memories_callback`**: Automatically extracts, persists, and preloads user travel preferences and memory items across multi-turn interactions.

### 7. 🧩 Interactive A2UI Component Cards (`app/a2ui_utils.py` & `app/agent.py`)
- **`a2ui_callback`**: Uses ADK model callbacks to transform agent responses into rich, interactive A2UI component catalog cards rendered directly inside supported frontends.

### 8. 💻 Plain Chat UI Web Application (`frontend/`)
- A minimal FastAPI web proxy and responsive front-end interface (`frontend/static/index.html`).
- Features a dark/light mode toggle, welcome onboarding card, quick category filter chips (`🏖️ Beaches`, `🏛️ Culture`, `🌲 Nature`, `🍜 Foodie`), rich bouncing dot typing indicators, and a 1-click itinerary copy button.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    User["User Web Browser"] <--> Frontend["FastAPI Proxy (frontend/)"]
    Frontend <--> ADK["Agent Development Kit (app/agent.py)"]
    ADK <--> Gemini["Gemini 2.5 Flash / Omni Models"]
    ADK <--> Firestore["Google Cloud Firestore"]
    ADK <--> GCS["Google Cloud Storage Bucket"]
    ADK <--> Maps["Google Maps & Open-Meteo APIs"]
```

---

## 🚀 Setup & Local Execution Instructions

### Prerequisites
- Python 3.10+
- `uv` package manager (`pip install uv` or `uv tool install google-agents-cli`)
- Google Cloud project with Vertex AI, Firestore, and Cloud Storage APIs enabled.

### 1. Installation & Dependencies
Clone the repository and install project dependencies using `uv`:

```bash
uv sync
cd frontend && uv pip install -r requirements.txt && cd ..
```

### 2. Environment Configuration
Create a `.env` file in the project root based on `.env.example`:

```bash
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-east1
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### 3. Seed Firestore Database (Optional)
Populate your Firestore database with initial destination records:

```bash
uv run python seed_firestore.py
```

### 4. Option A: Run Interactive Agent Playground (CLI)
Test the agent logic, tools, and artifacts interactively in your terminal:

```bash
agents-cli playground
```

### 5. Option B: Run Agent & Web Chat UI Locally
To run the full agent with the custom web chat interface locally:

```bash
# 1. Set environment variables to route to your agent directory
export AGENT_DIRECTORY=app
export AGENT_ENGINE_RESOURCE_NAME=$(jq -r .reasoning_engine_id deployment_metadata.json 2>/dev/null || echo "")

# 2. Start the FastAPI server locally from the frontend folder
cd frontend
uv run uvicorn main:app --host 0.0.0.0 --port 8080
```

Open your browser to `http://localhost:8080` to interact with the Travel Planner AI chat interface.

---

## ☁️ Deployment Instructions (Agent Engine & Cloud Run)

If you need to deploy or re-deploy the backend agent and web frontend to Google Cloud:

### Step 1: Deploy the Agent Engine Backend
Deploy the updated agent code in `app/` to Vertex AI Reasoning Engine:

```bash
agents-cli deploy --no-confirm-project
```
*This updates `deployment_metadata.json` with the deployed Reasoning Engine resource ID.*

### Step 2: Deploy the Frontend Chat UI to Cloud Run
Deploy the FastAPI chat UI container to Cloud Run and configure its target agent parameters:

```bash
# 1. Extract deployed Reasoning Engine ID
REASONING_ENGINE_ID=$(jq -r .reasoning_engine_id deployment_metadata.json)

# 2. Deploy frontend service to Cloud Run
gcloud run deploy travel-planner-frontend \
  --source ./frontend \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME=${REASONING_ENGINE_ID},AGENT_DIRECTORY=app

# 3. Grant Cloud Run service account access to Vertex AI Agent Engine
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")

gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

---

## 🧪 Running Unit & Integration Tests

Run the test suite with `pytest`:

```bash
uv run pytest tests/unit tests/integration
```

# Project Prompts & Context History

This document records the chronological prompts, instructions, and context used to build, customize, test, deploy, and publish the **Travel Planner AI Agent** application.

---

## 📜 Full Development Prompt History

### 1. Frontend Scaffolding & Agent Wiring
> "Using the build-agent-frontend skill, copy its minimal FastAPI proxy and chat UI template into `./frontend` and wire it to my deployed agent using `AGENT_ENGINE_RESOURCE_NAME` and `AGENT_DIRECTORY` (my `agent_directory` from `agents-cli-manifest.yaml`). Keep it a plain chat UI. Do not build a React app or pull in a large sample frontend."

---

### 2. Local Web Server Execution
> "Run my frontend locally from the `frontend/` folder: install its dependencies, set `AGENT_ENGINE_RESOURCE_NAME` to the resource name in `deployment_metadata.json` and `AGENT_DIRECTORY` to my `agent_directory` from `agents-cli-manifest.yaml`, then start the server on `http://localhost:8080`."

---

### 3. Cloud Run Deployment & IAM Permissions
> "Deploy the frontend to Cloud Run pointing at my `AGENT_ENGINE_RESOURCE_NAME` and `AGENT_DIRECTORY`, and grant the Cloud Run service account `roles/aiplatform.user` so it can reach the agent."

---

### 4. Branding & Custom UI Theme
> "Rebrand my frontend: set the title and header to my app's name and change the accent color."

---

### 5. Interactive Prompt Chips
> "Add a row of 3 clickable example prompts above the input, tailored to my agent (look at my `project_brief.md`)."

---

### 6. Custom Dialogue Layout
> "Create a nice dialogue layout for my app that matches my theme."

---

### 7. UI/UX Enhancements & Refinements
> "Suggest some UI improvements we can make to the frontend."
*(Implemented: Dark/Light Mode toggle, Category Filter Tabs (`🏖️ Beaches`, `🏛️ Culture`, `🌲 Nature`, `🍜 Foodie`), Bouncing Dot Typing Indicator, and 1-Click Itinerary Copying).*

---

### 8. Gemini Omni Video Generation Tool
> "Add a tool that generates a short video for an item in my agent's domain (look at my `project_brief.md`) using Google's Omni model (`gemini-omni-flash-preview`) in the `global` region. Do two things with the generated video: (1) save it with `tool_context.save_artifact` so it shows up in the Playground's Artifacts panel, and (2) upload the same video bytes to the public Cloud Storage bucket I created earlier and return its public https URL (`https://storage.googleapis.com/<bucket>/<object>`) from the tool. Hardcode the bucket name as a string, the same way we hardcoded the Firestore project. Do not write the video to a local file and return a path. Use the Developer Knowledge MCP to confirm the API if you're unsure."

---

### 9. Demo Video Recording & Lo-Fi Music Synthesis
> "Record a demo video of my agent. Show it doing the thing my app does best, then ask a second, richer prompt that shows off a tool call, a database lookup, or a generated image. A great clip is short and snappy — roughly 30–40 seconds. Record a demo of my agent and add some upbeat lo-fi background music. Keep the 35 sec demo video in the repository as well."

---

### 10. Accurate Codebase Audit & README Generation
> "Generate a `README.md` for my project. Describe what my agent actually does based on the code in this repo — read `app/` and `agents-cli-manifest.yaml` to see which tools and Google Cloud services are really wired up (Memory Bank, Firestore, Cloud Storage, image generation, A2UI) and list ONLY those. Don't claim a capability the code doesn't implement; if something in my `project_brief.md` was planned but not finished, leave it out or mark it clearly as 'planned, not yet implemented.' Do NOT put any live links to localhost (like `http://localhost:8080`) or to ephemeral Cloud URLs (Cloud Run / Agent Engine endpoints from this lab) in the README — they die when this workstation is torn down and will 404 for anyone reading it later. If you need to show how to run it, write it as setup/run instructions (the commands to start it locally), not as a clickable link. Then convert the demo I recorded with record-demo (the `.webm` file) to an optimized, looping GIF and embed it near the top with a relative path so it plays inline — use only that real recording; if there isn't one, leave the demo out rather than generating or drawing a placeholder."

---

### 11. GitHub Repository Publication & Documentation
> "Publish my project to GitHub. Don't generate the swag submission form."

> "Create a `prompts.md` file and push it as well. It should contain all the context and prompts I gave to create the app."

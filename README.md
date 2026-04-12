---
title: Cloud Cost Optimizer Environment
emoji: ☁️
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
---

# ☁️ AI-Driven Cloud Cost Optimizer Environment

An Autonomous Cloud Financial Management Environment that uses Large Language Models to balance strict system survival with aggressive cost consolidation. 

Modern companies waste billions of dollars annually on over-provisioned cloud infrastructure. This environment replaces static auto-scaling rules with an intelligent, real-time AI cloud engineer, heavily featuring **"Make-Before-Break"** load balancing to survive traffic surges without dropping system health.

## 🚀 The Simulation Scenarios (Tasks)

The environment includes three specific stress-test scenarios for the AI agent to solve:
1. **`zombie_shutdown`**: Identify and terminate expensive servers running at 0% CPU without touching the active nodes.
2. **`cost_reduction`**: Consolidate loads and terminate high-cost, underutilized servers to minimize hourly burn rate.
3. **`load_balance_spike`**: Face a massive simulated traffic surge and scale out infrastructure immediately to prevent system health from dropping to zero.

---

## 💻 Quick Start & Local Development

Because this project is fully Dockerized and uses the standard OpenEnv specification, running it locally is incredibly simple.

### 1. Build and Run the Environment
```bash
# Build the Docker image
docker build -t cloud-ai-optimizer .

# Run the OpenEnv FastApi server
docker run -p 8000:8000 cloud-ai-optimizer
```

2. Run the Baseline AI Agent
Once the environment is running on port 8000, open a second terminal and run the official inference script. Make sure you have an `.env` file with your `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN`.

```bash
python inference.py
```

You will see the AI output its logic [START], [STEP], and [END] logs as it manages the server rack in real-time!

🧠 Environment Details
Action Schema (CloudCostOptimizerAction)
The agent interacts with the environment by sending this JSON structure:

action_type (str): The command to execute (e.g., "start_server", "terminate_server", "do_nothing").

target_server_id (str): The ID of the server to target, or "new" if provisioning a new one.

Observation Schema (CloudCostOptimizerObservation)
The environment returns the current state of the infrastructure:

servers (list): A list of server objects detailing id, cpu_usage, hourly_cost, and status.

system_health (float): The overall health of the cluster (0.0 to 100.0).

Reward & Info
The info dictionary returns current_cost, system_health, and step_number. The agent is evaluated heavily on maximizing the system_health score while minimizing the current_cost across an episode.

☁️ Deploying to Hugging Face Spaces
You can easily deploy this environment to Hugging Face Spaces using the openenv push command provided by the hackathon organizers:

```Bash
# From the project root
openenv push

# Or specify a specific repository
openenv push --repo-id my-org/my-env

```

The openenv push command will:

Validate the openenv.yaml file.

Upload the environment to Hugging Face (ensuring you're logged in).

Automatically expose the Web Interface, API Docs, and WebSocket endpoints.

### 📂 Project Structure

```text
cloud_cost_optimizer/
├── openenv.yaml           # OpenEnv manifest
├── inference.py           # The baseline AI agent evaluation script
├── models.py              # Pydantic Action/Observation schemas
├── tasks.py               # The 3 hackathon evaluation scenarios
├── requirements.txt       # Dependencies (FastAPI, OpenAI, etc.)
├── server/
│   ├── cloud_cost_optimizer_environment.py  # Core simulation logic
│   └── app.py             # OpenEnv FastAPI & WebSocket application
├── Dockerfile             # Container image definition
└── .gitignore             # Excluded files (like .env)
```

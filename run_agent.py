import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import your environment and models
from server import CloudCostOptimizerEnvironment
from models import CloudCostOptimizerAction

# Load the GEMINI_API_KEY from your .env file
load_dotenv()

def run_agent_loop():
    # 1. Setup the Gemini Client
    client = genai.Client()
    
    # 2. Setup the Environment
    env = CloudCostOptimizerEnvironment()
    observation = env.reset()
    initial_hourly_cost = sum(server.hourly_cost for server in observation.servers)
    print("🌍 Environment Initialized. Starting Gemini AI Agent Loop...\n")

    # 3. Give the Agent its "Persona" and Rules
    system_prompt = """
    You are an expert Cloud Financial Management AI. 
    Your goal is to minimize cloud costs without degrading system health.
    
    Rules:
    1. 🚨 EMERGENCY: If ANY server's cpu_usage > 85.0, start a new server (action_type='start_server', target_server_id='new'). This overrides all other rules.
    2. ZERO USE: If a server has < 5.0 CPU usage, terminate it (action_type='terminate_server').
    3. 🧠 CONSOLIDATION: If no server is in an emergency, look at the overall load. If most servers are running below 50.0 CPU, you have too many servers! Find the server with the HIGHEST `hourly_cost` and terminate it to force the load balancer to pack the traffic onto cheaper servers.
    4. If average CPU is healthy (between 50 and 80) and costs are optimized, output action_type='do_nothing'.
    """

    max_steps = 5 
    
    for step in range(max_steps):
        print(f"--- STEP {step + 1} ---")
        
        # Convert Pydantic observation to a JSON string for the LLM to read
        current_state_json = observation.model_dump_json(indent=2)
        print(f"👀 Agent sees:\n{current_state_json}\n")

        print("🧠 Agent is thinking...")
        
        # 4. Ask Gemini to make a decision using Structured Outputs
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Fast, highly capable, and free
            contents=f"Here is the current environment state: {current_state_json}. What is your next action?",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=CloudCostOptimizerAction, # Force the Pydantic schema!
                temperature=0.1, # Keep it low so the agent makes logical, consistent choices
            ),
        )

        # 5. Extract the JSON and convert it back into your Pydantic object
        action = CloudCostOptimizerAction.model_validate_json(response.text)
        
        print(f"✅ Agent decided to execute:\n{action}\n")

        # 6. Execute the action in the environment
        observation, reward, done, info = env.step(action)
        
        if done:
            print("🏁 Environment signaled the task is complete!")
            break
    
    # ==========================================
    # 🧾 PRINT THE FINAL SCOREBOARD
    # ==========================================
    # Calculate the final cost after all AI actions
    final_hourly_cost = sum(server.hourly_cost for server in observation.servers)
    
    print("\n" + "="*45)
    print("🧾 FINAL AI OPTIMIZATION RECEIPT")
    print("="*45)
    print(f"Initial System Cost: ${initial_hourly_cost:.2f} / hour")
    print(f"Final System Cost:   ${final_hourly_cost:.2f} / hour")
    print(f"Total Money Saved:   ${(initial_hourly_cost - final_hourly_cost):.2f} / hour")
    print(f"Final System Health: {observation.system_health}%")
    print("="*45 + "\n")
    

if __name__ == "__main__":
    run_agent_loop()
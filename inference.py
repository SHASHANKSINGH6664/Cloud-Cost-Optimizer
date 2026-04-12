try:
    import openai
    import dotenv
except ImportError:
    import sys
    import subprocess
    print("Dependencies missing. Force installing openai and python-dotenv...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "python-dotenv"])
    import openai
    import dotenv
    
import os
import json




from openai import OpenAI
from dotenv import load_dotenv

from server import CloudCostOptimizerEnvironment
from models import CloudCostOptimizerAction

load_dotenv()

# ==========================================
# 1. HACKATHON MANDATORY SETUP
# ==========================================
# The rules require these exact variables
api_base_url = os.environ.get("API_BASE_URL")
hf_token = os.environ.get("HF_TOKEN")
model_name = os.environ.get("MODEL_NAME")

client = OpenAI(
    base_url=api_base_url,
    api_key=hf_token
)

def run_evaluation():
    env = CloudCostOptimizerEnvironment()
    
    system_prompt = """
    You are an expert Cloud AI. Your goal is to save money but keep the system healthy.
    
    Rules:
    1. EMERGENCY: If ANY server > 85.0 CPU, output action_type='start_server', target_server_id='new'.
    2. SURVIVAL: NEVER terminate a server if it is the ONLY one running.
    3. ZERO USE: If server < 5.0 CPU, terminate it (action_type='terminate_server').
    4. CONSOLIDATE: If multiple servers run < 50.0 CPU, terminate the one with the HIGHEST hourly_cost.
    5. HEALTHY: If average CPU is 50-80, output action_type='do_nothing'.
    
    IMPORTANT: You must return valid JSON matching this schema exactly:
    {
      "action_type": "string",
      "target_server_id": "string"
    }
    """

    for task_id in [1, 2, 3]:
        # MANDATORY LOG: [START]
        print(f"[START] Task {task_id}")
        
        observation = env.reset(task_id=task_id)
        done = False
        step_count = 0
        
        # Give the AI 3 steps to solve the scenario
        while not done and step_count < 3:
            step_count += 1
            
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Current state: {observation.model_dump_json()}. What is your next action?"}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                
                raw_json = response.choices[0].message.content
                action_dict = json.loads(raw_json)
                action = CloudCostOptimizerAction(**action_dict)
                
                # Safely extract just the observation
                step_result = env.step(action)
                observation = step_result[0] if isinstance(step_result, tuple) else step_result
                
                # MANDATORY LOG: [STEP]
                print(f"[STEP] Task {task_id} | Step {step_count} | Action: {action.action_type} on {action.target_server_id} | Health: {info['health']}% | Cost: ${info['current_cost']}/hr")
                
            except Exception as e:
                print(f"[STEP] Task {task_id} | Step {step_count} | ERROR: {str(e)} | Action: DO_NOTHING")
                fallback_action = CloudCostOptimizerAction(
                    action_type="do_nothing", 
                    target_server_id="none"
                )
                # Safely extract just the observation here too
                step_result = env.step(fallback_action)
                observation = step_result[0] if isinstance(step_result, tuple) else step_result

        # Calculate final score for the task
        health_value = observation.system_health
        health_score = health_value / 100.0
        task_score = health_score * 1.0  # Simple scoring metric for the grader
        
        # MANDATORY LOG: [END]
        print(f"[END] Task {task_id} | Score: {task_score:.2f}")

if __name__ == "__main__":
    run_evaluation()
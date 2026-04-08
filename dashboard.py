import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import random

# Import your custom environment and models
from server import CloudCostOptimizerEnvironment
from models import CloudCostOptimizerAction

# Load environment variables
load_dotenv()

# ==========================================
# 1. SETUP PAGE & SESSION STATE
# ==========================================
st.set_page_config(page_title="AI Cloud Optimizer", layout="wide")
st.title("☁️ AI Cloud Cost Optimizer Dashboard")

if "env" not in st.session_state:
    st.session_state.env = CloudCostOptimizerEnvironment()
    st.session_state.observation, _ = st.session_state.env.reset()
    st.session_state.client = genai.Client()
    st.session_state.logs = []
    
    # NEW: Track money across the whole session!
    st.session_state.total_money_saved = 0.0
    st.session_state.last_step_cost = sum(s.hourly_cost for s in st.session_state.observation.servers if s.status == "RUNNING")

system_prompt = """
You are an expert Cloud AI. 
Your goal is to save money but keep the system healthy.

Rules:
1. 🚨 EMERGENCY: If ANY server is over 85.0 CPU, you MUST start a new server (action_type='start_server', target_server_id='new').
2. 🛡️ SURVIVAL: NEVER terminate a server if it is the ONLY one running. The website needs at least one server to live!
3. 🗑️ ZERO USE: If a server is under 5.0 CPU, terminate it.
4. 🧠 CONSOLIDATE: If you have MULTIPLE servers running, and they are mostly under 50.0 CPU, terminate the one with the HIGHEST `hourly_cost`.
5. ⚖️ HEALTHY: If average CPU is between 50 and 80, output action_type='do_nothing'.
"""

obs = st.session_state.observation

# ==========================================
# 2. UI: TOP METRICS & THE BANK
# ==========================================
st.markdown("### 📊 Live System Metrics")
col1, col2, col3, col4 = st.columns(4)

current_cost = sum(s.hourly_cost for s in obs.servers if s.status == "RUNNING")
active_servers = len([s for s in obs.servers if s.status == "RUNNING"])

col1.metric("System Health", f"{obs.system_health:.1f}%")
col2.metric("Current Burn Rate", f"${current_cost:.2f}/hr")
col3.metric("Active Servers", f"{active_servers}")
# NEW: The Hackathon Winning Metric
col4.metric("💰 All-Time Savings", f"${st.session_state.total_money_saved:.2f}", delta="Money Saved!")

st.divider()

# ==========================================
# 3. UI: SERVER VISUALIZATION
# ==========================================
st.markdown("### 🖥️ Server Rack")
server_cols = st.columns(max(len(obs.servers), 1)) 

for idx, server in enumerate(obs.servers):
    with server_cols[idx]:
        if server.status == "RUNNING":
            if server.cpu_usage > 85.0:
                st.error(f"**{server.id}** 🔥 DANGER")
            else:
                st.success(f"**{server.id}**")
            
            st.progress(min(int(server.cpu_usage) / 100.0, 1.0)) # Cap at 1.0 to prevent UI crashes
            st.caption(f"CPU: {server.cpu_usage:.1f}%  |  Cost: ${server.hourly_cost:.2f}")
        else:
            st.warning(f"**{server.id}** (TERMINATED)")
            st.caption(f"CPU: 0.0%  |  Cost: $0.00")

st.divider()

# ==========================================
# 4. CONTROLS (AI & CHAOS)
# ==========================================
col_btn, col_log = st.columns([1, 2])

with col_btn:
    st.markdown("### 🤖 Controls")
    
    # Normal AI Step
    if st.button("Step Forward (Run AI)", use_container_width=True, type="primary"):
        with st.spinner("AI is analyzing the system..."):
            
            # Ask Gemini what to do
            response = st.session_state.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Current state: {obs.model_dump_json()}. What is your next action?",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=CloudCostOptimizerAction,
                    temperature=0.1,
                ),
            )
            
            # Parse action and step environment
            action = CloudCostOptimizerAction.model_validate_json(response.text)
            st.session_state.observation, reward, done, info = st.session_state.env.step(action)
            
            # Update the Bank!
            new_cost = sum(s.hourly_cost for s in st.session_state.observation.servers if s.status == "RUNNING")
            saved_this_step = st.session_state.last_step_cost - new_cost
            st.session_state.total_money_saved += saved_this_step
            st.session_state.last_step_cost = new_cost
            
            # Log the action
            icon = "🛑" if "terminate" in action.action_type else "🚀" if "start" in action.action_type else "👀"
            st.session_state.logs.insert(0, f"{icon} AI Action: `{action.action_type}` on `{action.target_server_id}`")
            st.rerun()

    # NEW: God Mode / Chaos Button
    st.markdown("---")
    st.markdown("### ⚡ Inject Chaos")
    if st.button("Simulate Massive Traffic Spike", use_container_width=True):
        # Find the first running server and manually set its CPU to 99%
        for s in st.session_state.observation.servers:
            if s.status == "RUNNING":
                s.cpu_usage = 99.0
                st.session_state.logs.insert(0, f"⛈️ INJECTED CHAOS: Forced {s.id} to 99% CPU!")
                st.rerun()
                break

with col_log:
    st.markdown("### 📝 AI Activity Log")
    for log in st.session_state.logs[:6]: 
        st.info(log)
# tasks.py

# Import your ServerState model so we can build servers
from models import ServerState 

def get_task(task_id: int):
    """Returns the starting layout of servers for a specific hackathon task."""
    
    if task_id == 1:
        # 🟢 TASK 1: Scale Down (Stop the Bleeding)
        # Scenario: 5 servers running, but barely any traffic. Huge waste of money.
        # Goal: The AI must terminate servers 2 through 5 to save money, but keep server 1 alive.
        return [
            ServerState(id="server-1", cpu_usage=10.0, hourly_cost=2.0, status="RUNNING"),
            ServerState(id="server-2", cpu_usage=0.0, hourly_cost=5.0, status="RUNNING"),
            ServerState(id="server-3", cpu_usage=0.0, hourly_cost=2.0, status="RUNNING"),
            ServerState(id="server-4", cpu_usage=0.0, hourly_cost=5.0, status="RUNNING"),
            ServerState(id="server-5", cpu_usage=0.0, hourly_cost=1.5, status="RUNNING")
        ]
        
    elif task_id == 2:
        # 🔴 TASK 2: Scale Out (Survive the Spike)
        # Scenario: A massive traffic spike hits a single server. Imminent crash.
        # Goal: The AI must immediately start a new server to save the system.
        return [
            ServerState(id="server-1", cpu_usage=98.0, hourly_cost=2.0, status="RUNNING")
        ]
        
    elif task_id == 3:
        # 🧠 TASK 3: Consolidate (Smart Packing)
        # Scenario: A messy infrastructure. Traffic is low, but expensive servers are running.
        # Goal: The AI must terminate the $5/hr servers, forcing the load balancer 
        # to pack the traffic onto the cheaper $1/hr servers.
        return [
            ServerState(id="server-1", cpu_usage=30.0, hourly_cost=1.0, status="RUNNING"), # Keep this
            ServerState(id="server-2", cpu_usage=25.0, hourly_cost=5.0, status="RUNNING"), # Kill this
            ServerState(id="server-3", cpu_usage=20.0, hourly_cost=5.0, status="RUNNING"), # Kill this
            ServerState(id="server-4", cpu_usage=35.0, hourly_cost=1.0, status="RUNNING")  # Keep this
        ]
    
    else:
        raise ValueError(f"Task {task_id} does not exist.")
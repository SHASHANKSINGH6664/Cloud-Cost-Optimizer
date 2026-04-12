# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Cloud Cost Optimizer Environment.

The cloud_cost_optimizer environment is a simple test environment that echoes back messages.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# 1. What does a single server look like?
class ServerState(BaseModel):
    id: str
    cpu_usage: float      # 0.0 to 100.0
    hourly_cost: float    # How much money it wastes
    status: str           # "RUNNING" or "STOPPED"

# 2. What does the AI see? (Observation)
class CloudCostOptimizerObservation(BaseModel):
    servers: List[ServerState]
    system_health: float  # Starts at 100%. Drops if the AI stops busy servers.
    reward: float = 0.0
    done: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

# 3. What can the AI do? (Action)
class CloudCostOptimizerAction(BaseModel):
    action_type: str      # "STOP" or "KEEP"
    target_server_id: str # Which server to apply the action to
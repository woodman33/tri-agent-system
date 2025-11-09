"""
Dual-Layer Tri-Agent Orchestrator

Spawns 6 agents per task:
- Layer 1 (Primary): 3 agents using Ollama (user-facing work)
- Layer 2 (Shadow): 3 agents using vLLM (monitoring + backup)

100% Free & Open Source:
- Ollama for primary (fast, local)
- vLLM for shadow (can run locally or self-hosted)
- Qwen3 8B model (free, open source)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from agents.agent1_coder import Agent1Coder
from agents.agent2_improver import Agent2Improver
from agents.agent3_doctor import Agent3Doctor
from core.spawner import TriAgentSpawner
from core.inference_layer import InferenceLayer, OllamaProvider, VLLMProvider
from shared.memory import SharedMemory

from typing import Dict, Any, Optional, List
import json


class DualLayerTriAgent:
    """
    6-Agent System:
    - 3 primary agents (Ollama - fast, user-facing)
    - 3 shadow agents (vLLM - monitoring, backup)

    When complexity increases, spawns 6 more (3+3)
    """

    def __init__(self, workspace_id: str = "default", use_vllm_shadow: bool = True):
        self.workspace_id = workspace_id

        # Setup inference layers
        self.primary_inference = self._setup_primary_inference()
        self.shadow_inference = self._setup_shadow_inference() if use_vllm_shadow else None

        # Layer 1: Primary agents (Ollama)
        print(f"\n[Dual-Layer] 🎭 Initializing Layer 1 (Primary - Ollama)")
        self.layer1_agent1 = Agent1Coder(f"{workspace_id}_layer1")
        self.layer1_agent2 = Agent2Improver(f"{workspace_id}_layer1")
        self.layer1_agent3 = Agent3Doctor(f"{workspace_id}_layer1")

        # Layer 2: Shadow agents (vLLM) - monitoring
        if use_vllm_shadow and self.shadow_inference:
            print(f"[Dual-Layer] 👁️  Initializing Layer 2 (Shadow - vLLM)")
            self.layer2_agent1m = Agent1Coder(f"{workspace_id}_layer2_monitor")
            self.layer2_agent2m = Agent2Improver(f"{workspace_id}_layer2_monitor")
            self.layer2_agent3m = Agent3Doctor(f"{workspace_id}_layer2_monitor")
        else:
            print(f"[Dual-Layer] ⚠️  Shadow layer disabled (vLLM not available)")
            self.layer2_agent1m = None
            self.layer2_agent2m = None
            self.layer2_agent3m = None

        # Spawner for both layers
        self.spawner = TriAgentSpawner(workspace_id)

        # Shared memory
        self.memory = SharedMemory(workspace_id)

        print(f"\n{'='*60}")
        print(f"✅ DUAL-LAYER TRI-AGENT INITIALIZED")
        print(f"{'='*60}")
        print(f"Workspace: {workspace_id}")
        print(f"Layer 1 (Primary): Ollama - 3 agents (user-facing)")
        if self.shadow_inference:
            print(f"Layer 2 (Shadow):  vLLM - 3 agents (monitoring)")
        print(f"Total Agents: {6 if self.shadow_inference else 3}")
        print(f"{'='*60}\n")

    def _setup_primary_inference(self) -> InferenceLayer:
        """Setup primary inference (Ollama)"""
        ollama = OllamaProvider(model="qwen3:8b")

        if not ollama.is_available():
            print("⚠️  WARNING: Ollama not running. Start with: brew services start ollama")

        return InferenceLayer(ollama)

    def _setup_shadow_inference(self) -> Optional[InferenceLayer]:
        """
        Setup shadow inference (vLLM).

        To use vLLM locally:
        1. Install: pip install vllm
        2. Start server:
           vllm serve Qwen/Qwen2.5-7B-Instruct \\
               --port 8000 \\
               --max-model-len 4096
        3. vLLM will be available at http://localhost:8000
        """
        vllm_url = "http://localhost:8000"

        vllm = VLLMProvider(api_url=vllm_url, model="Qwen/Qwen2.5-7B-Instruct")

        if not vllm.is_available():
            print(f"⚠️  vLLM not available at {vllm_url}")
            print(f"   To enable shadow layer:")
            print(f"   1. pip install vllm")
            print(f"   2. vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000")
            return None

        print(f"✅ vLLM shadow layer active at {vllm_url}")
        return InferenceLayer(vllm)

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task using dual-layer system.

        Layer 1 does primary work, Layer 2 monitors.
        """
        print(f"\n{'='*60}")
        print(f"📋 DUAL-LAYER TASK EXECUTION")
        print(f"{'='*60}")
        print(f"Task: {task.get('description', 'Unnamed')}")
        print(f"Layer 1: Primary execution (Ollama)")
        if self.shadow_inference:
            print(f"Layer 2: Monitoring & backup (vLLM)")
        print(f"{'='*60}\n")

        # Check if we need to spawn additional teams
        complexity = self.spawner.assess_task_complexity(task)
        teams_spawned = []

        if complexity > 3:
            print(f"[Spawner] 🧬 Complexity: {complexity}")
            print(f"[Spawner] 📊 Spawning {complexity // 4 + 1} team pairs (6 agents each)\n")

            teams_needed = complexity // 4 + 1
            for i in range(teams_needed):
                team_id = self._spawn_dual_layer_team(task, i)
                teams_spawned.append(team_id)

        # Layer 1: Start primary work
        print(f"[Layer 1] 🚀 Primary agents starting...")
        self.layer1_agent1.start_task(task.get("description", "Task"))

        if "user_input" in task:
            self.memory.add_user_context("user_input", task["user_input"])

        # Layer 2: Start monitoring (if available)
        if self.shadow_inference:
            print(f"[Layer 2] 👁️  Shadow agents monitoring Layer 1...")
            self._monitor_layer1()

        # Get results
        result = {
            "task": task.get("description"),
            "status": "executing",
            "layer1": {
                "agent1": self.layer1_agent1.get_status(),
                "agent2": self.layer1_agent2.get_status(),
                "agent3": self.layer1_agent3.get_status()
            },
            "layer2": None,
            "spawned_teams": teams_spawned
        }

        if self.shadow_inference:
            result["layer2"] = {
                "agent1m": self.layer2_agent1m.get_status() if self.layer2_agent1m else None,
                "agent2m": self.layer2_agent2m.get_status() if self.layer2_agent2m else None,
                "agent3m": self.layer2_agent3m.get_status() if self.layer2_agent3m else None
            }

        return result

    def _spawn_dual_layer_team(self, task: Dict[str, Any], team_index: int) -> str:
        """
        Spawn 6 agents:
        - 3 for primary work (Ollama)
        - 3 for monitoring (vLLM if available)
        """
        subtask = task.get("subtasks", [f"Subtask {team_index+1}"])[team_index] \
                  if team_index < len(task.get("subtasks", [])) \
                  else f"Parallel work {team_index+1}"

        # Spawn primary team (Layer 1)
        team_id_primary = self.spawner.spawn_tri_agent_team(
            task=subtask,
            parent_agent_id="layer1_agent1",
            team_workspace=f"{self.workspace_id}_team{team_index}_layer1"
        )

        # Spawn shadow team (Layer 2) if vLLM available
        if self.shadow_inference:
            team_id_shadow = self.spawner.spawn_tri_agent_team(
                task=f"Monitor: {subtask}",
                parent_agent_id="layer2_agent1m",
                team_workspace=f"{self.workspace_id}_team{team_index}_layer2"
            )

            print(f"[Spawner] ✅ Spawned team pair {team_index+1}:")
            print(f"  Primary: {team_id_primary} (Ollama)")
            print(f"  Shadow:  {team_id_shadow} (vLLM)")

            return f"{team_id_primary}+{team_id_shadow}"
        else:
            print(f"[Spawner] ✅ Spawned team {team_index+1}: {team_id_primary} (Ollama only)")
            return team_id_primary

    def _monitor_layer1(self):
        """Layer 2 monitors Layer 1"""
        if not self.shadow_inference:
            return

        # Agent 2M monitors Agent 1
        layer1_status = self.layer1_agent1.get_status()

        if layer1_status.get("needs_help"):
            print(f"[Layer 2] 🚨 Layer 1 Agent 1 needs help!")
            print(f"[Layer 2] 🔧 Shadow Agent 2M providing assistance...")

        # Agent 3M monitors overall health
        if self.layer2_agent3m:
            diagnosis = self.layer2_agent3m.diagnose_system()
            if diagnosis["health"] != "healthy":
                print(f"[Layer 2] ⚠️  System health: {diagnosis['health']}")
                print(f"[Layer 2] 🏥 Shadow Agent 3M standing by for intervention...")

    def get_system_status(self) -> Dict[str, Any]:
        """Get complete dual-layer status"""
        status = {
            "workspace_id": self.workspace_id,
            "inference": {
                "primary": self.primary_inference.get_status(),
                "shadow": self.shadow_inference.get_status() if self.shadow_inference else None
            },
            "layer1_primary": {
                "agent1": self.layer1_agent1.get_status(),
                "agent2": self.layer1_agent2.get_status(),
                "agent3": self.layer1_agent3.get_status()
            },
            "layer2_shadow": None,
            "spawned_teams": self.spawner.get_all_spawned_teams()
        }

        if self.shadow_inference:
            status["layer2_shadow"] = {
                "agent1m": self.layer2_agent1m.get_status() if self.layer2_agent1m else None,
                "agent2m": self.layer2_agent2m.get_status() if self.layer2_agent2m else None,
                "agent3m": self.layer2_agent3m.get_status() if self.layer2_agent3m else None
            }

        return status

    def run_demo(self):
        """Run dual-layer demonstration"""
        print("\n" + "="*60)
        print("🎭 DUAL-LAYER TRI-AGENT DEMO")
        print("="*60)

        # Demo 1: Simple task (3 agents on Layer 1, 3 monitoring on Layer 2)
        simple_task = {
            "description": "Fix typo in README",
            "subtasks": ["Find typo"],
            "estimated_hours": 0.5,
            "difficulty": "low",
            "user_input": "Line 42 has a typo"
        }

        print(f"\n{'#'*60}")
        print(f"# DEMO 1: Simple Task (6 agents total)")
        print(f"{'#'*60}")
        result1 = self.execute_task(simple_task)

        # Demo 2: Complex task (spawns multiple team pairs)
        complex_task = {
            "description": "Build microservices architecture",
            "subtasks": [
                "API Gateway",
                "Auth Service",
                "User Service",
                "Payment Service"
            ],
            "estimated_hours": 30,
            "dependencies": ["Docker", "K8s"],
            "difficulty": "high",
            "user_input": "Need scalable microservices"
        }

        print(f"\n{'#'*60}")
        print(f"# DEMO 2: Complex Task (Spawns multiple 6-agent teams)")
        print(f"{'#'*60}")
        result2 = self.execute_task(complex_task)

        # Final status
        print(f"\n{'='*60}")
        print(f"📊 FINAL SYSTEM STATUS")
        print(f"{'='*60}")
        status = self.get_system_status()

        print(f"\n🔹 Layer 1 (Primary - Ollama):")
        print(f"  Agent 1: {status['layer1_primary']['agent1']['role']}")
        print(f"  Agent 2: {status['layer1_primary']['agent2']['role']}")
        print(f"  Agent 3: {status['layer1_primary']['agent3']['role']}")

        if status['layer2_shadow']:
            print(f"\n🔹 Layer 2 (Shadow - vLLM):")
            print(f"  Agent 1M: Monitoring Agent 1")
            print(f"  Agent 2M: Monitoring Agent 2")
            print(f"  Agent 3M: Monitoring Agent 3")

        print(f"\n🧬 Spawned Teams: {len(status['spawned_teams'])}")

        print(f"\n{'='*60}")
        print(f"✅ DEMO COMPLETE")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # Run demonstration
    orchestrator = DualLayerTriAgent("demo_dual_layer", use_vllm_shadow=True)
    orchestrator.run_demo()

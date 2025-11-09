"""
Tri-Agent Orchestrator
Manages the coordination between Agent 1 (Coder), Agent 2 (Improver), and Agent 3 (Doctor)
Handles spawning when needed
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from agents.agent1_coder import Agent1Coder
from agents.agent2_improver import Agent2Improver
from agents.agent3_doctor import Agent3Doctor
from core.spawner import TriAgentSpawner
from shared.memory import SharedMemory

from typing import Dict, Any, Optional
import time


class TriAgentOrchestrator:
    """
    Orchestrates the tri-agent system:
    - Agent 1: Focused coder
    - Agent 2: Helper and backup
    - Agent 3: Doctor and arbitrator
    """

    def __init__(self, workspace_id: str = "default"):
        self.workspace_id = workspace_id

        # Initialize all three agents
        self.agent1 = Agent1Coder(workspace_id)
        self.agent2 = Agent2Improver(workspace_id)
        self.agent3 = Agent3Doctor(workspace_id)

        # Initialize spawner
        self.spawner = TriAgentSpawner(workspace_id)

        # Shared memory
        self.memory = SharedMemory(workspace_id)

        print(f"[Orchestrator] 🎭 Tri-Agent System Initialized")
        print(f"  Workspace: {workspace_id}")
        print(f"  Agent 1: Coder (primary executor)")
        print(f"  Agent 2: Improver/Backup (helper)")
        print(f"  Agent 3: Doctor (arbitrator)")

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using the tri-agent system.
        Automatically spawns additional teams if needed.
        """
        print(f"\n{'='*60}")
        print(f"📋 NEW TASK: {task.get('description', 'Unnamed task')}")
        print(f"{'='*60}\n")

        # Step 1: Check if we need to spawn additional teams
        spawned_teams = self.spawner.spawn_for_task(task, self.agent1.agent_id)

        if spawned_teams:
            print(f"\n🧬 Spawned {len(spawned_teams)} additional teams")
            for team_id in spawned_teams:
                print(f"  - {team_id}")

        # Step 2: Agent 1 starts working
        print(f"\n[Agent 1] 🚀 Starting work...")
        self.agent1.start_task(task.get("description", "Task"))

        # Add user context
        if "user_input" in task:
            self.memory.add_user_context("user_input", task["user_input"])

        if "user_docs" in task:
            self.memory.add_user_context("user_docs", task["user_docs"])

        # Step 3: Agent 2 monitors
        print(f"[Agent 2] 👀 Monitoring Agent 1...")
        self.agent2.monitor_and_assist()

        # Step 4: Agent 3 checks system health
        needs_intervention = self.agent3.monitor_health()

        # Simulate work
        result = {
            "task": task.get("description"),
            "status": "in_progress",
            "agents": {
                "agent1": self.agent1.get_status(),
                "agent2": self.agent2.get_status(),
                "agent3": self.agent3.get_status()
            },
            "spawned_teams": spawned_teams
        }

        return result

    def handle_agent1_stuck(self, error: str):
        """
        Agent 1 hit a wall. Orchestrate rescue.
        """
        print(f"\n{'='*60}")
        print(f"⚠️  AGENT 1 STUCK: {error}")
        print(f"{'='*60}\n")

        # Step 1: Agent 2 tries to help
        print(f"[Agent 2] 🔧 Stepping in to help...")
        solution = self.agent2.help_with_bug(0)

        if solution:
            print(f"[Agent 2] ✅ Solution found: {solution}")
            return

        # Step 2: If Agent 2 can't solve it, escalate to Agent 3
        print(f"[Agent 3] 🏥 Escalating to Doctor...")
        cure = self.agent3.cure_bug(0, deep_fix=True)

        if cure["success"]:
            print(f"[Agent 3] 💉 Bug cured!")

    def handle_dispute(self, agent1_position: str, agent2_position: str):
        """
        Agent 1 and Agent 2 disagree. Agent 3 arbitrates.
        """
        print(f"\n{'='*60}")
        print(f"⚖️  DISPUTE DETECTED")
        print(f"{'='*60}\n")

        decision = self.agent3.settle_dispute(
            agent1_position=agent1_position,
            agent2_position=agent2_position,
            context="Implementation approach"
        )

        return decision

    def agent1_takes_break(self):
        """
        Agent 1 needs a break. Agent 2 substitutes.
        """
        print(f"\n{'='*60}")
        print(f"🔄 AGENT ROTATION")
        print(f"{'='*60}\n")

        self.agent1.take_break()
        self.agent2.substitute_for_agent1(self.agent1.current_task)

        # Simulate break
        print(f"[System] ⏰ Agent 1 resting for 5 minutes...")

        # Agent 1 returns
        self.agent1.resume()
        self.agent2.step_back()

    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "workspace_id": self.workspace_id,
            "agents": {
                "agent1": self.agent1.get_status(),
                "agent2": self.agent2.get_status(),
                "agent3": self.agent3.get_status()
            },
            "spawned_teams": self.spawner.get_all_spawned_teams(),
            "health": self.agent3.diagnose_system()
        }

    def run_demo(self):
        """
        Run a complete demonstration of the tri-agent system
        """
        print("\n" + "="*60)
        print("🎭 TRI-AGENT SYSTEM DEMO")
        print("="*60)

        # Demo task 1: Simple task (no spawning)
        simple_task = {
            "description": "Fix typo in README",
            "subtasks": ["Find typo", "Fix it"],
            "estimated_hours": 0.5,
            "difficulty": "low",
            "user_input": "The README has a typo in line 42",
            "user_docs": "Follow the style guide"
        }

        print(f"\n\n{'#'*60}")
        print(f"# DEMO 1: Simple Task (No Spawning)")
        print(f"{'#'*60}")
        result1 = self.execute_task(simple_task)

        # Demo task 2: Agent 1 gets stuck
        print(f"\n\n{'#'*60}")
        print(f"# DEMO 2: Agent 1 Hits a Wall")
        print(f"{'#'*60}")
        self.handle_agent1_stuck("TypeError: unsupported operand type")

        # Demo task 3: Dispute between agents
        print(f"\n\n{'#'*60}")
        print(f"# DEMO 3: Agent Dispute")
        print(f"{'#'*60}")
        self.handle_dispute(
            agent1_position="Use async/await for better performance",
            agent2_position="Use sync code for better reliability"
        )

        # Demo task 4: Agent 1 takes break
        print(f"\n\n{'#'*60}")
        print(f"# DEMO 4: Agent Rotation")
        print(f"{'#'*60}")
        self.agent1_takes_break()

        # Demo task 5: Complex task (spawning)
        complex_task = {
            "description": "Build complete microservices architecture",
            "subtasks": [
                "Design API gateway",
                "Build auth service",
                "Build user service",
                "Build payment service",
                "Setup monitoring",
                "Deploy to K8s"
            ],
            "estimated_hours": 24,
            "dependencies": ["Docker", "Kubernetes", "PostgreSQL"],
            "difficulty": "high",
            "user_input": "We need a scalable microservices setup",
            "user_docs": "Follow 12-factor app principles"
        }

        print(f"\n\n{'#'*60}")
        print(f"# DEMO 5: Complex Task (Boyle's Law - Spawning)")
        print(f"{'#'*60}")
        result2 = self.execute_task(complex_task)

        # Final status
        print(f"\n\n{'='*60}")
        print(f"📊 FINAL SYSTEM STATUS")
        print(f"{'='*60}")
        status = self.get_system_status()
        print(f"\nAgent 1: {status['agents']['agent1']['role']} - {status['agents']['agent1']['state']}")
        print(f"Agent 2: {status['agents']['agent2']['role']} - {status['agents']['agent2']['state']}")
        print(f"Agent 3: {status['agents']['agent3']['role']} - {status['agents']['agent3']['interventions_count']} interventions")
        print(f"\nSpawned Teams: {len(status['spawned_teams'])}")

        print(f"\n{'='*60}")
        print(f"✅ DEMO COMPLETE")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # Run demonstration
    orchestrator = TriAgentOrchestrator("demo_workspace")
    orchestrator.run_demo()

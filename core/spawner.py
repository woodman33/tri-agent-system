"""
Dynamic Agent Spawner - Boyle's Law Implementation
"Gas expands to fill its container" - Agents spawn to fill task complexity

When task complexity increases, spawn additional tri-agent teams.
Each spawned team is a complete tri-agent system.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.memory import SharedMemory
from typing import List, Dict, Any, Optional
import uuid
import json
from datetime import datetime


class TriAgentSpawner:
    """
    Dynamically spawns tri-agent teams based on task complexity.
    Implements "Boyle's Law" - expand to fill the container.
    """

    def __init__(self, workspace_id: str = "default"):
        self.workspace_id = workspace_id
        self.memory = SharedMemory(workspace_id)
        self.spawned_teams: List[str] = []
        self.max_teams = 10  # Safety limit

    def assess_task_complexity(self, task: Dict[str, Any]) -> int:
        """
        Analyze task and determine how many tri-agent teams needed.

        Returns: number of additional teams to spawn (0 = no spawn needed)
        """
        complexity_score = 0

        # Factor 1: Subtask count
        subtasks = task.get("subtasks", [])
        complexity_score += len(subtasks)

        # Factor 2: Estimated duration
        duration_hours = task.get("estimated_hours", 0)
        if duration_hours > 8:
            complexity_score += 2
        elif duration_hours > 4:
            complexity_score += 1

        # Factor 3: Dependencies
        dependencies = task.get("dependencies", [])
        complexity_score += len(dependencies)

        # Factor 4: Technical difficulty
        difficulty = task.get("difficulty", "medium")
        if difficulty == "high":
            complexity_score += 3
        elif difficulty == "medium":
            complexity_score += 1

        # Calculate number of teams needed
        # 0-3: Single team (original tri-agent)
        # 4-7: Spawn 1 additional team
        # 8-12: Spawn 2 additional teams
        # 13+: Spawn 3 additional teams

        if complexity_score <= 3:
            return 0
        elif complexity_score <= 7:
            return 1
        elif complexity_score <= 12:
            return 2
        else:
            return 3

    def spawn_tri_agent_team(
        self,
        task: str,
        parent_agent_id: str,
        team_workspace: Optional[str] = None
    ) -> str:
        """
        Spawn a complete tri-agent team for a specific task.

        Returns: spawned_team_id
        """
        if len(self.spawned_teams) >= self.max_teams:
            print(f"[Spawner] ⚠️  Max teams reached ({self.max_teams}). Not spawning.")
            return None

        # Generate unique team ID
        team_id = f"team_{uuid.uuid4().hex[:8]}"
        team_workspace = team_workspace or f"{self.workspace_id}_{team_id}"

        # Register in shared memory
        self.memory.register_spawned_agent(
            parent_id=parent_agent_id,
            spawned_id=team_id,
            task=task
        )

        # Create team directory
        team_dir = Path(__file__).parent.parent / "spawned" / team_id
        team_dir.mkdir(parents=True, exist_ok=True)

        # Create team config
        team_config = {
            "team_id": team_id,
            "parent_workspace": self.workspace_id,
            "workspace": team_workspace,
            "task": task,
            "spawned_at": datetime.now().isoformat(),
            "spawned_by": parent_agent_id,
            "agents": {
                "agent1_coder": {"status": "active"},
                "agent2_improver": {"status": "monitoring"},
                "agent3_doctor": {"status": "standby"}
            }
        }

        config_file = team_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(team_config, f, indent=2)

        self.spawned_teams.append(team_id)

        self.memory.log(
            "spawner",
            f"Spawned tri-agent team {team_id} for task: {task}"
        )

        print(f"[Spawner] 🧬 Spawned Team: {team_id}")
        print(f"  Task: {task}")
        print(f"  Workspace: {team_workspace}")

        return team_id

    def spawn_for_task(self, task: Dict[str, Any], parent_agent_id: str) -> List[str]:
        """
        Analyze task and spawn appropriate number of teams.
        Implements Boyle's Law - expand to fill complexity.

        Returns: list of spawned team IDs
        """
        teams_needed = self.assess_task_complexity(task)

        if teams_needed == 0:
            print(f"[Spawner] ✅ Task complexity low. Original tri-agent sufficient.")
            return []

        print(f"[Spawner] 📊 Task complexity requires {teams_needed} additional teams")

        spawned_ids = []

        # Spawn teams in parallel
        for i in range(teams_needed):
            subtask = task.get("subtasks", [f"Subtask {i+1}"])[i] if i < len(task.get("subtasks", [])) else f"Parallel work {i+1}"

            team_id = self.spawn_tri_agent_team(
                task=subtask,
                parent_agent_id=parent_agent_id
            )

            if team_id:
                spawned_ids.append(team_id)

        return spawned_ids

    def check_team_status(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Check status of spawned team"""
        team_dir = Path(__file__).parent.parent / "spawned" / team_id
        config_file = team_dir / "config.json"

        if not config_file.exists():
            return None

        with open(config_file, 'r') as f:
            return json.load(f)

    def terminate_team(self, team_id: str):
        """Terminate a spawned team when task complete"""
        self.memory.log(
            "spawner",
            f"Terminating tri-agent team {team_id}"
        )

        if team_id in self.spawned_teams:
            self.spawned_teams.remove(team_id)

        print(f"[Spawner] 💀 Terminated Team: {team_id}")

    def get_all_spawned_teams(self) -> List[Dict[str, Any]]:
        """Get status of all spawned teams"""
        return self.memory.get_spawned_agents()

    def demonstrate_boyles_law(self):
        """
        Demonstrate Boyle's Law principle:
        As task complexity increases, agents expand to fill it.
        """
        print("\n" + "="*60)
        print("🧪 DEMONSTRATING BOYLE'S LAW FOR AGENTS")
        print("="*60)

        tasks = [
            {
                "name": "Simple bug fix",
                "subtasks": ["Fix typo"],
                "estimated_hours": 0.5,
                "difficulty": "low"
            },
            {
                "name": "Medium feature",
                "subtasks": ["Design", "Implement", "Test"],
                "estimated_hours": 6,
                "difficulty": "medium"
            },
            {
                "name": "Complex refactor",
                "subtasks": ["Analyze", "Plan", "Refactor core", "Refactor modules", "Test", "Deploy"],
                "estimated_hours": 16,
                "dependencies": ["Database", "API", "Frontend"],
                "difficulty": "high"
            }
        ]

        for task in tasks:
            print(f"\n📦 Task: {task['name']}")
            teams_needed = self.assess_task_complexity(task)
            print(f"   Complexity Score: {self.assess_task_complexity(task)}")
            print(f"   Teams Needed: {teams_needed + 1} (1 original + {teams_needed} spawned)")

            if teams_needed > 0:
                print(f"   🧬 Spawning {teams_needed} additional teams...")
                print(f"   💨 Agents expand to fill the complexity container!")


if __name__ == "__main__":
    # Test spawner
    spawner = TriAgentSpawner("demo_workspace")

    # Demonstrate Boyle's Law
    spawner.demonstrate_boyles_law()

    # Spawn team for complex task
    print("\n" + "="*60)
    print("🚀 SPAWNING TEAMS FOR REAL TASK")
    print("="*60)

    complex_task = {
        "name": "Build microservices architecture",
        "subtasks": [
            "Design API gateway",
            "Build auth service",
            "Build user service",
            "Build payment service",
            "Setup monitoring"
        ],
        "estimated_hours": 20,
        "dependencies": ["Docker", "K8s", "PostgreSQL"],
        "difficulty": "high"
    }

    spawned = spawner.spawn_for_task(complex_task, "agent1_coder")
    print(f"\n✅ Spawned {len(spawned)} teams: {spawned}")

    # Check status
    print("\n📊 All Spawned Teams:")
    for team in spawner.get_all_spawned_teams():
        print(f"  - {team['spawned_id']}: {team['task']}")

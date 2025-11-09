"""
Agent 2: The Improver/Backup
- Suggests improvements
- Helps when Agent 1 hits a wall or bug
- Can substitute for Agent 1 (give it a break)
- Reads logs to understand context
- Support and backup role
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.memory import SharedMemory
from typing import Optional, Dict, Any, List


class Agent2Improver:
    """
    The improvement and backup agent.
    Monitors Agent 1, suggests improvements, steps in when needed.
    """

    def __init__(self, workspace_id: str = "default"):
        self.agent_id = "agent2_improver"
        self.memory = SharedMemory(workspace_id)
        self.is_substituting = False

    def read_logs(self, lines: int = 50) -> List[str]:
        """
        Agent 2 CAN read logs (unlike Agent 1).
        Uses logs to understand what's happening.
        """
        return self.memory.read_logs(lines)

    def check_agent1_status(self) -> Dict[str, Any]:
        """Monitor Agent 1's status"""
        return self.memory.get_agent_state("agent1_coder")

    def suggest_improvement(self, code: str, context: str) -> Dict[str, str]:
        """
        Analyze code and suggest improvements.
        """
        self.memory.log(
            self.agent_id,
            f"Analyzing code for improvements: {context}"
        )

        # Simulate analysis (in real implementation, use LLM)
        suggestions = {
            "code_quality": "Consider adding type hints for better maintainability",
            "performance": "Consider using itertools for better performance",
            "error_handling": "Add try-catch blocks for edge cases",
            "documentation": "Add docstrings explaining parameters and return values"
        }

        self.memory.add_conversation(
            self.agent_id,
            "assistant",
            f"Suggested improvements: {suggestions}"
        )

        print(f"[Agent 2 - Improver] 💡 Suggestions:")
        for category, suggestion in suggestions.items():
            print(f"  - {category}: {suggestion}")

        return suggestions

    def help_with_bug(self, bug_id: int) -> Optional[str]:
        """
        Agent 1 hit a wall. Help debug and solve.
        """
        self.memory.log(
            self.agent_id,
            f"Assisting with bug #{bug_id}"
        )

        # Read logs to understand context
        recent_logs = self.read_logs(100)

        # Simulate debugging (in real implementation, analyze logs and code)
        solution = f"Debug solution for bug #{bug_id}: Check input validation and edge cases"

        self.memory.add_solution(self.agent_id, bug_id, solution)

        print(f"[Agent 2 - Improver] 🔧 Helping with bug #{bug_id}")
        print(f"  Solution: {solution}")

        return solution

    def substitute_for_agent1(self, task: str):
        """
        Agent 1 needs a break. Agent 2 takes over.
        """
        self.is_substituting = True

        self.memory.update_agent_state(
            self.agent_id,
            status="substituting",
            task=task
        )

        self.memory.log(
            self.agent_id,
            f"Substituting for Agent 1 on task: {task}"
        )

        print(f"[Agent 2 - Improver] 🔄 Substituting for Agent 1")
        print(f"  Task: {task}")

    def step_back(self):
        """Agent 1 is back, return to support role"""
        self.is_substituting = False

        self.memory.update_agent_state(
            self.agent_id,
            status="monitoring",
            task=None
        )

        self.memory.log(self.agent_id, "Agent 1 resumed. Returning to support role.")
        print(f"[Agent 2 - Improver] ✅ Agent 1 is back. Returning to monitoring.")

    def monitor_and_assist(self):
        """
        Continuous monitoring loop.
        Watch Agent 1, offer help when needed.
        """
        agent1_status = self.check_agent1_status()

        # Check if Agent 1 needs help
        if agent1_status.get("status") == "coding":
            # Read logs to see if there are issues
            logs = self.read_logs(20)

            # Look for warning/error patterns
            issues_found = [log for log in logs if "WARNING" in log or "ERROR" in log]

            if issues_found:
                print(f"[Agent 2 - Improver] 👀 Detected {len(issues_found)} potential issues")

        # Check if Agent 1 is resting
        elif agent1_status.get("status") == "resting":
            task = agent1_status.get("current_task")
            if task and not self.is_substituting:
                self.substitute_for_agent1(task)

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "agent_id": self.agent_id,
            "role": "Improver/Backup",
            "is_substituting": self.is_substituting,
            "state": self.memory.get_agent_state(self.agent_id)
        }


if __name__ == "__main__":
    # Test Agent 2
    agent2 = Agent2Improver("test_workspace")

    # Monitor Agent 1
    agent1_status = agent2.check_agent1_status()
    print(f"Agent 1 Status: {agent1_status}")

    # Suggest improvement
    code = "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)"
    agent2.suggest_improvement(code, "Fibonacci implementation")

    # Help with bug
    agent2.help_with_bug(0)

    print(f"\nStatus: {agent2.get_status()}")

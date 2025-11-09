"""
Agent 1: The Coder
- Primary executor
- Focused ONLY on: user context, user input, user docs, and coding
- Does NOT read logs (stays focused on forward momentum)
- Main driver of development
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.memory import SharedMemory
from typing import Optional, Dict, Any


class Agent1Coder:
    """
    The primary coding agent.
    Stays laser-focused on user requirements and implementation.
    """

    def __init__(self, workspace_id: str = "default"):
        self.agent_id = "agent1_coder"
        self.memory = SharedMemory(workspace_id)
        self.current_task = None
        self.needs_help = False

    def focus_on_user_context(self) -> Dict[str, Any]:
        """
        Agent 1's primary focus: user input, docs, and context.
        Does NOT read logs - stays forward-focused.
        """
        context = self.memory.get_user_context()
        return {
            "user_input": context.get("user_input", []),
            "user_docs": context.get("user_docs", []),
            "codebase_context": context.get("codebase_context", [])
        }

    def start_task(self, task_description: str):
        """Begin working on a task"""
        self.current_task = task_description
        self.needs_help = False

        # Update shared state
        self.memory.update_agent_state(
            self.agent_id,
            status="coding",
            task=task_description
        )

        # Add to conversation
        self.memory.add_conversation(
            self.agent_id,
            "system",
            f"Starting task: {task_description}"
        )

        print(f"[Agent 1 - Coder] 🚀 Starting: {task_description}")

    def execute_code(self, code: str, description: str) -> Dict[str, Any]:
        """
        Execute coding task.
        Returns result or signals need for help.
        """
        self.memory.log(self.agent_id, f"Executing: {description}")

        try:
            # Simulate code execution (in real implementation, this would use tools)
            result = {
                "success": True,
                "code": code,
                "description": description,
                "output": "Code executed successfully"
            }

            self.memory.add_conversation(
                self.agent_id,
                "assistant",
                f"Completed: {description}"
            )

            return result

        except Exception as e:
            # Hit a wall - signal for help
            self.needs_help = True
            self.memory.add_bug(
                self.agent_id,
                bug_description=str(e),
                context={
                    "task": self.current_task,
                    "code": code,
                    "description": description
                }
            )

            self.memory.log(
                self.agent_id,
                f"Hit a wall: {str(e)}. Requesting Agent 2 assistance.",
                level="WARNING"
            )

            return {
                "success": False,
                "error": str(e),
                "needs_help": True
            }

    def take_break(self):
        """
        Agent 1 takes a break, Agent 2 will substitute.
        """
        self.memory.update_agent_state(
            self.agent_id,
            status="resting",
            task=None
        )

        self.memory.log(
            self.agent_id,
            "Taking a break. Agent 2 will substitute.",
            level="INFO"
        )

        print(f"[Agent 1 - Coder] 😴 Taking a break...")

    def resume(self):
        """Resume after break"""
        self.memory.update_agent_state(
            self.agent_id,
            status="active",
            task=self.current_task
        )

        self.memory.log(self.agent_id, "Resumed coding")
        print(f"[Agent 1 - Coder] 💪 Back to work!")

    def check_if_needs_help(self) -> bool:
        """Check if agent needs assistance"""
        return self.needs_help

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "agent_id": self.agent_id,
            "role": "Coder",
            "current_task": self.current_task,
            "needs_help": self.needs_help,
            "state": self.memory.get_agent_state(self.agent_id)
        }


if __name__ == "__main__":
    # Test Agent 1
    agent1 = Agent1Coder("test_workspace")

    # Add user context
    agent1.memory.add_user_context("user_input", "Build a function to calculate fibonacci")
    agent1.memory.add_user_context("user_docs", "Use recursive approach with memoization")

    # Start task
    agent1.start_task("Implement fibonacci function")

    # Execute code
    code = """
def fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
    return memo[n]
"""

    result = agent1.execute_code(code, "Fibonacci function with memoization")
    print(f"\nResult: {result}")
    print(f"\nStatus: {agent1.get_status()}")

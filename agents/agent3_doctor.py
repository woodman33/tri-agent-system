"""
Agent 3: The Doctor
- Rarely codes
- Settles disputes between Agent 1 and Agent 2
- Cures bugs for both agents
- Can do simple commands to fix or get out of trouble
- Reads logs for deep diagnosis
- Arbitrator and debugger role
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.memory import SharedMemory
from typing import Optional, Dict, Any, List


class Agent3Doctor:
    """
    The doctor and arbitrator.
    Rarely codes, but fixes critical issues and settles disputes.
    """

    def __init__(self, workspace_id: str = "default"):
        self.agent_id = "agent3_doctor"
        self.memory = SharedMemory(workspace_id)
        self.interventions = 0

    def read_logs(self, lines: int = 200) -> List[str]:
        """
        Agent 3 reads logs extensively for diagnosis.
        Deeper log analysis than Agent 2.
        """
        return self.memory.read_logs(lines)

    def diagnose_system(self) -> Dict[str, Any]:
        """
        Deep system diagnosis.
        Analyze all agent states and logs.
        """
        self.memory.log(self.agent_id, "Running system diagnosis")

        agent1_state = self.memory.get_agent_state("agent1_coder")
        agent2_state = self.memory.get_agent_state("agent2_improver")
        logs = self.read_logs(200)

        # Analyze for critical issues
        errors = [log for log in logs if "ERROR" in log]
        warnings = [log for log in logs if "WARNING" in log]

        diagnosis = {
            "agent1_status": agent1_state.get("status"),
            "agent2_status": agent2_state.get("status"),
            "errors_count": len(errors),
            "warnings_count": len(warnings),
            "health": "critical" if len(errors) > 5 else "warning" if len(warnings) > 10 else "healthy"
        }

        print(f"[Agent 3 - Doctor] 🏥 System Diagnosis:")
        print(f"  Agent 1: {diagnosis['agent1_status']}")
        print(f"  Agent 2: {diagnosis['agent2_status']}")
        print(f"  Errors: {diagnosis['errors_count']}")
        print(f"  Warnings: {diagnosis['warnings_count']}")
        print(f"  Health: {diagnosis['health']}")

        return diagnosis

    def settle_dispute(self, agent1_position: str, agent2_position: str, context: str) -> Dict[str, str]:
        """
        Agent 1 and Agent 2 disagree. Agent 3 makes the final call.
        """
        self.memory.log(
            self.agent_id,
            f"Settling dispute. Context: {context}"
        )

        # Analyze both positions
        print(f"[Agent 3 - Doctor] ⚖️  Settling Dispute:")
        print(f"  Agent 1 Position: {agent1_position}")
        print(f"  Agent 2 Position: {agent2_position}")
        print(f"  Context: {context}")

        # Make final decision (in real implementation, use deep reasoning)
        decision = f"Decision: Both agents have valid points. Proceeding with Agent 1's approach but incorporating Agent 2's safety checks."
        reasoning = "Agent 1's approach is more aligned with user requirements, but Agent 2's caution about edge cases is warranted."

        self.memory.add_decision(
            self.agent_id,
            decision=decision,
            reasoning=reasoning
        )

        print(f"  🏛️  Final Decision: {decision}")
        print(f"  📝 Reasoning: {reasoning}")

        return {
            "decision": decision,
            "reasoning": reasoning
        }

    def cure_bug(self, bug_id: int, deep_fix: bool = True) -> Dict[str, Any]:
        """
        Agent 3's bug cure - more thorough than Agent 2's help.
        Can execute simple commands to fix issues.
        """
        self.memory.log(
            self.agent_id,
            f"Curing bug #{bug_id} (deep_fix={deep_fix})"
        )

        # Read extensive logs for context
        logs = self.read_logs(300)

        # Deep analysis
        print(f"[Agent 3 - Doctor] 💉 Curing Bug #{bug_id}")

        # Simulate bug cure (in real implementation, execute fix commands)
        fix_commands = [
            "Reset agent state",
            "Clear corrupted cache",
            "Restore from last known good state",
            "Apply emergency patch"
        ]

        cure = {
            "bug_id": bug_id,
            "diagnosis": "Root cause: race condition in shared memory access",
            "treatment": fix_commands,
            "success": True,
            "prevention": "Add mutex locks to shared memory operations"
        }

        # Record the cure
        self.memory.add_solution(
            self.agent_id,
            bug_id,
            f"Deep cure: {cure['diagnosis']}. Treatment: {', '.join(fix_commands)}"
        )

        self.interventions += 1

        print(f"  Diagnosis: {cure['diagnosis']}")
        print(f"  Treatment:")
        for cmd in fix_commands:
            print(f"    - {cmd}")
        print(f"  Prevention: {cure['prevention']}")

        return cure

    def execute_emergency_command(self, command: str, reason: str) -> Dict[str, Any]:
        """
        Execute simple emergency commands to get system out of trouble.
        Agent 3's special ability to directly intervene.
        """
        self.memory.log(
            self.agent_id,
            f"EMERGENCY: Executing '{command}'. Reason: {reason}",
            level="WARNING"
        )

        print(f"[Agent 3 - Doctor] 🚨 EMERGENCY INTERVENTION")
        print(f"  Command: {command}")
        print(f"  Reason: {reason}")

        # Execute (in real implementation, this would run actual commands)
        result = {
            "command": command,
            "reason": reason,
            "executed": True,
            "output": f"Emergency command executed successfully"
        }

        self.memory.add_conversation(
            self.agent_id,
            "system",
            f"Emergency intervention: {command}"
        )

        return result

    def monitor_health(self) -> bool:
        """
        Continuous health monitoring.
        Returns True if intervention needed.
        """
        diagnosis = self.diagnose_system()

        # Check if intervention needed
        if diagnosis["health"] == "critical":
            print(f"[Agent 3 - Doctor] 🚨 CRITICAL: Intervention required!")
            return True

        elif diagnosis["health"] == "warning":
            print(f"[Agent 3 - Doctor] ⚠️  WARNING: Elevated risk")
            return False

        else:
            # System healthy, stay in background
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "agent_id": self.agent_id,
            "role": "Doctor/Arbitrator",
            "interventions_count": self.interventions,
            "state": self.memory.get_agent_state(self.agent_id)
        }


if __name__ == "__main__":
    # Test Agent 3
    agent3 = Agent3Doctor("test_workspace")

    # Run diagnosis
    diagnosis = agent3.diagnose_system()

    # Settle a dispute
    agent3.settle_dispute(
        agent1_position="Use recursion for clarity",
        agent2_position="Use iteration for performance",
        context="Fibonacci implementation strategy"
    )

    # Cure a bug
    agent3.cure_bug(0, deep_fix=True)

    # Emergency intervention
    agent3.execute_emergency_command(
        command="kill -9 <stuck_process>",
        reason="Agent 1 stuck in infinite loop"
    )

    print(f"\nStatus: {agent3.get_status()}")

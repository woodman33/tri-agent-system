"""
Shared Memory System for Tri-Agent
All 3 agents share the same memory and logs
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading


class SharedMemory:
    """Thread-safe shared memory for tri-agent system"""

    def __init__(self, workspace_id: str = "default"):
        self.workspace_id = workspace_id
        self.base_dir = Path(__file__).parent.parent / "shared" / workspace_id
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.memory_file = self.base_dir / "memory.json"
        self.log_file = self.base_dir / "tri_agent.log"
        self.context_file = self.base_dir / "context.json"

        self.lock = threading.Lock()
        self._initialize_memory()

    def _initialize_memory(self):
        """Initialize memory file if it doesn't exist"""
        if not self.memory_file.exists():
            initial_memory = {
                "created_at": datetime.now().isoformat(),
                "workspace_id": self.workspace_id,
                "conversation_history": [],
                "decisions": [],
                "bugs_encountered": [],
                "solutions": [],
                "agent_states": {
                    "agent1_coder": {"status": "idle", "current_task": None},
                    "agent2_improver": {"status": "idle", "current_task": None},
                    "agent3_doctor": {"status": "idle", "current_task": None}
                },
                "spawned_agents": []
            }
            self._write_json(self.memory_file, initial_memory)

        if not self.context_file.exists():
            initial_context = {
                "user_input": [],
                "user_docs": [],
                "codebase_context": []
            }
            self._write_json(self.context_file, initial_context)

    def _read_json(self, file_path: Path) -> Dict:
        """Thread-safe JSON read"""
        with self.lock:
            with open(file_path, 'r') as f:
                return json.load(f)

    def _write_json(self, file_path: Path, data: Dict):
        """Thread-safe JSON write"""
        with self.lock:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

    def log(self, agent_id: str, message: str, level: str = "INFO"):
        """Write to shared log file (Agents 2 & 3 can read, Agent 1 ignores)"""
        with self.lock:
            with open(self.log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"[{timestamp}] [{agent_id}] {level}: {message}\n")

    def add_conversation(self, agent_id: str, role: str, content: str):
        """Add to conversation history"""
        memory = self._read_json(self.memory_file)
        memory["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "role": role,
            "content": content
        })
        self._write_json(self.memory_file, memory)

    def add_decision(self, agent_id: str, decision: str, reasoning: str):
        """Record decision (used by Agent 3 for disputes)"""
        memory = self._read_json(self.memory_file)
        memory["decisions"].append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "decision": decision,
            "reasoning": reasoning
        })
        self._write_json(self.memory_file, memory)

    def add_bug(self, agent_id: str, bug_description: str, context: Dict):
        """Record bug encounter"""
        memory = self._read_json(self.memory_file)
        memory["bugs_encountered"].append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "description": bug_description,
            "context": context,
            "resolved": False
        })
        self._write_json(self.memory_file, memory)

    def add_solution(self, agent_id: str, bug_id: int, solution: str):
        """Record bug solution"""
        memory = self._read_json(self.memory_file)
        memory["solutions"].append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "bug_id": bug_id,
            "solution": solution
        })
        # Mark bug as resolved
        if bug_id < len(memory["bugs_encountered"]):
            memory["bugs_encountered"][bug_id]["resolved"] = True
        self._write_json(self.memory_file, memory)

    def update_agent_state(self, agent_id: str, status: str, task: Optional[str] = None):
        """Update agent state"""
        memory = self._read_json(self.memory_file)
        memory["agent_states"][agent_id] = {
            "status": status,
            "current_task": task,
            "updated_at": datetime.now().isoformat()
        }
        self._write_json(self.memory_file, memory)

    def get_agent_state(self, agent_id: str) -> Dict:
        """Get agent state"""
        memory = self._read_json(self.memory_file)
        return memory["agent_states"].get(agent_id, {})

    def add_user_context(self, context_type: str, content: str):
        """Add user input/docs (only Agent 1 uses this)"""
        context = self._read_json(self.context_file)
        context[context_type].append({
            "timestamp": datetime.now().isoformat(),
            "content": content
        })
        self._write_json(self.context_file, context)

    def get_user_context(self) -> Dict:
        """Get all user context (Agent 1 focused on this)"""
        return self._read_json(self.context_file)

    def read_logs(self, lines: int = 100) -> List[str]:
        """Read recent logs (Agents 2 & 3 use this)"""
        if not self.log_file.exists():
            return []
        with open(self.log_file, 'r') as f:
            return f.readlines()[-lines:]

    def register_spawned_agent(self, parent_id: str, spawned_id: str, task: str):
        """Register a dynamically spawned agent"""
        memory = self._read_json(self.memory_file)
        memory["spawned_agents"].append({
            "timestamp": datetime.now().isoformat(),
            "parent_id": parent_id,
            "spawned_id": spawned_id,
            "task": task,
            "status": "active"
        })
        self._write_json(self.memory_file, memory)

    def get_spawned_agents(self) -> List[Dict]:
        """Get all spawned agents"""
        memory = self._read_json(self.memory_file)
        return memory.get("spawned_agents", [])

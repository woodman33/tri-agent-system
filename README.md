# Tri-Agent System 🎭

**Self-coordinating 3-agent team with dynamic spawning capability**

## 🎯 Concept

The Tri-Agent System is a self-managing team of three specialized agents that work together, share memory, and can spawn additional teams when complexity increases.

### The Three Agents

1. **Agent 1 - The Coder** 💻
   - Primary executor
   - Focused ONLY on: user context, user input, user docs, and coding
   - Does NOT read logs (stays forward-focused)
   - Main driver of development

2. **Agent 2 - The Improver/Backup** 🔧
   - Suggests improvements
   - Helps when Agent 1 hits a wall or bug
   - Can substitute for Agent 1 (give it a break)
   - Reads logs to understand context
   - Support and backup role

3. **Agent 3 - The Doctor** 🏥
   - Rarely codes
   - Settles disputes between Agent 1 and Agent 2
   - Cures bugs for both agents
   - Can execute simple commands to fix or get out of trouble
   - Reads logs for deep diagnosis
   - Arbitrator and debugger role

### Key Features

- **Shared Memory**: All 3 agents share the same memory file and logs
- **Role Separation**:
  - Agent 1: Only reads user context (not logs)
  - Agents 2 & 3: Read logs and monitor Agent 1
- **Dynamic Spawning**: Implements "Boyle's Law" - agents expand to fill complexity
- **Reproducible**: Template system for creating multiple instances

## 🧬 Boyle's Law for Agents

> "Gas expands to fill its container"

When task complexity increases, the system automatically spawns additional tri-agent teams:

- **Simple tasks** (0-3 complexity): Single tri-agent team
- **Medium tasks** (4-7 complexity): 1 additional team spawned
- **Complex tasks** (8-12 complexity): 2 additional teams spawned
- **Very complex tasks** (13+ complexity): 3 additional teams spawned

Complexity calculated from:
- Number of subtasks
- Estimated duration
- Dependencies
- Technical difficulty

## 📂 Structure

```
tri-agent-system/
├── agents/                    # The 3 core agents
│   ├── agent1_coder.py       # Primary executor
│   ├── agent2_improver.py    # Helper & backup
│   └── agent3_doctor.py      # Doctor & arbitrator
├── core/                      # Core system
│   ├── orchestrator.py       # Coordinates the 3 agents
│   └── spawner.py            # Dynamic team spawning
├── shared/                    # Shared resources
│   ├── memory.py             # Shared memory system
│   └── <workspace_id>/       # Per-workspace data
│       ├── memory.json       # Shared memory
│       ├── context.json      # User context
│       └── tri_agent.log     # Shared logs
├── templates/                 # Template generator
│   └── template_generator.py # Create new instances
└── spawned/                   # Dynamically spawned teams
    └── team_<id>/            # Each spawned team
```

## 🚀 Quick Start

### 1. Run the Demo

```bash
cd ~/multiagent-frameworks/tri-agent-system
export PATH="/Users/willmeldman/.local/bin:$PATH"
cd ~/multiagent-frameworks && poetry run python tri-agent-system/core/orchestrator.py
```

This will demonstrate:
- Simple task execution
- Agent 1 hitting a wall (Agent 2 helps)
- Dispute resolution (Agent 3 arbitrates)
- Agent rotation (Agent 2 substitutes)
- Complex task (Boyle's law spawning)

### 2. Create a New Tri-Agent Instance

```bash
cd ~/multiagent-frameworks/tri-agent-system/templates
python3 template_generator.py create --name "My Project" --description "Build something awesome"
```

This creates a complete, independent tri-agent system at `~/tri-agent-instances/my_project/`

### 3. Use in Your Code

```python
from tri-agent-system.core.orchestrator import TriAgentOrchestrator

# Create orchestrator
orchestrator = TriAgentOrchestrator("my_workspace")

# Execute task
task = {
    "description": "Build authentication system",
    "subtasks": ["Design", "Implement", "Test"],
    "estimated_hours": 8,
    "difficulty": "medium",
    "user_input": "Need OAuth and JWT support",
    "user_docs": "Follow OWASP guidelines"
}

result = orchestrator.execute_task(task)

# System automatically spawns teams if needed
print(f"Spawned teams: {result['spawned_teams']}")
```

## 🧠 How It Works

### Shared Memory

All 3 agents share:
- **Memory file**: Conversation history, decisions, bugs, solutions
- **Log file**: Real-time activity log (Agents 2 & 3 read this)
- **Context file**: User input and docs (Agent 1's focus)

```python
from shared.memory import SharedMemory

memory = SharedMemory("workspace_id")

# Agent 1 adds user context
memory.add_user_context("user_input", "Build a REST API")

# Agent 2 reads logs
logs = memory.read_logs(100)

# Agent 3 records decision
memory.add_decision("agent3_doctor", "Proceed with approach A", "Lower risk")
```

### Agent Coordination

1. **Normal Flow**:
   - Agent 1 codes based on user context
   - Agent 2 monitors and suggests improvements
   - Agent 3 stays in background, monitoring health

2. **Agent 1 Stuck**:
   - Agent 2 steps in to help
   - If Agent 2 can't solve it → escalate to Agent 3
   - Agent 3 performs deep diagnosis and cure

3. **Dispute**:
   - Agent 1 and Agent 2 disagree on approach
   - Agent 3 analyzes both positions
   - Agent 3 makes final binding decision

4. **Agent 1 Tired**:
   - Agent 1 takes a break
   - Agent 2 substitutes and continues work
   - Agent 1 resumes when ready

### Dynamic Spawning

When complexity threshold is exceeded:

```python
from core.spawner import TriAgentSpawner

spawner = TriAgentSpawner("workspace")

# Assess task
teams_needed = spawner.assess_task_complexity(task)

# Spawn teams
for i in range(teams_needed):
    team_id = spawner.spawn_tri_agent_team(
        task=f"Subtask {i}",
        parent_agent_id="agent1_coder"
    )
```

Each spawned team is a complete tri-agent system with its own:
- Agent 1 (Coder)
- Agent 2 (Improver)
- Agent 3 (Doctor)
- Shared memory

## 📖 Examples

### Example 1: Bug Fix Flow

```
1. Agent 1 encounters bug
   → Logs error to shared memory
   → Sets needs_help = True

2. Agent 2 detects issue in logs
   → Analyzes error
   → Suggests solution
   → If can't solve → escalate

3. Agent 3 receives escalation
   → Deep log analysis
   → Execute fix commands
   → Mark bug as resolved
```

### Example 2: Dispute Resolution

```
Agent 1: "Use recursion for clarity"
Agent 2: "Use iteration for performance"

Agent 3 arbitrates:
  → Analyzes both approaches
  → Considers context (performance critical vs readability)
  → Makes final decision with reasoning
  → Records decision in shared memory
```

### Example 3: Boyle's Law Spawning

```
Task: "Build microservices architecture"
- 6 subtasks
- 24 hours estimated
- 3 dependencies
- High difficulty
→ Complexity Score: 15

System spawns 3 additional tri-agent teams:
- Team 1: Auth service
- Team 2: User service
- Team 3: Payment service

Each team has its own Agent 1, 2, 3 working in parallel
```

## 🔧 Configuration

Edit `config.json` in each instance:

```json
{
  "project_name": "My Project",
  "workspace_id": "my_project",
  "agents": {
    "agent1_coder": {"enabled": true},
    "agent2_improver": {"enabled": true},
    "agent3_doctor": {"enabled": true}
  },
  "spawning": {
    "enabled": true,
    "max_teams": 10,
    "auto_spawn": true
  }
}
```

## 🧪 Testing

### Run Demo
```bash
poetry run python core/orchestrator.py
```

### Test Individual Agents
```bash
poetry run python agents/agent1_coder.py
poetry run python agents/agent2_improver.py
poetry run python agents/agent3_doctor.py
```

### Test Spawner
```bash
poetry run python core/spawner.py
```

### Test Template Generator
```bash
poetry run python templates/template_generator.py
```

## 📊 Use Cases

Perfect for:
- **Complex coding projects** - Multiple agents tackle different parts
- **Long-running tasks** - Agents can substitute and take breaks
- **Uncertain requirements** - Doctor settles disputes as they arise
- **High-reliability needs** - Doctor monitors and fixes issues
- **Scalable systems** - Spawns teams as complexity grows

## 🎯 Design Philosophy

1. **Focused Roles**: Each agent has clear responsibilities
2. **Shared Memory**: Coordination through shared state
3. **Log Separation**: Agent 1 ignores logs to stay focused
4. **Dynamic Scaling**: Spawn teams when needed (Boyle's Law)
5. **Reproducible**: Template system for easy replication

## 🚦 Status

- ✅ Shared memory system
- ✅ Agent 1 (Coder) implementation
- ✅ Agent 2 (Improver) implementation
- ✅ Agent 3 (Doctor) implementation
- ✅ Orchestrator
- ✅ Dynamic spawner (Boyle's Law)
- ✅ Template generator
- ✅ Complete demo

## 📝 License

MIT

---

## 🆘 Support

- **Email**: info@kraftforgelabs.com
- **GitHub**: [github.com/woodman33/tri-agent-system](https://github.com/woodman33/tri-agent-system)
- **Issues**: Report bugs via GitHub Issues

---

**Built with**: Python 3.10+
**Dependencies**: None (pure Python)
**Status**: Production Ready ✅

Made by **Kraftforge Labs** 🔨

# Tri-Agent System - Quick Start 🚀

## What You Built

A **self-coordinating 3-agent team** that:

1. **Agent 1 (Coder)** - Stays laser-focused on user requirements and coding
2. **Agent 2 (Improver)** - Helps, suggests improvements, can substitute
3. **Agent 3 (Doctor)** - Settles disputes, cures bugs, rarely codes

**Key Innovation**: **Boyle's Law for Agents** - "Like gas expanding to fill its container, agents spawn to fill complexity"

## 🎯 Quick Demo

```bash
cd ~/multiagent-frameworks/tri-agent-system
export PYTHONPATH="/Users/willmeldman/multiagent-frameworks/tri-agent-system:$PYTHONPATH"
poetry run python core/orchestrator.py
```

This demonstrates:
- ✅ Simple task (no spawning)
- ✅ Agent 1 stuck (Agent 2 helps)
- ✅ Dispute (Agent 3 arbitrates)
- ✅ Agent rotation (Agent 2 substitutes)
- ✅ Complex task (spawns 3 additional teams!)

## 🧬 The Magic: Dynamic Spawning

When you give it a complex task like "Build microservices architecture":

```
Task complexity score: 15 (high)
  → System spawns 3 additional tri-agent teams
  → Each team gets a subtask
  → All teams work in parallel
  → Like gas expanding to fill the container!
```

## 📦 Create Your Own Tri-Agent System

```bash
cd ~/multiagent-frameworks/tri-agent-system/templates
poetry run python template_generator.py create \
  --name "My Project" \
  --description "Build something awesome"
```

This creates a complete tri-agent system at:
`~/tri-agent-instances/my_project/`

Then:
```bash
cd ~/tri-agent-instances/my_project
./start.sh
```

## 🔧 Use in Your Code

```python
from tri_agent_system.core.orchestrator import TriAgentOrchestrator

# Create orchestrator
orchestrator = TriAgentOrchestrator("my_workspace")

# Define task
task = {
    "description": "Build authentication system",
    "subtasks": ["Design", "Implement JWT", "Add OAuth", "Test"],
    "estimated_hours": 12,
    "difficulty": "high",
    "user_input": "Need Google and GitHub OAuth",
    "user_docs": "Follow OWASP security guidelines"
}

# Execute - automatically spawns teams if needed!
result = orchestrator.execute_task(task)

# Check results
print(f"Status: {result['status']}")
print(f"Spawned teams: {len(result['spawned_teams'])}")
```

## 🧠 How Agent Roles Work

### Agent 1 - The Coder 💻
```python
from agents.agent1_coder import Agent1Coder

agent1 = Agent1Coder("workspace")
agent1.start_task("Build REST API")

# Agent 1 ONLY reads user context (not logs)
context = agent1.focus_on_user_context()
# → Returns: user_input, user_docs, codebase_context
```

**Agent 1 Focus**: User context, user input, docs, coding. Nothing else.

### Agent 2 - The Improver 🔧
```python
from agents.agent2_improver import Agent2Improver

agent2 = Agent2Improver("workspace")

# Agent 2 CAN read logs
logs = agent2.read_logs(50)

# Monitor Agent 1
agent1_status = agent2.check_agent1_status()

# Help with bug
if agent1_status["needs_help"]:
    agent2.help_with_bug(bug_id=0)

# Substitute if Agent 1 needs break
if agent1_status["status"] == "resting":
    agent2.substitute_for_agent1(task)
```

### Agent 3 - The Doctor 🏥
```python
from agents.agent3_doctor import Agent3Doctor

agent3 = Agent3Doctor("workspace")

# Run system diagnosis
diagnosis = agent3.diagnose_system()

# Settle dispute
if dispute_detected:
    decision = agent3.settle_dispute(
        agent1_position="Use recursion",
        agent2_position="Use iteration",
        context="Performance critical section"
    )

# Cure bug with deep fix
cure = agent3.cure_bug(bug_id=0, deep_fix=True)

# Emergency intervention
if critical_issue:
    agent3.execute_emergency_command(
        command="kill -9 <pid>",
        reason="Infinite loop detected"
    )
```

## 🚦 Complexity-Based Spawning

```python
from core.spawner import TriAgentSpawner

spawner = TriAgentSpawner("workspace")

# Assess complexity
task = {
    "subtasks": 6,
    "estimated_hours": 20,
    "dependencies": 3,
    "difficulty": "high"
}

teams_needed = spawner.assess_task_complexity(task)
# → Returns: 3 (spawn 3 additional teams)

# Spawn teams
spawned = spawner.spawn_for_task(task, "agent1_coder")
# → Returns: ["team_abc123", "team_def456", "team_ghi789"]
```

**Complexity Thresholds**:
- 0-3: Single team (no spawning)
- 4-7: +1 team
- 8-12: +2 teams
- 13+: +3 teams

## 📊 Shared Memory System

All 3 agents share the same memory:

```python
from shared.memory import SharedMemory

memory = SharedMemory("workspace")

# Add conversation
memory.add_conversation("agent1_coder", "user", "Build API")

# Record decision
memory.add_decision("agent3_doctor", "Use approach A", "Lower risk")

# Log bug
memory.add_bug("agent1_coder", "TypeError", {"line": 42})

# Add solution
memory.add_solution("agent3_doctor", bug_id=0, "Added type check")

# Update agent state
memory.update_agent_state("agent1_coder", status="coding", task="Build API")

# Add user context (Agent 1's focus)
memory.add_user_context("user_input", "Need OAuth support")

# Read logs (Agents 2 & 3)
logs = memory.read_logs(100)
```

## 🎭 Complete Example

```python
from core.orchestrator import TriAgentOrchestrator

# Initialize
orchestrator = TriAgentOrchestrator("production")

# Complex task
complex_task = {
    "description": "Refactor entire codebase to microservices",
    "subtasks": [
        "Analyze current monolith",
        "Design service boundaries",
        "Extract auth service",
        "Extract user service",
        "Extract payment service",
        "Add API gateway",
        "Setup service mesh",
        "Migrate database"
    ],
    "estimated_hours": 80,
    "dependencies": ["Docker", "K8s", "Istio"],
    "difficulty": "high",
    "user_input": "Need zero-downtime migration",
    "user_docs": "Follow 12-factor app principles"
}

# Execute
result = orchestrator.execute_task(complex_task)

# System automatically:
# 1. Spawns 3 additional teams (Boyle's law)
# 2. Agent 1 focuses on user requirements
# 3. Agent 2 monitors and suggests improvements
# 4. Agent 3 watches for issues

print(f"Spawned {len(result['spawned_teams'])} additional teams")
print(f"System health: {orchestrator.agent3.diagnose_system()['health']}")
```

## 🔥 Key Features

1. **Role Separation**
   - Agent 1: Only user context (NOT logs)
   - Agents 2 & 3: Read logs and memory

2. **Shared Memory**
   - All agents share same memory file
   - Thread-safe operations
   - Real-time synchronization

3. **Dynamic Spawning**
   - Automatic complexity assessment
   - Spawns additional tri-agent teams
   - "Boyle's Law" - expand to fill complexity

4. **Reproducible**
   - Template generator
   - Create unlimited instances
   - Each instance is independent

5. **Self-Managing**
   - Agent 2 helps when Agent 1 stuck
   - Agent 3 settles disputes
   - Agents can rotate and substitute

## 📁 Project Structure

```
tri-agent-system/
├── agents/              # The 3 agents
├── core/                # Orchestrator + spawner
├── shared/              # Shared memory
├── templates/           # Template generator
├── spawned/             # Dynamically spawned teams
├── README.md            # Full documentation
└── QUICKSTART.md        # This file
```

## 🎯 What's Next?

1. **Integrate with your workflow**
   - Add to CI/CD pipeline
   - Use for code reviews
   - Automate refactoring

2. **Customize agents**
   - Add LLM integration
   - Connect to your tools
   - Add custom commands

3. **Scale up**
   - Increase max_teams
   - Add more complexity factors
   - Create specialized tri-agent templates

## 💡 Pro Tips

1. **Agent 1 stays focused** - Don't make it read logs, that's Agent 2 & 3's job
2. **Let it spawn** - Don't manually create teams, let Boyle's law work
3. **Use disputes** - When agents disagree, Agent 3 makes the call
4. **Shared memory is king** - All coordination happens through shared memory
5. **Template everything** - Create tri-agent instances for each project

## 🚀 You're Ready!

You now have a self-coordinating, self-scaling, self-managing agent system that expands to fill complexity like gas filling a container.

**Boyle's Law for Agents**: The more complex the task, the more agents spawn to handle it.

Start building! 🎭

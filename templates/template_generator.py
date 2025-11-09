"""
Reproducible Tri-Agent Template Generator

Creates new tri-agent systems from template.
Users can spawn multiple independent tri-agent systems for different projects.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import shutil
import json
from datetime import datetime
from typing import Dict, Optional


class TriAgentTemplate:
    """
    Generate reproducible tri-agent systems from template.
    """

    def __init__(self):
        self.template_dir = Path(__file__).parent.parent
        self.templates_output_dir = Path.home() / "tri-agent-instances"
        self.templates_output_dir.mkdir(exist_ok=True)

    def create_new_system(
        self,
        project_name: str,
        description: str,
        custom_config: Optional[Dict] = None
    ) -> str:
        """
        Create a new tri-agent system instance.

        Args:
            project_name: Name for this tri-agent instance
            description: What this system will do
            custom_config: Optional custom configuration

        Returns:
            Path to new system
        """
        # Sanitize project name
        safe_name = project_name.lower().replace(" ", "_").replace("-", "_")
        instance_dir = self.templates_output_dir / safe_name

        if instance_dir.exists():
            print(f"⚠️  Instance '{safe_name}' already exists at {instance_dir}")
            return str(instance_dir)

        print(f"\n{'='*60}")
        print(f"🧬 CREATING NEW TRI-AGENT SYSTEM")
        print(f"{'='*60}")
        print(f"Project: {project_name}")
        print(f"Location: {instance_dir}")
        print(f"Description: {description}\n")

        # Create directory structure
        self._create_directory_structure(instance_dir)

        # Copy core files
        self._copy_core_files(instance_dir)

        # Create instance config
        self._create_instance_config(
            instance_dir,
            project_name,
            description,
            custom_config
        )

        # Create startup scripts
        self._create_startup_scripts(instance_dir, safe_name)

        # Create README
        self._create_readme(instance_dir, project_name, description)

        print(f"\n✅ Tri-Agent System Created!")
        print(f"\n📂 Location: {instance_dir}")
        print(f"\n🚀 To start:")
        print(f"   cd {instance_dir}")
        print(f"   ./start.sh")

        return str(instance_dir)

    def _create_directory_structure(self, instance_dir: Path):
        """Create directory structure"""
        dirs = [
            "agents",
            "core",
            "shared",
            "spawned",
            "logs"
        ]

        for dir_name in dirs:
            (instance_dir / dir_name).mkdir(parents=True, exist_ok=True)

        print("📁 Directory structure created")

    def _copy_core_files(self, instance_dir: Path):
        """Copy core agent files"""
        # Copy shared memory
        shutil.copy(
            self.template_dir / "shared" / "memory.py",
            instance_dir / "shared" / "memory.py"
        )

        # Copy agents
        for agent_file in ["agent1_coder.py", "agent2_improver.py", "agent3_doctor.py"]:
            shutil.copy(
                self.template_dir / "agents" / agent_file,
                instance_dir / "agents" / agent_file
            )

        # Copy core system
        for core_file in ["orchestrator.py", "spawner.py"]:
            shutil.copy(
                self.template_dir / "core" / core_file,
                instance_dir / "core" / core_file
            )

        print("📋 Core files copied")

    def _create_instance_config(
        self,
        instance_dir: Path,
        project_name: str,
        description: str,
        custom_config: Optional[Dict]
    ):
        """Create instance configuration"""
        config = {
            "project_name": project_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "workspace_id": project_name.lower().replace(" ", "_"),
            "agents": {
                "agent1_coder": {
                    "enabled": True,
                    "role": "Primary coder - focused on user context and coding"
                },
                "agent2_improver": {
                    "enabled": True,
                    "role": "Helper and backup - suggests improvements"
                },
                "agent3_doctor": {
                    "enabled": True,
                    "role": "Doctor and arbitrator - fixes bugs, settles disputes"
                }
            },
            "spawning": {
                "enabled": True,
                "max_teams": 10,
                "auto_spawn": True
            }
        }

        if custom_config:
            config.update(custom_config)

        config_file = instance_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print("⚙️  Configuration created")

    def _create_startup_scripts(self, instance_dir: Path, safe_name: str):
        """Create startup scripts"""

        # start.sh
        start_script = f"""#!/bin/bash
# Tri-Agent System Startup Script
# Project: {safe_name}

echo "🎭 Starting Tri-Agent System: {safe_name}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Start orchestrator
echo "🚀 Starting orchestrator..."
python3 core/orchestrator.py

echo ""
echo "✅ System running!"
"""

        start_file = instance_dir / "start.sh"
        with open(start_file, 'w') as f:
            f.write(start_script)
        start_file.chmod(0o755)

        # run_demo.sh
        demo_script = f"""#!/bin/bash
# Run Tri-Agent System Demo

echo "🎭 Running Tri-Agent Demo"
echo ""

python3 core/orchestrator.py
"""

        demo_file = instance_dir / "run_demo.sh"
        with open(demo_file, 'w') as f:
            f.write(demo_script)
        demo_file.chmod(0o755)

        print("📜 Startup scripts created")

    def _create_readme(self, instance_dir: Path, project_name: str, description: str):
        """Create README for this instance"""
        readme_content = f"""# {project_name}

{description}

## Tri-Agent System

This project uses the **Tri-Agent System** - a self-coordinating team of three specialized agents:

### 🤖 The Agents

1. **Agent 1 - The Coder**
   - Primary executor
   - Focused on user context, input, and coding
   - Does NOT read logs (stays focused forward)
   - Main driver of development

2. **Agent 2 - The Improver/Backup**
   - Suggests improvements
   - Helps when Agent 1 hits a wall
   - Can substitute for Agent 1 (gives it a break)
   - Reads logs for context
   - Support role

3. **Agent 3 - The Doctor**
   - Rarely codes
   - Settles disputes between Agent 1 and Agent 2
   - Cures bugs for both agents
   - Can execute simple commands to fix issues
   - Arbitrator and debugger

### 🧬 Dynamic Spawning (Boyle's Law)

When task complexity increases, the system automatically spawns additional tri-agent teams.

> "Like gas expanding to fill its container" - agents spawn to fill complexity

### 🚀 Quick Start

```bash
# Start the system
./start.sh

# Run demo
./run_demo.sh

# Check logs
tail -f logs/*.log
```

### 📁 Structure

```
.
├── agents/           # The 3 core agents
├── core/             # Orchestrator and spawner
├── shared/           # Shared memory system
├── spawned/          # Dynamically spawned teams
├── logs/             # System logs
└── config.json       # Configuration
```

### 🧠 Shared Memory

All 3 agents share the same memory and logs:
- **Agent 1**: Reads user context only
- **Agent 2 & 3**: Read logs and shared memory

### ⚙️ Configuration

Edit `config.json` to customize:
- Enable/disable agents
- Set max spawned teams
- Configure auto-spawning

---

**Created**: {datetime.now().strftime("%Y-%m-%d")}
**System**: Tri-Agent v1.0
"""

        readme_file = instance_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)

        print("📖 README created")

    def list_instances(self):
        """List all created tri-agent instances"""
        instances = []

        for item in self.templates_output_dir.iterdir():
            if item.is_dir():
                config_file = item / "config.json"
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    instances.append({
                        "name": config["project_name"],
                        "path": str(item),
                        "description": config["description"],
                        "created": config["created_at"]
                    })

        return instances


def main():
    """CLI for template generator"""
    import argparse

    parser = argparse.ArgumentParser(description="Tri-Agent Template Generator")
    parser.add_argument("command", choices=["create", "list"], help="Command to execute")
    parser.add_argument("--name", help="Project name (for create)")
    parser.add_argument("--description", help="Project description (for create)")

    args = parser.parse_args()

    generator = TriAgentTemplate()

    if args.command == "create":
        if not args.name:
            print("❌ --name required for create command")
            return

        description = args.description or "Tri-Agent System Instance"

        generator.create_new_system(
            project_name=args.name,
            description=description
        )

    elif args.command == "list":
        print("\n📋 Tri-Agent System Instances:\n")
        instances = generator.list_instances()

        if not instances:
            print("No instances found.")
        else:
            for i, instance in enumerate(instances, 1):
                print(f"{i}. {instance['name']}")
                print(f"   📂 {instance['path']}")
                print(f"   📝 {instance['description']}")
                print(f"   📅 Created: {instance['created']}")
                print()


if __name__ == "__main__":
    # Demo: Create a new instance
    generator = TriAgentTemplate()

    # Example 1: Web API project
    generator.create_new_system(
        project_name="FastAPI Backend",
        description="Build a FastAPI backend with authentication and database"
    )

    # Example 2: Data pipeline
    generator.create_new_system(
        project_name="Data ETL Pipeline",
        description="Extract, transform, and load data from multiple sources"
    )

    # List all instances
    print("\n" + "="*60)
    print("📋 ALL TRI-AGENT INSTANCES")
    print("="*60 + "\n")

    instances = generator.list_instances()
    for i, instance in enumerate(instances, 1):
        print(f"{i}. {instance['name']}")
        print(f"   {instance['description']}")
        print(f"   📂 {instance['path']}\n")

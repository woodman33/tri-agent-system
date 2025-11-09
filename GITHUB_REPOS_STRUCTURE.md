# Double Down Studios - GitHub Repository Structure

## 🎯 Two Separate Repositories

### Repository 1: Local AI Studio
**GitHub:** `github.com/woodman33/local-ai-studio`
**Company:** Double Down Studios
**License:** MIT (Free Tier) + Proprietary (Paid Tiers)

### Repository 2: Tri-Agent System
**GitHub:** `github.com/woodman33/tri-agent-system`
**Company:** Double Down Studios
**License:** Proprietary (Paid Addon)

---

## 📦 Repository 1: Local AI Studio

```
github.com/woodman33/local-ai-studio/
├── README.md
├── LICENSE (MIT for free tier)
├── .github/
│   ├── workflows/
│   │   ├── release.yml
│   │   └── tests.yml
│   └── FUNDING.yml (Gumroad links)
├── src/
│   ├── frontend/ (React + Vite)
│   ├── backend/ (vLLM + Python)
│   └── core/
├── docs/
│   ├── INSTALLATION.md
│   ├── CONFIGURATION.md
│   └── INTEGRATIONS.md
├── scripts/
│   ├── install.sh
│   └── start.sh
└── package.json
```

### README.md (Local AI Studio)
```markdown
# Local AI Studio

<div align="center">
  <img src="docs/logo.png" width="200" />
  <h3>Professional Local AI Chat Interface</h3>
  <p>By <strong>Double Down Studios</strong></p>

  [![GitHub stars](https://img.shields.io/github/stars/woodman33/local-ai-studio)](https://github.com/woodman33/local-ai-studio)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  [![Buy Pro](https://img.shields.io/badge/Buy-Pro%20$9.99-blue)](https://doubledownstudios.gumroad.com/l/local-ai-studio-pro)
</div>

## Features

### Free Tier ✅
- 2 open-source models (Qwen 2.5 3B, Llama 3.2 8B)
- ChatGPT-style interface
- 100% local, no cloud
- vLLM backend

### Pro Tier 💎 ($9.99 one-time)
- All 4 models (+ Phi-4, Mistral 7B)
- Enhanced UI themes
- Priority model loading
- [Buy Now](https://doubledownstudios.gumroad.com/l/local-ai-studio-pro)

### Want Autonomous Agents? 🤖
Check out our [Tri-Agent System](https://github.com/woodman33/tri-agent-system) addon!

## Quick Start

\`\`\`bash
git clone https://github.com/woodman33/local-ai-studio.git
cd local-ai-studio
./install.sh
./start.sh
\`\`\`

## Integration with Tri-Agent System

This app works standalone OR with our [Tri-Agent System](https://github.com/woodman33/tri-agent-system) addon:

- **Standalone**: Chat interface (this repo)
- **With Tri-Agent**: Chat + 6 autonomous agents

The Tri-Agent System uses this app's vLLM server as its shadow layer!

## About Double Down Studios

Professional AI tools built for developers who value:
- ✅ Privacy (100% local)
- ✅ Open source foundations
- ✅ No subscriptions
- ✅ One-time purchases

## License

MIT License for free tier. Paid tiers are proprietary.

Copyright © 2025 Double Down Studios
```

---

## 📦 Repository 2: Tri-Agent System

```
github.com/woodman33/tri-agent-system/
├── README.md
├── LICENSE (Proprietary)
├── .github/
│   ├── workflows/
│   └── FUNDING.yml
├── agents/
│   ├── agent1_coder.py
│   ├── agent2_improver.py
│   └── agent3_doctor.py
├── core/
│   ├── orchestrator.py
│   ├── dual_layer_orchestrator.py
│   ├── spawner.py
│   └── inference_layer.py
├── shared/
│   └── memory.py
├── docs/
│   ├── INSTALLATION.md
│   ├── QUICKSTART.md
│   ├── INTEGRATION.md (with Local AI Studio)
│   └── API.md
├── examples/
├── tests/
└── monetization/
    ├── license_manager.py
    └── activation.py
```

### README.md (Tri-Agent System)
```markdown
# Tri-Agent System

<div align="center">
  <img src="docs/tri-agent-logo.png" width="200" />
  <h3>Autonomous 6-Agent System with Dynamic Spawning</h3>
  <p>By <strong>Double Down Studios</strong></p>

  [![GitHub stars](https://img.shields.io/github/stars/woodman33/tri-agent-system)](https://github.com/woodman33/tri-agent-system)
  [![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
  [![Buy Now](https://img.shields.io/badge/Buy-$39.99-purple)](https://doubledownstudios.gumroad.com/l/tri-agent-system)
</div>

## What Is This?

A **self-coordinating 6-agent team** that works together to code, improve, and debug:

- **Agent 1 (Coder)**: Focused on user tasks
- **Agent 2 (Improver)**: Suggests improvements, helps Agent 1
- **Agent 3 (Doctor)**: Fixes bugs, settles disputes
- **Agents 1M, 2M, 3M (Shadow Layer)**: Monitor primary agents

When complexity increases, the system **spawns additional teams** automatically (Boyle's Law).

## 🎯 Requirements

### Required: Local AI Studio
This system integrates with [Local AI Studio](https://github.com/woodman33/local-ai-studio):

\`\`\`bash
# 1. Install Local AI Studio first
git clone https://github.com/woodman33/local-ai-studio.git
cd local-ai-studio
./install.sh

# 2. Then install Tri-Agent System
git clone https://github.com/woodman33/tri-agent-system.git
cd tri-agent-system
./install.sh
\`\`\`

The Tri-Agent System uses Local AI Studio's vLLM server as its shadow layer!

## 💰 Pricing

**$39.99 one-time purchase**

Includes:
- ✅ 6-agent autonomous system
- ✅ Boyle's Law dynamic spawning
- ✅ Dual-layer architecture
- ✅ Lifetime updates
- ✅ Priority support

[**Purchase Now**](https://doubledownstudios.gumroad.com/l/tri-agent-system)

## 🔐 License Activation

After purchase:

\`\`\`bash
# Run activation script
./activate.sh

# Enter license key from email
License Key: XXXX-XXXX-XXXX-XXXX
Email: your@email.com

# System automatically downloads and activates
✅ Tri-Agent System activated!
\`\`\`

## Features

### Dual-Layer Architecture
- **Layer 1 (Primary)**: Ollama - user-facing work
- **Layer 2 (Shadow)**: vLLM - monitoring & backup

### Boyle's Law Spawning
When complexity increases, spawns additional teams:
- Simple tasks: 6 agents
- Complex tasks: 18+ agents (3 teams × 6)

### 100% Free & Open Source Stack
- Ollama (free)
- vLLM (free)
- Qwen3 8B (free, open-source model)
- No APIs, no cloud costs

## Integration

Works seamlessly with Local AI Studio:

\`\`\`
Local AI Studio (Chat Interface)
         ↓
    vLLM Server (Port 8000)
         ↓
Tri-Agent System (Uses same vLLM!)
\`\`\`

No duplication, shared resources!

## Documentation

- [Quick Start](docs/QUICKSTART.md)
- [Integration Guide](docs/INTEGRATION.md)
- [API Documentation](docs/API.md)
- [Examples](examples/)

## About Double Down Studios

Professional AI tools for serious developers.

**Our Products:**
- [Local AI Studio](https://github.com/woodman33/local-ai-studio) - Free/Pro chat interface
- [Tri-Agent System](https://github.com/woodman33/tri-agent-system) - $39.99 autonomous agents

## License

Proprietary. Purchase required for use.

Copyright © 2025 Double Down Studios
```

---

## 🏢 Double Down Studios Branding

### GitHub Organization
```
github.com/woodman33/
├── local-ai-studio (Public - Free + Paid tiers)
├── tri-agent-system (Public - Paid addon)
└── doubledown-studios.github.io (Company website)
```

### Company Profile

**GitHub `woodman33` Profile:**
```markdown
# Double Down Studios 🎲

Professional AI tools built on open-source foundations.

## Products

🎨 **[Local AI Studio](https://github.com/woodman33/local-ai-studio)**
Professional local AI chat interface
- Free tier available
- Pro: $9.99

🤖 **[Tri-Agent System](https://github.com/woodman33/tri-agent-system)**
Autonomous 6-agent development system
- $39.99 one-time

## Philosophy

✅ Privacy first (100% local)
✅ Open source foundations
✅ No subscriptions
✅ Lifetime purchases
```

### Gumroad Products

**Product 1: Local AI Studio Pro**
- URL: `doubledownstudios.gumroad.com/l/local-ai-studio-pro`
- Price: $9.99
- Generates license key
- Webhook to license server

**Product 2: Tri-Agent System**
- URL: `doubledownstudios.gumroad.com/l/tri-agent-system`
- Price: $39.99
- Generates license key
- Webhook to license server

---

## 🔗 Cross-Linking Strategy

### Local AI Studio → Tri-Agent System
```markdown
## Want Autonomous Agents?

The Tri-Agent System addon works with this app!

- Uses the same vLLM server
- 6 agents working together
- Dynamic spawning when tasks get complex

[Learn More →](https://github.com/woodman33/tri-agent-system)
```

### Tri-Agent System → Local AI Studio
```markdown
## Requirements

Requires [Local AI Studio](https://github.com/woodman33/local-ai-studio) installed.

The Tri-Agent System uses Local AI Studio's vLLM backend
for its shadow layer (Layer 2).

Install Local AI Studio first (free tier works!), then add
Tri-Agent System for autonomous agents.
```

---

## 📊 GitHub Badges

Both repos should have:
```markdown
![GitHub stars](https://img.shields.io/github/stars/woodman33/REPO)
![GitHub forks](https://img.shields.io/github/forks/woodman33/REPO)
![License](https://img.shields.io/badge/License-...)
![Double Down Studios](https://img.shields.io/badge/By-Double%20Down%20Studios-blue)
```

---

## 💼 Recommended GitHub Org Setup

**Create Organization:**
```
github.com/doubledown-studios/
├── local-ai-studio
└── tri-agent-system
```

**Or use personal account:**
```
github.com/woodman33/
├── local-ai-studio
└── tri-agent-system
```

**Recommended:** Use organization for professional branding

---

## 🚀 Launch Checklist

### Local AI Studio Repo
- [ ] Create repo on GitHub
- [ ] Add README with branding
- [ ] Add LICENSE (MIT for free, proprietary for paid)
- [ ] Setup Gumroad product
- [ ] Add .github/FUNDING.yml
- [ ] Create release (v1.0.0)

### Tri-Agent System Repo
- [ ] Create repo on GitHub
- [ ] Add README with branding
- [ ] Add LICENSE (Proprietary)
- [ ] Setup Gumroad product
- [ ] Link to Local AI Studio
- [ ] Create release (v1.0.0)

### Double Down Studios
- [ ] Setup Gumroad account
- [ ] Create company logo
- [ ] Setup GitHub organization (optional)
- [ ] Create license validation server
- [ ] Setup webhooks

---

**Both repos by woodman33 at Double Down Studios** ✅
**Separate but integrated** ✅
**Professional monetization** ✅

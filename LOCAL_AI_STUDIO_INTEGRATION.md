# Local AI Studio Integration

## 🎯 Perfect Match!

Your **Local AI Studio** already has vLLM running! The tri-agent system can use the **same vLLM server** as your AI Studio.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                Your Local AI Ecosystem                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  LOCAL AI STUDIO              TRI-AGENT SYSTEM             │
│  (React + vLLM)               (Python Agents)              │
│                                                             │
│  ┌──────────────┐            ┌──────────────┐             │
│  │ Chat UI      │            │ Layer 1      │             │
│  │ (Frontend)   │            │ (Ollama)     │             │
│  └──────┬───────┘            │ - Agent 1,2,3│             │
│         │                    └──────┬───────┘             │
│         │                           │                      │
│         │    ┌─────────────────────┴──────┐              │
│         │    │                             │              │
│         ▼    ▼                             ▼              │
│  ┌─────────────────────────────────────────────┐         │
│  │         vLLM Server (Port 8000)              │         │
│  │  - Qwen 2.5 3B                               │         │
│  │  - Llama 3.2 8B                              │         │
│  │  - Phi-4 Mini                                │         │
│  │  - Mistral 7B                                │         │
│  └─────────────────────────────────────────────┘         │
│         │                             │                    │
│         │                             ▼                    │
│         │                    ┌──────────────┐             │
│         │                    │ Layer 2      │             │
│         └───────────────────▶│ (vLLM)       │             │
│                              │ - Agent 1M,2M│             │
│                              │   3M         │             │
│                              └──────────────┘             │
│                                                             │
│  SHARED vLLM SERVER = NO DUPLICATION!                      │
└────────────────────────────────────────────────────────────┘
```

## Benefits

✅ **One vLLM Server** - Both systems use it
✅ **No Duplication** - Models loaded once
✅ **Resource Efficient** - Share GPU/CPU
✅ **Unified Management** - One place to manage models
✅ **Llama.cpp** - Can use for even faster inference

## Setup

### 1. Start Your AI Studio vLLM Server

```bash
cd ~/local-ai-studio/backend
python vllm_server.py

# vLLM now running at http://localhost:8000
```

### 2. Configure Tri-Agent to Use Your vLLM

Edit `tri-agent-system/config/inference.json`:

```json
{
  "primary": {
    "type": "ollama",
    "model": "qwen3:8b",
    "base_url": "http://localhost:11434"
  },
  "shadow": {
    "enabled": true,
    "type": "vllm",
    "api_url": "http://localhost:8000",
    "model": "Qwen/Qwen2.5-3B"  // Your AI Studio model!
  }
}
```

### 3. Run Tri-Agent System

```bash
cd ~/multiagent-frameworks/tri-agent-system
export PYTHONPATH="/Users/willmeldman/multiagent-frameworks/tri-agent-system:$PYTHONPATH"
poetry run python core/dual_layer_orchestrator.py
```

Now:
- ✅ AI Studio uses vLLM for chat
- ✅ Tri-Agent Layer 2 uses same vLLM for monitoring
- ✅ Only ONE vLLM server running

## Model Selection

Your AI Studio has 4 models. Choose best for each use case:

### For Tri-Agent Layer 2 (Monitoring)

**Option 1: Qwen 2.5 3B** (Recommended)
- Smallest (1.5GB)
- Fast inference
- Good for monitoring tasks
- Leaves resources for Layer 1

**Option 2: Llama 3.2 8B**
- Best quality
- Slower
- Use if monitoring needs deep reasoning

### For AI Studio Chat

Use any model you prefer! They're independent.

## Advanced: llama.cpp Integration

Your AI Studio can ALSO support llama.cpp for even faster inference:

```bash
# Install llama.cpp
brew install llama.cpp

# Download GGUF model
wget https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf

# Start llama.cpp server
llama-server \
  --model qwen2.5-3b-instruct-q4_k_m.gguf \
  --port 8080 \
  --ctx-size 4096
```

Then tri-agent can use llama.cpp instead:

```json
{
  "shadow": {
    "enabled": true,
    "type": "llamacpp",
    "api_url": "http://localhost:8080"
  }
}
```

## Usage Patterns

### Pattern 1: Chat + Agents (Light)
```
AI Studio: Qwen 2.5 3B (chat)
Tri-Agent Layer 1: Ollama Qwen3 8B (primary)
Tri-Agent Layer 2: vLLM Qwen 2.5 3B (monitoring)

Total models loaded: 2
Memory usage: ~6GB
```

### Pattern 2: Chat + Agents (Heavy)
```
AI Studio: Llama 3.2 8B (chat)
Tri-Agent Layer 1: Ollama Qwen3 8B (primary)
Tri-Agent Layer 2: vLLM Llama 3.2 8B (monitoring)

Total models loaded: 2
Memory usage: ~13GB
```

### Pattern 3: Maximum Efficiency
```
AI Studio: llama.cpp Qwen 2.5 3B (chat)
Tri-Agent Layer 1: Ollama Qwen3 8B (primary)
Tri-Agent Layer 2: llama.cpp Qwen 2.5 3B (monitoring)

Total models loaded: 2
Memory usage: ~5GB (llama.cpp is lighter!)
```

## Unified Model Management

All models in ONE place:

```bash
# Your AI Studio backend manages models
cd ~/local-ai-studio/backend

# List available models
curl http://localhost:8000/v1/models

# Add new model to your AI Studio
# Edit backend/vllm_server.py

# Both AI Studio and Tri-Agent automatically see it!
```

## API Compatibility

Your AI Studio vLLM server is **OpenAI-compatible**:

```python
# Tri-Agent can use it like this:
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # vLLM doesn't require key
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-3B",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Example: Full Stack Running

**Terminal 1: AI Studio Backend**
```bash
cd ~/local-ai-studio/backend
python vllm_server.py
# vLLM server at http://localhost:8000
```

**Terminal 2: AI Studio Frontend**
```bash
cd ~/local-ai-studio/frontend
npm run dev
# Chat UI at http://localhost:5173
```

**Terminal 3: Tri-Agent System**
```bash
cd ~/multiagent-frameworks/tri-agent-system
export PYTHONPATH="/Users/willmeldman/multiagent-frameworks/tri-agent-system:$PYTHONPATH"
poetry run python core/dual_layer_orchestrator.py
# Agents using same vLLM server!
```

Now:
- ✅ Chat in AI Studio UI
- ✅ Agents working autonomously
- ✅ Both using SAME vLLM server
- ✅ No duplication, efficient resources

## Benefits of Integration

### 1. Resource Efficiency
- Models loaded ONCE
- Share GPU/CPU between systems
- Lower memory footprint

### 2. Unified Interface
- Manage models in AI Studio
- Both systems auto-update

### 3. Development Flow
```
1. Test prompt in AI Studio chat
2. Works well? Use same model in tri-agent
3. One model, two interfaces
```

### 4. Cost Savings
```
Without integration:
- AI Studio vLLM: 4GB
- Tri-Agent vLLM: 4GB
- Total: 8GB

With integration:
- Shared vLLM: 4GB
- Total: 4GB

Savings: 50% memory!
```

## Configuration Files

### AI Studio: `backend/vllm_server.py`
```python
# Your existing vLLM server
# Already configured and running!
```

### Tri-Agent: `config/inference.json`
```json
{
  "primary": {
    "type": "ollama",
    "model": "qwen3:8b"
  },
  "shadow": {
    "enabled": true,
    "type": "vllm",
    "api_url": "http://localhost:8000",  // Your AI Studio!
    "model": "Qwen/Qwen2.5-3B"           // Your AI Studio model!
  }
}
```

## Troubleshooting

### AI Studio vLLM won't start
```bash
# Check if port 8000 in use
lsof -i :8000

# Kill if needed
kill -9 <PID>

# Restart AI Studio backend
cd ~/local-ai-studio/backend
python vllm_server.py
```

### Tri-Agent can't connect to vLLM
```bash
# Test vLLM endpoint
curl http://localhost:8000/health

# Should return: {"status": "ok"}

# If not, restart AI Studio backend
```

### Out of memory
```bash
# Use smaller model in AI Studio
# Edit backend/vllm_server.py
# Use Qwen 2.5 3B instead of Llama 3.2 8B

# Or use llama.cpp (lighter)
brew install llama.cpp
llama-server --model <model.gguf> --port 8080
```

## Next Level: AnythingLLM Integration

You also have **AnythingLLM** installed! Can integrate that too:

```
┌──────────────────────────────────────────────────┐
│         Complete Local AI Ecosystem              │
├──────────────────────────────────────────────────┤
│                                                   │
│  AnythingLLM (Documents)                         │
│       │                                           │
│       ├─→ vLLM Server (Port 8000)                │
│       │      │                                    │
│  AI Studio Chat  ├─→ Tri-Agent Layer 2          │
│       │          │                                │
│       └──────────┘                                │
│                                                   │
│  ALL using the SAME vLLM server!                 │
└──────────────────────────────────────────────────┘
```

## Summary

✅ Your **Local AI Studio vLLM** = Tri-Agent **Layer 2**
✅ No duplication, shared resources
✅ Both systems benefit from same models
✅ Unified model management
✅ Optional llama.cpp for max speed
✅ 100% free, 100% local, 100% open source

**You already have everything you need!** 🎉

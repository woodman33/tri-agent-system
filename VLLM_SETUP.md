# vLLM Setup Guide (100% Free & Open Source)

## Why vLLM for Shadow Layer?

**Benefits:**
- ✅ **Free & Open Source** - No cost, self-hosted
- ✅ **Fast inference** - Optimized for throughput
- ✅ **Load distribution** - Offload monitoring to vLLM
- ✅ **Runs locally** - Your Mac or any server you control
- ✅ **Failover** - If Ollama crashes, vLLM can take over

## Option 1: Local vLLM (Your Mac)

### Install
```bash
# Using pip
pip install vllm

# Or using poetry (in your project)
cd ~/multiagent-frameworks
poetry add vllm
```

### Start vLLM Server
```bash
# Start vLLM with Qwen3 8B (same model as Ollama)
vllm serve Qwen/Qwen2.5-7B-Instruct \
    --port 8000 \
    --max-model-len 4096 \
    --dtype auto

# Server will be at: http://localhost:8000
```

### Test
```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "prompt": "What is 2+2?",
    "max_tokens": 100
  }'
```

## Option 2: Self-Hosted vLLM (Free Server)

### Using Oracle Cloud (Free Tier)
Oracle offers **FREE forever** tier with:
- 4 ARM cores + 24GB RAM
- Perfect for vLLM

```bash
# SSH into your Oracle Cloud instance
ssh ubuntu@your-oracle-instance

# Install vLLM
pip install vllm

# Start vLLM
vllm serve Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 4096

# Access from anywhere: http://your-oracle-ip:8000
```

### Using Your Own Server
Any Linux box with:
- 8GB+ RAM
- Modern CPU
- GPU optional (CPU inference works fine)

## Option 3: No vLLM (Ollama Only)

If you don't want to run vLLM, the system gracefully degrades:

```python
# Shadow layer disabled, primary layer only
orchestrator = DualLayerTriAgent(
    "workspace",
    use_vllm_shadow=False  # Only Ollama, 3 agents instead of 6
)
```

## Current Architecture

### With vLLM (6 agents)
```
┌────────────────────────────────────────┐
│  Layer 1 (Primary)  │ Layer 2 (Shadow) │
│  ├─ Ollama          │ ├─ vLLM          │
│  ├─ Agent 1,2,3     │ ├─ Agent 1M,2M,3M│
│  └─ User work       │ └─ Monitoring    │
├────────────────────────────────────────┤
│  Both 100% free & open source          │
│  Both running locally (your control)   │
└────────────────────────────────────────┘
```

### Without vLLM (3 agents)
```
┌──────────────────────┐
│  Layer 1 (Primary)   │
│  ├─ Ollama           │
│  ├─ Agent 1,2,3      │
│  └─ User work        │
├──────────────────────┤
│  100% free & local   │
└──────────────────────┘
```

## Configuration

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
    "model": "Qwen/Qwen2.5-7B-Instruct"
  }
}
```

## Performance

### Ollama (Primary)
- **Speed**: ~20 tokens/sec (CPU)
- **Latency**: Low (local)
- **Use**: User-facing work

### vLLM (Shadow)
- **Speed**: ~30-50 tokens/sec (optimized)
- **Latency**: Low (local) or medium (remote)
- **Use**: Monitoring, backup

## Failover

If Ollama crashes:
1. vLLM automatically takes over
2. Shadow agents become primary
3. System continues working
4. When Ollama recovers, it resumes

## Cost Comparison

### Our Setup (FREE)
- Ollama: **$0/month**
- vLLM (local): **$0/month**
- vLLM (Oracle Free): **$0/month**
- **TOTAL: $0/month forever**

### Cloud Alternative (EXPENSIVE)
- OpenAI API: **$10-100/month**
- Anthropic: **$15-150/month**
- Together AI: **$8-80/month**
- **TOTAL: $33-330/month**

## Quick Start

### 1. Start Ollama (if not running)
```bash
brew services start ollama
ollama pull qwen3:8b
```

### 2. Start vLLM (optional)
```bash
# Terminal 1: Start vLLM
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000

# Terminal 2: Test dual-layer
cd ~/multiagent-frameworks/tri-agent-system
export PYTHONPATH="/Users/willmeldman/multiagent-frameworks/tri-agent-system:$PYTHONPATH"
poetry run python core/dual_layer_orchestrator.py
```

### 3. Without vLLM (Ollama only)
```python
from core.dual_layer_orchestrator import DualLayerTriAgent

# 3 agents (no shadow layer)
orchestrator = DualLayerTriAgent("workspace", use_vllm_shadow=False)
```

## Troubleshooting

### vLLM won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill if needed
kill -9 <PID>

# Restart vLLM
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000
```

### Out of memory
```bash
# Use smaller context window
vllm serve Qwen/Qwen2.5-7B-Instruct \
    --port 8000 \
    --max-model-len 2048  # Reduced from 4096
```

### Can't download model
```bash
# Download manually first
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B-Instruct')"

# Then start vLLM
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000
```

## Recommended Setup

**For Development:**
- Ollama only (3 agents)
- Fast, simple, local

**For Production:**
- Ollama + vLLM (6 agents)
- Load distribution
- Failover capability
- Monitoring layer

## Next Steps

1. Try Ollama-only first (works out of the box)
2. Add vLLM when you need:
   - Load distribution
   - Failover
   - Monitoring layer
3. Scale to self-hosted vLLM when ready

---

**Everything is FREE and OPEN SOURCE!** 🎉

No APIs, no cloud costs, no vendor lock-in.

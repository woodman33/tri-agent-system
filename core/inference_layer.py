"""
Inference Layer Abstraction

Supports:
- Local inference (Ollama, llama.cpp)
- Remote inference (vLLM, LiteLLM, Digital Ocean, OpenStack)
- Automatic failover between providers
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
import requests
import json
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod


class InferenceProvider(ABC):
    """Abstract base for inference providers"""

    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """Generate completion"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get provider name"""
        pass


class OllamaProvider(InferenceProvider):
    """Local Ollama inference"""

    def __init__(self, model: str = "qwen3:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """Generate using Ollama"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.3)
            }
        }

        if system:
            payload["system"] = system

        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_name(self) -> str:
        return f"Ollama ({self.model})"


class VLLMProvider(InferenceProvider):
    """Remote vLLM inference server"""

    def __init__(
        self,
        api_url: str,
        model: str = "qwen3-8b",
        api_key: Optional[str] = None
    ):
        self.api_url = api_url.rstrip("/")
        self.model = model
        self.api_key = api_key or os.getenv("VLLM_API_KEY")
        self.completions_url = f"{self.api_url}/v1/completions"

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """Generate using vLLM"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.3),
            "stream": False
        }

        try:
            response = requests.post(
                self.completions_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["text"]
        except Exception as e:
            raise Exception(f"vLLM generation failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if vLLM server is reachable"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_name(self) -> str:
        return f"vLLM ({self.api_url})"


class LiteLLMProvider(InferenceProvider):
    """LiteLLM proxy server"""

    def __init__(
        self,
        api_url: str,
        model: str = "qwen3-8b",
        api_key: Optional[str] = None
    ):
        self.api_url = api_url.rstrip("/")
        self.model = model
        self.api_key = api_key or os.getenv("LITELLM_API_KEY")
        self.completions_url = f"{self.api_url}/chat/completions"

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """Generate using LiteLLM"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.3),
            "stream": False
        }

        try:
            response = requests.post(
                self.completions_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"LiteLLM generation failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if LiteLLM is reachable"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_name(self) -> str:
        return f"LiteLLM ({self.api_url})"


class DigitalOceanProvider(InferenceProvider):
    """Digital Ocean hosted inference"""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key or os.getenv("DO_API_KEY")

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """Generate using DO endpoint"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "prompt": prompt,
            "system": system,
            "temperature": kwargs.get("temperature", 0.3)
        }

        try:
            response = requests.post(
                f"{self.api_url}/generate",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            raise Exception(f"Digital Ocean generation failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if DO endpoint is reachable"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.api_url}/health", headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_name(self) -> str:
        return f"DigitalOcean ({self.api_url})"


class InferenceLayer:
    """
    Unified inference layer with automatic failover.

    Supports:
    - Local: Ollama, llama.cpp
    - Remote: vLLM, LiteLLM, Digital Ocean

    Automatically fails over if primary provider unavailable.
    """

    def __init__(
        self,
        primary_provider: InferenceProvider,
        backup_providers: Optional[List[InferenceProvider]] = None
    ):
        self.primary = primary_provider
        self.backups = backup_providers or []
        self.all_providers = [self.primary] + self.backups

        # Track provider health
        self.provider_failures = {p.get_name(): 0 for p in self.all_providers}

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate completion with automatic failover.

        Returns:
            {
                "response": str,
                "provider": str,
                "fallback_used": bool
            }
        """
        # Try primary first
        for provider in self.all_providers:
            if not provider.is_available():
                print(f"[InferenceLayer] ⚠️  {provider.get_name()} unavailable, trying next...")
                self.provider_failures[provider.get_name()] += 1
                continue

            try:
                response = provider.generate(prompt, system, **kwargs)

                # Reset failure count on success
                self.provider_failures[provider.get_name()] = 0

                return {
                    "response": response,
                    "provider": provider.get_name(),
                    "fallback_used": provider != self.primary
                }

            except Exception as e:
                print(f"[InferenceLayer] ❌ {provider.get_name()} failed: {str(e)}")
                self.provider_failures[provider.get_name()] += 1
                continue

        # All providers failed
        raise Exception("All inference providers failed")

    def get_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return {
            "primary": {
                "name": self.primary.get_name(),
                "available": self.primary.is_available(),
                "failures": self.provider_failures[self.primary.get_name()]
            },
            "backups": [
                {
                    "name": p.get_name(),
                    "available": p.is_available(),
                    "failures": self.provider_failures[p.get_name()]
                }
                for p in self.backups
            ]
        }


def create_inference_layer(config: Dict[str, Any]) -> InferenceLayer:
    """
    Factory function to create inference layer from config.

    Example config:
    {
        "primary": {
            "type": "ollama",
            "model": "qwen3:8b"
        },
        "backups": [
            {
                "type": "vllm",
                "api_url": "https://my-vllm.example.com",
                "model": "qwen3-8b"
            },
            {
                "type": "digitalocean",
                "api_url": "https://my-do-app.ondigitalocean.app"
            }
        ]
    }
    """
    # Create primary
    primary_config = config["primary"]
    primary_type = primary_config["type"]

    if primary_type == "ollama":
        primary = OllamaProvider(
            model=primary_config.get("model", "qwen3:8b"),
            base_url=primary_config.get("base_url", "http://localhost:11434")
        )
    elif primary_type == "vllm":
        primary = VLLMProvider(
            api_url=primary_config["api_url"],
            model=primary_config.get("model", "qwen3-8b"),
            api_key=primary_config.get("api_key")
        )
    elif primary_type == "litellm":
        primary = LiteLLMProvider(
            api_url=primary_config["api_url"],
            model=primary_config.get("model", "qwen3-8b"),
            api_key=primary_config.get("api_key")
        )
    elif primary_type == "digitalocean":
        primary = DigitalOceanProvider(
            api_url=primary_config["api_url"],
            api_key=primary_config.get("api_key")
        )
    else:
        raise ValueError(f"Unknown provider type: {primary_type}")

    # Create backups
    backups = []
    for backup_config in config.get("backups", []):
        backup_type = backup_config["type"]

        if backup_type == "ollama":
            backup = OllamaProvider(
                model=backup_config.get("model", "qwen3:8b"),
                base_url=backup_config.get("base_url", "http://localhost:11434")
            )
        elif backup_type == "vllm":
            backup = VLLMProvider(
                api_url=backup_config["api_url"],
                model=backup_config.get("model", "qwen3-8b"),
                api_key=backup_config.get("api_key")
            )
        elif backup_type == "litellm":
            backup = LiteLLMProvider(
                api_url=backup_config["api_url"],
                model=backup_config.get("model", "qwen3-8b"),
                api_key=backup_config.get("api_key")
            )
        elif backup_type == "digitalocean":
            backup = DigitalOceanProvider(
                api_url=backup_config["api_url"],
                api_key=backup_config.get("api_key")
            )
        else:
            print(f"⚠️  Unknown backup provider type: {backup_type}, skipping")
            continue

        backups.append(backup)

    return InferenceLayer(primary, backups)


if __name__ == "__main__":
    # Test inference layer with failover
    print("🧪 Testing Inference Layer with Failover\n")

    # Config with local primary, remote backup
    config = {
        "primary": {
            "type": "ollama",
            "model": "qwen3:8b"
        },
        "backups": [
            # Add your vLLM/DO endpoints here
            # {
            #     "type": "vllm",
            #     "api_url": "https://my-vllm.example.com",
            #     "model": "qwen3-8b"
            # }
        ]
    }

    inference = create_inference_layer(config)

    # Check status
    print("📊 Provider Status:")
    status = inference.get_status()
    print(f"Primary: {status['primary']['name']} - {'✅' if status['primary']['available'] else '❌'}")
    for backup in status['backups']:
        print(f"Backup: {backup['name']} - {'✅' if backup['available'] else '❌'}")

    # Test generation
    if status['primary']['available']:
        print("\n🚀 Testing generation...")
        result = inference.generate(
            prompt="What is 2+2?",
            system="You are a helpful assistant. Be concise."
        )
        print(f"\nProvider: {result['provider']}")
        print(f"Fallback used: {result['fallback_used']}")
        print(f"Response: {result['response'][:200]}...")

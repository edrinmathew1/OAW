import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Ollama endpoint and model
OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL: str = os.getenv("OLLAMA_MODEL", os.getenv("MODEL", "qwen2.5:3b"))


# Agent identity
AGENT_NAME: str = os.getenv("AGENT_NAME", "Observable Agent")

# Memory persistence
MEMORY_FILE: str = os.getenv("MEMORY_FILE", "memory.json")

# External API Keys (optional integrations)
TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")
E2B_API_KEY: str | None = os.getenv("E2B_API_KEY")


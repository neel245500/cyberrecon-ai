from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from core.constants import PROJECT_ROOT


@dataclass(slots=True)
class Settings:
    concurrency: int = 80
    timeout_seconds: int = 15
    retries: int = 2
    user_agent: str = "CyberReconAI/1.0"
    ollama_model: str = "llama3"
    ollama_url: str = "http://localhost:11434"
    openai_enabled: bool = False
    openai_api_key: str = ""
    deepseek_enabled: bool = False
    deepseek_api_key: str = ""


class Config:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or PROJECT_ROOT / "config" / "default.yaml"
        self.raw: dict[str, Any] = {}
        self.settings = Settings()

    def load(self) -> Settings:
        # Load from YAML
        if self.config_path.exists():
            with self.config_path.open("r", encoding="utf-8") as file:
                self.raw = yaml.safe_load(file) or {}
            merged = {**asdict(self.settings), **self.raw.get("settings", {})}
            self.settings = Settings(**merged)
        
        # Override with environment variables
        env_overrides = {
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "openai_enabled": bool(os.getenv("OPENAI_API_KEY")),
            "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY", ""),
            "ollama_url": os.getenv("OLLAMA_URL", self.settings.ollama_url),
            "ollama_model": os.getenv("OLLAMA_MODEL", self.settings.ollama_model),
        }
        current = asdict(self.settings)
        current.update({k: v for k, v in env_overrides.items() if v})
        self.settings = Settings(**current)
        
        return self.settings

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Iterable

from modules.base import ReconModule


class PluginManager:
    def __init__(self, plugin_dir: Path) -> None:
        self.plugin_dir = plugin_dir

    def load_modules(self) -> list[ReconModule]:
        modules: list[ReconModule] = []
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        for file in self.plugin_dir.glob("*.py"):
            plugin = self._load_py(file)
            if plugin is None:
                continue
            plugin_modules = getattr(plugin, "PLUGIN_MODULES", [])
            for module in plugin_modules:
                if isinstance(module, ReconModule):
                    modules.append(module)
        return modules

    def _load_py(self, file: Path) -> ModuleType | None:
        spec = importlib.util.spec_from_file_location(file.stem, file)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


class ModuleRegistry:
    def __init__(self) -> None:
        self._modules: list[ReconModule] = []

    def register(self, modules: Iterable[ReconModule]) -> None:
        self._modules.extend(modules)

    def get_all(self) -> list[ReconModule]:
        return list(self._modules)

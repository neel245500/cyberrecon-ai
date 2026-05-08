from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from core.config import Settings
from core.tool_manager import ToolManager
from core.types import Finding


@dataclass(slots=True)
class ModuleContext:
    settings: Settings
    tool_manager: ToolManager
    client: httpx.AsyncClient
    output_dir: str


class ReconModule:
    name = "base"

    async def run(self, target: str, context: ModuleContext) -> dict[str, Any]:
        raise NotImplementedError

    def finding(self, **kwargs: Any) -> Finding:
        return Finding(module=self.name, **kwargs)

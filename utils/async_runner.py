from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(slots=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


async def run_command(command: list[str], timeout: int = 120) -> CommandResult:
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except TimeoutError:
        proc.kill()
        await proc.communicate()
        return CommandResult(command=command, returncode=124, stdout="", stderr="Command timed out")

    return CommandResult(
        command=command,
        returncode=proc.returncode,
        stdout=stdout.decode(errors="ignore"),
        stderr=stderr.decode(errors="ignore"),
    )

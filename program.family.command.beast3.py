# program.family.command.beast3.py
# Beast System 3.0 — Unified Operator Command Layer

from dataclasses import dataclass, field
import time
import hashlib

@dataclass
class CommandEntry:
    operator_id: str
    module: str
    action: str
    payload: dict
    ts: float = field(default_factory=time.time)
    hash: str = ""

    def finalize(self):
        serialized = f"{self.operator_id}{self.module}{self.action}{self.payload}{self.ts}".encode("utf-8")
        self.hash = hashlib.sha256(serialized).hexdigest()

@dataclass
class CommandProfile:
    family_id: str
    commands: list = field(default_factory=list)
    last_update: float = field(default_factory=time.time)

    def add_command(self, operator_id: str, module: str, action: str, payload: dict):
        entry = CommandEntry(operator_id, module, action, payload)
        entry.finalize()
        self.commands.append(entry)
        self.last_update = entry.ts

class CommandEngine:
    def __init__(self, kernel):
        self.kernel = kernel
        self.command_profiles = {}

    def create_command_profile(self, family_id: str):
        profile = CommandProfile(family_id)
        self.command_profiles[family_id] = profile

        return self.kernel.dispatch(
            module="family.command",
            action="create_command_profile",
            payload={"family_id": family_id}
        )

    def execute(self, family_id: str, operator_id: str, module: str, action: str, payload: dict):
        if family_id not in self.command_profiles:
            raise ValueError("Command profile not found")

        profile = self.command_profiles[family_id]
        profile.add_command(operator_id, module, action, payload)

        return self.kernel.dispatch(
            module="family.command",
            action="execute",
            payload={
                "family_id": family_id,
                "operator_id": operator_id,
                "module": module,
                "action": action,
                "payload": payload,
                "ts": profile.last_update
            }
        )

    def get_commands(self, family_id: str):
        return self.command_profiles.get(family_id, None)

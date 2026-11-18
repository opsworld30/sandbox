from dataclasses import dataclass


@dataclass(frozen=True)
class ExpansionRequest:
    command_id: str
    hostname: str
    reason: str


class CommandPolicy:
    def __init__(self, base_network_enabled: bool = False):
        self.base_network_enabled = base_network_enabled
        self.approved: dict[str, set[str]] = {}

    def approve(self, request: ExpansionRequest) -> None:
        if not request.command_id or not request.hostname or not request.reason:
            raise ValueError("command_id, hostname and reason are required")
        self.approved.setdefault(request.command_id, set()).add(request.hostname.lower())

    def network_allowed(self, command_id: str, hostname: str) -> bool:
        if self.base_network_enabled:
            return True
        return hostname.lower() in self.approved.get(command_id, set())

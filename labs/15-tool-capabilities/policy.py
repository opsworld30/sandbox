from dataclasses import dataclass


@dataclass(frozen=True)
class ToolPolicy:
    capabilities: frozenset[str]


POLICIES = {
    "shell": ToolPolicy(frozenset({"workspace.read", "workspace.write"})),
    "browser": ToolPolicy(frozenset({"network.example.com"})),
    "mcp.issue.read": ToolPolicy(frozenset({"issue.read"})),
}


class CapabilityDenied(PermissionError):
    pass


class ToolBroker:
    def __init__(self, policies=None):
        self.policies = policies or POLICIES

    def require(self, tool: str, capability: str) -> None:
        policy = self.policies.get(tool)
        if policy is None or capability not in policy.capabilities:
            raise CapabilityDenied(f"{tool} lacks capability {capability}")

    def read_workspace(self, tool: str) -> str:
        self.require(tool, "workspace.read")
        return "workspace file contents"

    def fetch_example(self, tool: str) -> str:
        self.require(tool, "network.example.com")
        return "mock response from https://example.com"

    def read_issue(self, tool: str) -> str:
        self.require(tool, "issue.read")
        return "mock issue #42"

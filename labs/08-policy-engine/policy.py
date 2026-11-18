"""Teaching example: monotonic, deny-wins policy composition."""
from __future__ import annotations


def _intersection(current: set[str] | None, incoming: list[str]) -> set[str]:
    values = set(incoming)
    return values if current is None else current & values


def effective_policy(*layers: dict) -> dict:
    allowed_tools: set[str] | None = None
    denied_tools: set[str] = set()
    allowed_hosts: set[str] | None = None
    network_enabled = True

    for layer in layers:
        if "allow_tools" in layer:
            allowed_tools = _intersection(allowed_tools, layer["allow_tools"])
        denied_tools.update(layer.get("deny_tools", []))

        network = layer.get("network", {})
        if "enabled" in network:
            network_enabled = network_enabled and bool(network["enabled"])
        if "allowed_hosts" in network:
            allowed_hosts = _intersection(allowed_hosts, network["allowed_hosts"])

    if allowed_tools is None:
        allowed_tools = set()
    allowed_tools -= denied_tools
    if not network_enabled:
        allowed_hosts = set()

    return {
        "allow_tools": sorted(allowed_tools),
        "deny_tools": sorted(denied_tools),
        "network": {
            "enabled": network_enabled,
            "allowed_hosts": sorted(allowed_hosts or set()),
        },
    }


def tool_allowed(policy: dict, tool: str) -> bool:
    return tool in policy["allow_tools"] and tool not in policy["deny_tools"]

import json
from policy import effective_policy, tool_allowed

system = {
    "allow_tools": ["shell", "browser", "mcp.read"],
    "network": {"enabled": True, "allowed_hosts": ["github.com", "pypi.org"]},
}
team = {
    "allow_tools": ["shell", "mcp.read"],
    "deny_tools": ["mcp.read"],
    "network": {"enabled": True, "allowed_hosts": ["github.com"]},
}
project = {
    "allow_tools": ["shell"],
    "network": {"enabled": False},
}

policy = effective_policy(system, team, project)
print(json.dumps(policy, indent=2))
print("shell:", tool_allowed(policy, "shell"))
print("browser:", tool_allowed(policy, "browser"))
print("mcp.read:", tool_allowed(policy, "mcp.read"))

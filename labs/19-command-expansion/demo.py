from expansion import CommandPolicy, ExpansionRequest


policy = CommandPolicy(base_network_enabled=False)
request = ExpansionRequest(
    command_id="cmd-001",
    hostname="registry.npmjs.org",
    reason="install project dependencies",
)
print("before approval:", policy.network_allowed("cmd-001", "registry.npmjs.org"))
policy.approve(request)
print("approved command:", policy.network_allowed("cmd-001", "registry.npmjs.org"))
print("next command:", policy.network_allowed("cmd-002", "registry.npmjs.org"))

from policy import CapabilityDenied, ToolBroker


broker = ToolBroker()

checks = [
    ("shell", broker.read_workspace),
    ("browser", broker.fetch_example),
    ("mcp.issue.read", broker.read_issue),
]
for tool, operation in checks:
    print(tool, "=>", operation(tool))

for tool, operation in [
    ("browser", broker.read_workspace),
    ("shell", broker.fetch_example),
    ("mcp.issue.read", broker.read_workspace),
]:
    try:
        operation(tool)
        print("UNEXPECTED ALLOW", tool)
    except CapabilityDenied as exc:
        print("DENY:", exc)

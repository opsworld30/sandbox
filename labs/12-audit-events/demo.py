from audit import emit


emit(
    "tool.exec.denied",
    "session-demo-001",
    {
        "tool": "shell",
        "reason": "network_policy",
        "repository": "example/project",
        "authorization": "Bearer FAKE_DO_NOT_USE",
        "api_key": "ghp_FAKE_NOT_REAL",
        "raw_output": "request used Bearer FAKE_DO_NOT_USE",
    },
)

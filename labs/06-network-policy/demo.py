from policy import EgressPolicy


def main() -> None:
    policy = EgressPolicy({"github.com", "pypi.org"})
    cases = [
        "github.com",
        "api.github.com",
        "github.com.evil.test",
        "pypi.org.",
        "127.0.0.1",
        "localhost",
        "https://github.com",
    ]
    for host in cases:
        allowed, reason = policy.decide(host)
        print(f"{host:24} {'ALLOW' if allowed else 'DENY ':5} {reason}")


if __name__ == "__main__":
    main()

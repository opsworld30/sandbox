from runtime import MiniRuntime, PolicyDenied


def main() -> int:
    runtime = MiniRuntime()
    try:
        session = runtime.create_session()
        print("session:", session)
        print("pwd:", runtime.exec(session, ["pwd"]))
        print("read:", runtime.exec(session, ["cat", "README.txt"]))
        print("echo:", runtime.exec(session, ["echo", "hello", "agent"]))
        try:
            runtime.exec(session, ["sh", "-c", "id"])
        except PolicyDenied as exc:
            print("policy denied:", exc)
        runtime.destroy_session(session)
        print("destroyed; workspace exists:", session in runtime.sessions)
        print("audit:", runtime.audit_path.read_text(encoding="utf-8").splitlines())
    finally:
        runtime.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path
import sys

from runner import LocalRunner


def main() -> int:
    workspace = Path(__file__).parent / "workspace"
    workspace.mkdir(exist_ok=True)
    (workspace / "hello.txt").write_text("hello from workspace\n", encoding="utf-8")

    runner = LocalRunner(workspace, timeout=2, max_output_bytes=4096)
    result = runner.run([sys.executable, "-c", "print(open('hello.txt').read())"])
    print(result.output, end="")
    print(f"exit={result.returncode}, timeout={result.timed_out}")

    try:
        runner.run([sys.executable, "-c", "print('should not run')"], cwd="../")
    except PermissionError as exc:
        print(f"workspace guard: DENY ({exc})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

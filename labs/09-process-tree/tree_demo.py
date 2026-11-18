"""Demonstrate process-group cleanup on POSIX systems."""
import os
import signal
import subprocess
import sys
import time


def spawn(role: str) -> None:
    if role == "parent":
        child = subprocess.Popen([sys.executable, __file__, "child"])
        print(f"parent pid={os.getpid()} child_pid={child.pid} pgid={os.getpgrp()}", flush=True)
    elif role == "child":
        child = subprocess.Popen([sys.executable, __file__, "grandchild"])
        print(f"child pid={os.getpid()} grandchild_pid={child.pid} pgid={os.getpgrp()}", flush=True)
    while True:
        time.sleep(1)


def main() -> int:
    if os.name != "posix":
        print("This demo requires POSIX process groups.", file=sys.stderr)
        return 2

    if len(sys.argv) > 1:
        spawn(sys.argv[1])
        return 0

    root = subprocess.Popen(
        [sys.executable, __file__, "parent"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    assert root.stdout is not None
    time.sleep(0.8)
    print(f"root pid / process-group id = {root.pid}")
    print("child process tree:")
    # Read only what is already available; don't block waiting for another line.
    import selectors
    selector = selectors.DefaultSelector()
    selector.register(root.stdout, selectors.EVENT_READ)
    for _ in range(3):
        if selector.select(0.1):
            line = root.stdout.readline()
            if not line:
                break
            print(line.rstrip())
    selector.close()

    print(f"Sending SIGTERM to process group {root.pid}")
    try:
        os.killpg(root.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        root.wait(timeout=3)
    except subprocess.TimeoutExpired:
        os.killpg(root.pid, signal.SIGKILL)
        root.wait()

    print(f"root exit code={root.returncode}")
    print("Process-group cleanup request completed.")
    print("For production, verify no descendant escaped with setsid(); use cgroup v2 on Linux.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

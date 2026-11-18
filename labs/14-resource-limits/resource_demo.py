"""Bounded Linux RLIMIT demonstrations. Run only in a disposable VM."""
import os
import resource
import signal
import sys
import tempfile


def cpu_test() -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (1, 2))
    print("CPU limit set to soft=1s hard=2s; starting bounded busy loop", flush=True)
    value = 0
    while True:
        value = (value + 1) % 1_000_003


def memory_test() -> None:
    limit = 256 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    print("RLIMIT_AS set to 256 MiB; allocating in 8 MiB chunks", flush=True)
    chunks = []
    try:
        while True:
            chunks.append(bytearray(8 * 1024 * 1024))
    except MemoryError:
        print(f"MemoryError after {len(chunks) * 8} MiB of requested chunks")


def file_test() -> None:
    limit = 64 * 1024
    resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))
    signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
    path = os.path.join(tempfile.gettempdir(), "sandbox-lab-resource-output.bin")
    written = 0
    try:
        with open(path, "wb") as output:
            block = b"x" * 8192
            while True:
                output.write(block)
                written += len(block)
    except OSError as exc:
        print(f"write stopped after approximately {written} bytes: {exc}")
    finally:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    if sys.platform != "linux":
        raise SystemExit("This lab requires Linux.")
    modes = {"cpu": cpu_test, "memory": memory_test, "file": file_test}
    if len(sys.argv) != 2 or sys.argv[1] not in modes:
        raise SystemExit(f"usage: {sys.argv[0]} cpu|memory|file")
    modes[sys.argv[1]]()

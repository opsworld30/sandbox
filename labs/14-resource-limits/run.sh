#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ "$(uname -s)" == "Linux" ]] || { echo "Linux only" >&2; exit 2; }
command -v timeout >/dev/null 2>&1 || { echo "Install coreutils (timeout)" >&2; exit 127; }

echo "== CPU time limit =="
set +e
timeout --signal=TERM --kill-after=1s 4s python3 "$ROOT/resource_demo.py" cpu
CPU_STATUS=$?
set -e
echo "CPU test exit=$CPU_STATUS (non-zero is expected when RLIMIT_CPU fires)"

echo
echo "== Address-space limit =="
python3 "$ROOT/resource_demo.py" memory

echo
echo "== File-size limit =="
python3 "$ROOT/resource_demo.py" file

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$ROOT/../.." && pwd)"

run_tests() {
  local directory="$1"
  echo
  echo "===== $directory ====="
  (cd "$REPO_ROOT/$directory" && python3 -m unittest -v)
}

run_tests "labs/06-network-policy"
run_tests "labs/08-policy-engine"
run_tests "labs/15-tool-capabilities"
run_tests "labs/17-mini-runtime"

echo
echo "All application-layer regression tests passed."

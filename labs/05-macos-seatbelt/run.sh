#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$ROOT/workspace"
OUTSIDE="$ROOT/outside"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This lab only runs on macOS." >&2
  exit 2
fi
command -v sandbox-exec >/dev/null 2>&1 || {
  echo "sandbox-exec is unavailable on this macOS version." >&2
  exit 127
}
mkdir -p "$WORKSPACE" "$OUTSIDE"
[[ -f "$WORKSPACE/allowed.txt" ]] || echo "allowed" > "$WORKSPACE/allowed.txt"
[[ -f "$OUTSIDE/secret.txt" ]] || echo "secret" > "$OUTSIDE/secret.txt"

echo "Expect the first read to succeed and the second to be denied."
sandbox-exec -D "WORKSPACE=$WORKSPACE" -f "$ROOT/profile.sb" -- /bin/sh -c '
  echo "--- allowed file ---"
  /bin/cat "$1/allowed.txt"
  echo "--- outside file (expected denial) ---"
  if /bin/cat "$2/secret.txt"; then
    echo "UNEXPECTED: outside file was readable"
    exit 10
  else
    echo "DENIED as expected"
  fi
  echo "created by Seatbelt" > "$1/created.txt"
  echo "--- workspace write ---"
  /bin/cat "$1/created.txt"
' sh "$WORKSPACE" "$OUTSIDE"

#!/usr/bin/env bash
set -euo pipefail

command -v npm >/dev/null 2>&1 || {
  echo "npm is required (Node.js installation)." >&2
  exit 127
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp "$ROOT/package.json" "$ROOT/postinstall.js" "$TMP/"
cd "$TMP"

echo "== Phase 1: ignore lifecycle scripts =="
npm install --ignore-scripts --package-lock=false --no-audit --no-fund
if [[ -e postinstall-ran.txt ]]; then
  echo "ERROR: postinstall unexpectedly ran" >&2
  exit 1
fi
echo "PASS: marker absent"

echo
echo "== Phase 2: allow lifecycle scripts =="
npm install --ignore-scripts=false --package-lock=false --no-audit --no-fund
if [[ ! -e postinstall-ran.txt ]]; then
  echo "ERROR: postinstall did not run" >&2
  exit 1
fi
echo "PASS: marker created"
cat postinstall-ran.txt

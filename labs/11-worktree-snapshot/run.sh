#!/usr/bin/env bash
set -euo pipefail

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
REPO="$TMP/repo"
WORKTREE="$TMP/agent-a"

mkdir -p "$REPO"
cd "$REPO"
git init -q
git config user.name "Sandbox Lab"
git config user.email "sandbox-lab@example.invalid"
printf 'base version\n' > app.txt
git add app.txt
git commit -qm "baseline"

git worktree add -qb agent-a "$WORKTREE"
printf 'changed by agent A\n' >> "$WORKTREE/app.txt"
git -C "$WORKTREE" add app.txt
git -C "$WORKTREE" commit -qm "agent A change"

echo "== Worktrees =="
git worktree list
echo
echo "== Agent A commit =="
git -C "$WORKTREE" log -1 --oneline
echo
echo "== Export immutable source snapshot =="
git -C "$WORKTREE" archive --format=tar HEAD > "$TMP/agent-a-snapshot.tar"
tar -tf "$TMP/agent-a-snapshot.tar"
echo
echo "Snapshot bytes: $(wc -c < "$TMP/agent-a-snapshot.tar" | tr -d ' ')"

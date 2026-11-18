#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${ROOT}/workspace"
MODE="${1:-run}"

command -v bwrap >/dev/null 2>&1 || {
  echo "bwrap not found. Install bubblewrap first." >&2
  exit 127
}
[[ -d "$WORKSPACE" ]] || {
  echo "Create $WORKSPACE and add hello.txt first." >&2
  exit 2
}

args=(
  --die-with-parent
  --clearenv
  --unshare-user
  --unshare-pid
  --unshare-ipc
  --unshare-uts
  --unshare-net
  --ro-bind /usr /usr
  --ro-bind /bin /bin
  --ro-bind /etc /etc
  --proc /proc
  --dev /dev
  --tmpfs /tmp
  --dir /home
  --dir /home/sandbox
  --bind "$WORKSPACE" /workspace
  --chdir /workspace
  --setenv HOME /home/sandbox
  --setenv PATH /usr/bin:/bin
)

for libdir in /lib /lib64; do
  if [[ -d "$libdir" ]]; then
    args+=(--ro-bind "$libdir" "$libdir")
  fi
done

if [[ "$MODE" == "--check" ]]; then
  exec bwrap "${args[@]}" /bin/sh -c '
    echo "workspace:"
    cat /workspace/hello.txt
    echo "write test" > /workspace/sandbox-write-test.txt
    test -f /workspace/sandbox-write-test.txt
    if [ -e /host-secret.txt ]; then
      echo "unexpected host secret visibility" >&2
      exit 10
    fi
    if [ -e /etc/shadow ]; then
      echo "note: /etc is mounted read-only; shadow may be visible to root" >&2
    fi
    echo "network namespace:"
    readlink /proc/self/ns/net
    echo "sandbox check complete"
  '
fi

exec bwrap "${args[@]}" /bin/sh -c '
  echo "Inside Sandbox:"
  pwd
  cat /workspace/hello.txt
  echo "created in Sandbox" > /workspace/created.txt
  echo "Wrote /workspace/created.txt"
  echo "Network namespace:"
  readlink /proc/self/ns/net
'

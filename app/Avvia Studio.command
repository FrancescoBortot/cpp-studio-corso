#!/bin/zsh
cd "${0:A:h}"
if curl --silent --fail http://127.0.0.1:8765/api/status >/dev/null; then
  open 'http://127.0.0.1:8765'
  exit 0
fi
if [[ -f .runtime/root/bin/root-config ]]; then
  PYTHONDONTWRITEBYTECODE=1 python3 tools/configure_root.py || exit 1
fi
PYTHONDONTWRITEBYTECODE=1 python3 server.py &
studio_pid=$!
trap 'kill "$studio_pid" 2>/dev/null' EXIT INT TERM
for attempt in {1..30}; do
  if curl --silent --fail http://127.0.0.1:8765/api/status >/dev/null; then
    open 'http://127.0.0.1:8765'
    break
  fi
  sleep 0.2
done
wait "$studio_pid"

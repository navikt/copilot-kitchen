#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8765}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URL="http://localhost:${PORT}/"

cd "$DIR"

# Frigjør porten hvis noe annet holder den
existing_pid="$(lsof -ti :"$PORT" 2>/dev/null || true)"
if [ -n "$existing_pid" ]; then
  echo "Stopper eksisterende prosess på port $PORT (pid $existing_pid)…"
  kill "$existing_pid" 2>/dev/null || true
  sleep 0.3
fi

# Start server i bakgrunnen
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!

cleanup() {
  echo ""
  echo "Stopper server (pid $SERVER_PID)…"
  kill "$SERVER_PID" 2>/dev/null || true
  wait "$SERVER_PID" 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM

# Gi serveren et øyeblikk på å våkne
sleep 0.4

# Åpne default browser
open "$URL"

echo ""
echo "  ┌─────────────────────────────────────────────┐"
echo "  │  Hovmester-presentasjon kjører              │"
echo "  │  → $URL                  │"
echo "  │                                             │"
echo "  │  Piltaster  navigere                        │"
echo "  │  F         fullscreen                       │"
echo "  │  S         presenter mode (speaker notes)   │"
echo "  │  O         oversikt over alle slides        │"
echo "  │  ?         alle shortcuts                   │"
echo "  │                                             │"
echo "  │  Ctrl+C    stoppe server                    │"
echo "  └─────────────────────────────────────────────┘"
echo ""

# Hold i live til Ctrl+C
wait "$SERVER_PID"

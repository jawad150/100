#!/bin/bash
# Bespoke Bathroom UK · Social Studio (Mac): double-click to start.
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is not installed. Download it from https://nodejs.org (LTS), then double-click this file again."
  read -r -p "Press Enter to close."
  exit 1
fi
[ -d node_modules ] || npm install --no-fund --no-audit
(sleep 2 && open "http://localhost:${PORT:-4321}") &
node server.js

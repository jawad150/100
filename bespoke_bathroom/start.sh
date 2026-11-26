#!/bin/bash
# Bespoke Bathroom UK · Social Studio (Mac or Linux): run ./start.sh
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is not installed. Download it from https://nodejs.org (LTS), then run this again."
  read -r -p "Press Enter to close."
  exit 1
fi
[ -d node_modules ] || npm install --no-fund --no-audit
(sleep 2 && { command -v open >/dev/null && open "http://localhost:${PORT:-4321}" || xdg-open "http://localhost:${PORT:-4321}"; }) &
node server.js

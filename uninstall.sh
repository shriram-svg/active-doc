#!/usr/bin/env bash
# active-doc uninstaller.
# Stops the background job and removes installed files.
# Your notes file (~/active-doc/notes.md) is LEFT ALONE.

set -e

PLIST="$HOME/Library/LaunchAgents/com.activedoc.engine.plist"

if [[ "$(uname)" == "Darwin" ]] && [ -f "$PLIST" ]; then
  launchctl unload "$PLIST" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Stopped and removed background job."
fi

rm -f "$HOME/active-doc/engine.py"
rm -f "$HOME/active-doc/notes.md.state.json"

echo "Uninstalled. Your notes file at ~/active-doc/notes.md was kept."
echo "Delete it manually if you want: rm -rf ~/active-doc"

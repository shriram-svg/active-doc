#!/usr/bin/env bash
# active-doc installer — one command, zero config.
#
# What this does:
#   1. Creates ~/active-doc/  (your notes live here)
#   2. Downloads the engine
#   3. Creates notes.md if it doesn't exist
#   4. On macOS: installs a background job that re-ranks every 30s
#   5. Prints where your notes file is
#
# Run:
#   curl -fsSL https://raw.githubusercontent.com/shriram-svg/active-doc/master/install.sh | bash

set -e

REPO="https://raw.githubusercontent.com/shriram-svg/active-doc/master"
DIR="$HOME/active-doc"
NOTES="$DIR/notes.md"
ENGINE="$DIR/engine.py"
PLIST="$HOME/Library/LaunchAgents/com.activedoc.engine.plist"

echo ""
echo "Setting up active-doc..."
echo ""

# 1. Python check
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: Python 3 is not installed."
  echo "On macOS, install it by running:  xcode-select --install"
  echo "Or download from: https://www.python.org/downloads/"
  exit 1
fi

# 2. Make the folder
mkdir -p "$DIR"

# 3. Download the engine
echo "Downloading the engine..."
curl -fsSL "$REPO/engine.py" -o "$ENGINE"
chmod +x "$ENGINE"

# 4. Create starter notes file (don't overwrite existing)
if [ ! -f "$NOTES" ]; then
  cat > "$NOTES" <<'EOF'
# My Notes

Write anything here — meeting notes, thoughts, reminders.

Any line that sounds like something you need to do will bubble to the top.

Try it: add a few lines like these below, then save.

Need to call the plumber
IMPORTANT: renew passport
Waiting on sign-off from Sam
Should email Mom about Sunday
EOF
  echo "Created starter notes at: $NOTES"
fi

# 5. macOS: install launchd agent so it runs in the background
if [[ "$(uname)" == "Darwin" ]]; then
  mkdir -p "$HOME/Library/LaunchAgents"

  # Unload old one if present (ignore errors)
  launchctl unload "$PLIST" 2>/dev/null || true

  cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.activedoc.engine</string>
    <key>ProgramArguments</key>
    <array>
      <string>$(command -v python3)</string>
      <string>$ENGINE</string>
      <string>$NOTES</string>
    </array>
    <key>StartInterval</key>
    <integer>30</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/active-doc.out.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/active-doc.err.log</string>
  </dict>
</plist>
EOF

  launchctl load "$PLIST"
  BG_STATUS="running every 30 seconds in the background"
else
  # Linux / other — just run once, give instructions for continuous
  python3 "$ENGINE" "$NOTES" >/dev/null
  BG_STATUS="not started automatically (macOS only). To keep it running: python3 $ENGINE $NOTES --watch 30"
fi

# 6. First run
python3 "$ENGINE" "$NOTES" >/dev/null

echo ""
echo "Done."
echo ""
echo "Your notes file:  $NOTES"
echo "Background job:   $BG_STATUS"
echo ""
echo "Open your notes:"
if [[ "$(uname)" == "Darwin" ]]; then
  echo "  open \"$NOTES\""
else
  echo "  xdg-open \"$NOTES\""
fi
echo ""
echo "Write anything. Save. The top of the file will update automatically."
echo ""
echo "To uninstall:  curl -fsSL $REPO/uninstall.sh | bash"
echo ""

#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# daily-claude setup
# One-click installer for macOS
# https://github.com/nawzaysfinah/daily-claude
# ──────────────────────────────────────────────────────────────────────────────

set -e

REPO_URL="https://github.com/nawzaysfinah/daily-claude"
RAW_URL="https://raw.githubusercontent.com/nawzaysfinah/daily-claude/main"
INSTALL_DIR="$HOME/Desktop"
APP_NAME="Add Task.app"

echo ""
echo "  ┌─────────────────────────────────────┐"
echo "  │         daily-claude setup          │"
echo "  │   Your AI-powered morning OS 🌅     │"
echo "  └─────────────────────────────────────┘"
echo ""

# ── Check macOS ───────────────────────────────────────────────────────────────
if [[ "$OSTYPE" != "darwin"* ]]; then
  echo "❌  daily-claude currently requires macOS."
  exit 1
fi

echo "✓  macOS detected"

# ── Download AddTask.app ──────────────────────────────────────────────────────
echo "→  Downloading Add Task app..."

TMP_DIR=$(mktemp -d)
APP_DEST="$INSTALL_DIR/$APP_NAME"

# Download the app bundle files
mkdir -p "$TMP_DIR/$APP_NAME/Contents/MacOS"

curl -fsSL "$RAW_URL/AddTask.app/Contents/MacOS/AddTask" \
  -o "$TMP_DIR/$APP_NAME/Contents/MacOS/AddTask"

curl -fsSL "$RAW_URL/AddTask.app/Contents/Info.plist" \
  -o "$TMP_DIR/$APP_NAME/Contents/Info.plist"

chmod +x "$TMP_DIR/$APP_NAME/Contents/MacOS/AddTask"

# Remove old version if exists
[ -d "$APP_DEST" ] && rm -rf "$APP_DEST"

# Install to Desktop
cp -r "$TMP_DIR/$APP_NAME" "$APP_DEST"
rm -rf "$TMP_DIR"

echo "✓  Add Task app installed to Desktop"

# ── Remove quarantine flag (so macOS doesn't block it) ───────────────────────
xattr -dr com.apple.quarantine "$APP_DEST" 2>/dev/null || true
echo "✓  Security quarantine cleared"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "  ✅  Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Double-click 'Add Task' on your Desktop to add your first task"
echo "     (it will ask you where to store your TASKS.md on first launch)"
echo ""
echo "  2. Set up your daily morning briefing in Claude Cowork:"
echo "     → Open Claude Cowork"
echo "     → Ask Claude: 'Schedule a daily morning briefing at 8am'"
echo "     → Point it to your TASKS.md when prompted"
echo ""
echo "  3. Star the repo if you find it useful ⭐"
echo "     $REPO_URL"
echo ""

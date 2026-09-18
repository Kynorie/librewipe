#!/usr/bin/env bash

set -e

SCRIPT_NAME="librewipe.py"
COMMAND_NAME="librewipe"

if [ ! -f "$SCRIPT_NAME" ]; then
    echo "[x] $SCRIPT_NAME not found. Run this from the LibreWipe folder."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "[x] python3 is not installed. Install it and try again."
    exit 1
fi

if [ "$(id -u)" -eq 0 ]; then
    TARGET_DIR="/usr/local/bin"
else
    TARGET_DIR="$HOME/.local/bin"
fi

TARGET="$TARGET_DIR/$COMMAND_NAME"

echo "[-] Installing LibreWipe to $TARGET..."

mkdir -p "$TARGET_DIR"
cp "$SCRIPT_NAME" "$TARGET"
chmod +x "$TARGET"

echo "[+] Installed!"

case ":$PATH:" in
    *":$TARGET_DIR:"*)
        echo "[+] Run it with: librewipe --start"
        ;;
    *)
        echo "[!] $TARGET_DIR is not in your PATH."
        echo "    Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo "    Then restart your terminal."
        ;;
esac

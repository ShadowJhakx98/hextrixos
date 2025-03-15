#!/bin/bash
# Direct runner script for Hextrix AI OS that avoids PowerShell

# Define the project directory
HEXTRIX_DIR="$(pwd)"
cd "$HEXTRIX_DIR"

# Set GI_TYPELIB_PATH to include system typelib directories
echo "Setting up GObject introspection paths..."
export GI_TYPELIB_PATH="/usr/lib/x86_64-linux-gnu/girepository-1.0:/usr/lib/girepository-1.0:$GI_TYPELIB_PATH"

# Add the AI modules to Python path
export PYTHONPATH="$PYTHONPATH:$HEXTRIX_DIR:$HEXTRIX_DIR/ai:$HEXTRIX_DIR/hud"

# Ensure we're using the virtual environment's Python
VENV_PYTHON="$HEXTRIX_DIR/hextrix/bin/python3"

# Direct execution of the HUD main script
echo "Starting Hextrix AI OS directly..."
cd "$HEXTRIX_DIR"
"$VENV_PYTHON" "$HEXTRIX_DIR/hud/main.py" 
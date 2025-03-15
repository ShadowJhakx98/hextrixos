#!/bin/bash
# Quick script to run Hextrix AI OS with the correct Python environment

# Define the project directory
HEXTRIX_DIR="/home/jared/hextrix-ai-os-env"

# Set GI_TYPELIB_PATH to include system typelib directories
echo "Setting up GObject introspection paths..."
export GI_TYPELIB_PATH="/usr/lib/x86_64-linux-gnu/girepository-1.0:/usr/lib/girepository-1.0:$GI_TYPELIB_PATH"

# Add the AI modules to Python path
export PYTHONPATH="$PYTHONPATH:$HEXTRIX_DIR:$HEXTRIX_DIR/ai"

# Run the application using the main.py wrapper script
echo "Starting Hextrix AI OS..."
python "$HEXTRIX_DIR/main.py"

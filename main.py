#!/usr/bin/env python3
# Main entry point for Hextrix AI OS

import os
import sys
import subprocess

def main():
    # Get the absolute path of this script
    script_path = os.path.abspath(__file__)
    project_dir = os.path.dirname(script_path)
    
    # Define the path to the virtual environment
    venv_path = os.path.join(project_dir, "hextrix")
    
    # Define the path to the main application script
    hud_main_path = os.path.join(project_dir, "hud", "main.py")
    
    # Ensure PYTHONPATH includes necessary directories
    python_path = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = f"{python_path}:{project_dir}:{os.path.join(project_dir, 'ai')}:{os.path.join(project_dir, 'hud')}"
    
    # Execute the main.py file using the virtual environment's Python
    python_exe = os.path.join(venv_path, "bin", "python")
    
    print(f"Launching Hextrix AI OS with {python_exe}")
    subprocess.run([python_exe, hud_main_path])

if __name__ == "__main__":
    main()

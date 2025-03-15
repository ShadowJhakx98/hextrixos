#!/usr/bin/env python3
# Debug script to run Hextrix AI OS and capture errors

import os
import sys
import subprocess
import traceback

def main():
    try:
        # Get the absolute path of this script
        script_path = os.path.abspath(__file__)
        project_dir = os.path.dirname(script_path)
        
        # Define the path to the virtual environment
        venv_path = os.path.join(project_dir, "hextrix")
        
        # Define the path to the main application script
        hud_main_path = os.path.join(project_dir, "hud", "main.py")
        
        # Set up environment
        os.environ["PYTHONPATH"] = f"{os.environ.get('PYTHONPATH', '')}:{project_dir}:{os.path.join(project_dir, 'ai')}:{os.path.join(project_dir, 'hud')}"
        
        print(f"Starting Hextrix OS with {venv_path}")
        
        # Save original stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Open log file
        log_file = open(os.path.join(project_dir, "hextrix_debug.log"), "w")
        sys.stdout = log_file
        sys.stderr = log_file
        
        # Execute the main.py file using the virtual environment's Python
        python_exe = os.path.join(venv_path, "bin", "python")
        result = subprocess.run(
            [python_exe, hud_main_path],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Log the result
        log_file.write("\n\n----- STDOUT -----\n")
        log_file.write(result.stdout)
        log_file.write("\n\n----- STDERR -----\n")
        log_file.write(result.stderr)
        log_file.write(f"\n\nExit code: {result.returncode}\n")
        
        # Restore stdout/stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        print(f"Hextrix OS exited with code {result.returncode}")
        print(f"See {os.path.join(project_dir, 'hextrix_debug.log')} for details")
        
    except Exception as e:
        print(f"Error running Hextrix OS: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 
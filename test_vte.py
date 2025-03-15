#!/usr/bin/env python3
import gi
import sys
import os

# Print Python and gi versions for debugging
print(f"Python version: {sys.version}")
print(f"gi version: {gi.__version__}")

# Print GI_TYPELIB_PATH environment variable
print("\nGI_TYPELIB_PATH:")
gi_typelib_path = os.environ.get('GI_TYPELIB_PATH', 'Not set')
print(gi_typelib_path)

# List system typelib directories
print("\nChecking system typelib directories:")
typelib_dirs = [
    "/usr/lib/x86_64-linux-gnu/girepository-1.0",
    "/usr/lib/girepository-1.0"
]

for dir_path in typelib_dirs:
    if os.path.exists(dir_path):
        print(f"\nDirectory {dir_path} exists. Contents:")
        files = os.listdir(dir_path)
        vte_files = [f for f in files if f.startswith("Vte")]
        if vte_files:
            print(f"VTE typelibs found: {vte_files}")
        else:
            print("No VTE typelibs found")
    else:
        print(f"\nDirectory {dir_path} does not exist")

try:
    # Try to import VTE
    gi.require_version('Vte', '2.91')
    from gi.repository import Vte
    print("\nSuccess! VTE module was imported successfully.")
except ValueError as e:
    print(f"\nError: {e}")
    print("\nTroubleshooting steps:")
    print("1. Make sure the system has VTE typelib installed:")
    print("   sudo apt install -y gir1.2-vte-2.91")
    print("\n2. Try setting GI_TYPELIB_PATH environment variable:")
    print("   export GI_TYPELIB_PATH=/usr/lib/x86_64-linux-gnu/girepository-1.0:/usr/lib/girepository-1.0:$GI_TYPELIB_PATH")
    print("\n3. Check if PyGObject is properly installed in the conda environment:")
    print("   pip install PyGObject")
except Exception as e:
    print(f"\nUnexpected error: {e}") 
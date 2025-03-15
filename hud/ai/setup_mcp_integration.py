#!/usr/bin/env python3
# Script to set up integration between the AI (app.py) and MCP

import os
import sys
import importlib.util
import subprocess
import shutil

# Path constants
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
HEXTRIX_MCP_DIR = "/home/jared/hextrix-ai-os-env/hextrix_mcp"
INTEGRATION_FILE = os.path.join(CURRENT_DIR, "mcp_integration.py")
EXTENSION_FILE = os.path.join(CURRENT_DIR, "app_mcp_extension.py")
HOOK_SUPPORT_FILE = os.path.join(CURRENT_DIR, "message_hook_support.py")
MAIN_APP_FILE = os.path.join(CURRENT_DIR, "app.py")
APP_INIT_FILE = os.path.join(CURRENT_DIR, "__init__.py")

def check_mcp_client():
    """Check if MCP client is available and correctly configured"""
    mcp_client_path = os.path.join(HEXTRIX_MCP_DIR, "mcp_client.py")
    
    if not os.path.exists(mcp_client_path):
        print(f"Error: MCP client not found at {mcp_client_path}")
        return False
    
    print(f"Found MCP client at {mcp_client_path}")
    return True

def check_integration_files():
    """Check if the integration files exist"""
    missing_files = []
    
    if not os.path.exists(INTEGRATION_FILE):
        missing_files.append(INTEGRATION_FILE)
    
    if not os.path.exists(EXTENSION_FILE):
        missing_files.append(EXTENSION_FILE)
    
    if not os.path.exists(HOOK_SUPPORT_FILE):
        missing_files.append(HOOK_SUPPORT_FILE)
    
    if missing_files:
        print("Error: The following integration files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("Integration files found:")
    print(f"  - {INTEGRATION_FILE}")
    print(f"  - {EXTENSION_FILE}")
    print(f"  - {HOOK_SUPPORT_FILE}")
    return True

def check_main_app():
    """Check if the main app.py exists"""
    if not os.path.exists(MAIN_APP_FILE):
        print(f"Error: Main app not found at {MAIN_APP_FILE}")
        return False
    
    print(f"Found main app at {MAIN_APP_FILE}")
    return True

def create_backup(file_path):
    """Create a backup of a file"""
    backup_path = file_path + ".bak"
    
    # Remove old backup if it exists
    if os.path.exists(backup_path):
        os.remove(backup_path)
    
    # Create new backup
    shutil.copy2(file_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    return True

def modify_app_file():
    """Add code to import and initialize the MCP extension in app.py"""
    # First create a backup
    if not create_backup(MAIN_APP_FILE):
        return False
    
    # Read the file
    with open(MAIN_APP_FILE, "r") as f:
        lines = f.readlines()
    
    # Check if integration is already added
    for line in lines:
        if "app_mcp_extension" in line:
            print("MCP extension already imported in app.py")
            return True
    
    # Find where to insert import
    import_position = None
    for i, line in enumerate(lines):
        if line.startswith("# Import our modules"):
            import_position = i + 1
            break
    
    if import_position is None:
        # Try to find another suitable position
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_position = i
    
    if import_position is None:
        print("Error: Could not find a suitable position to insert import")
        return False
    
    # Insert import
    lines.insert(import_position, "# Import MCP extension\n")
    lines.insert(import_position + 1, "try:\n")
    lines.insert(import_position + 2, "    from app_mcp_extension import inject_mcp_extension\n")
    lines.insert(import_position + 3, "except ImportError:\n")
    lines.insert(import_position + 4, "    print(\"Warning: MCP extension not available\")\n")
    lines.insert(import_position + 5, "    inject_mcp_extension = None\n")
    lines.insert(import_position + 6, "\n")
    
    # Find where to initialize the extension
    init_position = None
    for i, line in enumerate(lines):
        # Look for app initialization or main function
        if "if __name__ == \"__main__\":" in line:
            # Find a suitable position after the app is created
            for j in range(i, len(lines)):
                if "app = Flask" in lines[j]:
                    init_position = j + 1
                    break
            break
    
    if init_position is None:
        # Try to find app initialization differently
        for i, line in enumerate(lines):
            if "app = Flask" in line:
                init_position = i + 1
                break
    
    if init_position is None:
        print("Error: Could not find app initialization")
        return False
    
    # Insert initialization
    lines.insert(init_position, "\n# Initialize MCP extension\n")
    lines.insert(init_position + 1, "if inject_mcp_extension:\n")
    lines.insert(init_position + 2, "    try:\n")
    lines.insert(init_position + 3, "        mcp_extension = inject_mcp_extension(app)\n")
    lines.insert(init_position + 4, "        print(\"MCP extension initialized successfully\")\n")
    lines.insert(init_position + 5, "    except Exception as e:\n")
    lines.insert(init_position + 6, "        print(f\"Error initializing MCP extension: {e}\")\n")
    
    # Write the modified file
    with open(MAIN_APP_FILE, "w") as f:
        f.writelines(lines)
    
    print("Modified app.py to initialize MCP extension")
    return True

def check_and_create_init():
    """Ensure __init__.py exists to make the directory a package"""
    if not os.path.exists(APP_INIT_FILE):
        with open(APP_INIT_FILE, "w") as f:
            f.write("# Make the directory a package\n")
        print(f"Created {APP_INIT_FILE}")
    
    return True

def main():
    """Main function to set up MCP integration"""
    print("Setting up MCP integration with app.py...")
    
    # Check if all required components are available
    if not check_mcp_client():
        sys.exit(1)
    
    if not check_integration_files():
        sys.exit(1)
    
    if not check_main_app():
        sys.exit(1)
    
    # Ensure directory is a package
    if not check_and_create_init():
        sys.exit(1)
    
    # Modify app.py to initialize the MCP extension
    if not modify_app_file():
        sys.exit(1)
    
    print("\nSetup completed successfully!")
    print("The MCP integration should now be available in app.py")
    print("You can test it by running app.py and using commands like:")
    print("  - \"list windows apps\"")
    print("  - \"run notepad app\"")
    print("  - \"find images sunset\"")
    print("  - \"voice command: open calculator\"")

if __name__ == "__main__":
    main() 
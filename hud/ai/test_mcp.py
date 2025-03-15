#!/usr/bin/env python3
# Test script for MCP integration

import os
import sys

# Add parent directory to path
sys.path.append('/home/jared/hextrix-ai-os-env')

# Try to import MCP client
try:
    from hextrix_mcp.mcp_client import HextrixMCPClient
    print("Successfully imported HextrixMCPClient!")
    
    # Initialize client
    client = HextrixMCPClient(base_url="http://localhost:3000")
    print("Initialized MCP client")
    
    # Try to get capabilities
    try:
        capabilities = client.get_capabilities()
        print("Successfully retrieved capabilities:")
        for capability, enabled in capabilities.items():
            print(f"  - {capability}: {'Enabled' if enabled else 'Disabled'}")
    except Exception as e:
        print(f"Error getting capabilities: {e}")
    
except ImportError as e:
    print(f"ERROR: Could not import HextrixMCPClient: {e}")
    print("\nImport path:")
    print(f"sys.path = {sys.path}")
    
    # Check if the file exists
    mcp_client_path = '/home/jared/hextrix-ai-os-env/hextrix_mcp/mcp_client.py'
    if os.path.exists(mcp_client_path):
        print(f"\nThe file {mcp_client_path} exists")
        
        # Check if it's a module
        if os.path.exists('/home/jared/hextrix-ai-os-env/hextrix_mcp/__init__.py'):
            print("hextrix_mcp is a proper module with __init__.py")
        else:
            print("WARNING: hextrix_mcp lacks __init__.py, so it's not a proper module")
            
            # Create the __init__.py file
            try:
                with open('/home/jared/hextrix-ai-os-env/hextrix_mcp/__init__.py', 'w') as f:
                    f.write("# Make hextrix_mcp a proper package\n")
                print("Created __init__.py file to make hextrix_mcp a proper package")
                
                # Try importing again
                try:
                    from hextrix_mcp.mcp_client import HextrixMCPClient
                    print("Successfully imported HextrixMCPClient after creating __init__.py!")
                except ImportError as e2:
                    print(f"Still could not import after creating __init__.py: {e2}")
            except Exception as e:
                print(f"Error creating __init__.py: {e}")
    else:
        print(f"\nERROR: The file {mcp_client_path} does not exist")

print("\nTest completed.") 
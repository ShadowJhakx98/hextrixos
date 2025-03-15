#!/usr/bin/env python3
# Test script for MCP integration module

import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

try:
    import mcp_integration
    print("Successfully imported MCP integration!")
    print(f"MCP integration class: {mcp_integration.MCPIntegration}")
    
    # Create an instance
    mcp = mcp_integration.MCPIntegration()
    print("Created MCPIntegration instance")
    
    # Check what client was loaded
    print(f"MCP client: {mcp.mcp.__class__.__name__}")
    
    # Test server capabilities
    print("\nTesting server capabilities:")
    capabilities = mcp.refresh_capabilities()
    if capabilities:
        print("Server capabilities successfully retrieved!")
        print(f"Capabilities: {mcp.capabilities}")
    else:
        print("Failed to retrieve server capabilities")
    
    # Test file operations
    print("\nTesting file operations:")
    try:
        result = mcp.search_files("README", "/home/jared/hextrix-ai-os-env", recursive=True)
        if isinstance(result, dict) and "error" in result:
            print(f"Error searching for files: {result['error']}")
        else:
            print(f"Found {len(result)} README files:")
            for file in result[:5] if result else []:  # Show only the first 5 files
                print(f"  - {file}")
            if result and len(result) > 5:
                print(f"  ... and {len(result) - 5} more")
    except Exception as e:
        print(f"Error testing file operations: {e}")
    
    # Test Windows app operations (if available)
    print("\nTesting Windows app operations:")
    try:
        result = mcp.list_windows_apps()
        if isinstance(result, dict) and "error" in result:
            print(f"Error listing Windows apps: {result['error']}")
        else:
            print(f"Found {len(result)} Windows apps:")
            for app in result[:5] if result else []:  # Show only the first 5 apps
                if isinstance(app, dict) and 'name' in app:
                    print(f"  - {app['name']}")
            if result and len(result) > 5:
                print(f"  ... and {len(result) - 5} more")
    except Exception as e:
        print(f"Error testing Windows app operations: {e}")
    
    # Test Android app operations (if available)
    print("\nTesting Android app operations:")
    try:
        result = mcp.list_android_apps()
        if isinstance(result, dict) and "error" in result:
            print(f"Error listing Android apps: {result['error']}")
        else:
            print(f"Found {len(result) if result else 0} Android apps:")
            if result and isinstance(result, list):
                for app in result[:5]:  # Show only the first 5 apps
                    if isinstance(app, dict) and 'name' in app:
                        print(f"  - {app['name']}")
                if len(result) > 5:
                    print(f"  ... and {len(result) - 5} more")
    except Exception as e:
        print(f"Error testing Android app operations: {e}")
    
except ImportError as e:
    print(f"Failed to import MCP integration: {e}")
    
print("\nTest completed.") 
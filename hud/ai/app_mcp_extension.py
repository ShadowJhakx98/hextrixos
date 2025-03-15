#!/usr/bin/env python3
# Extension for app.py to integrate MCP functionality
# This file adds system control capabilities to the main AI

import os
import sys
import json
import re
import importlib.util
import threading

# Try to import our MCP integration
try:
    from mcp_integration import MCPIntegration
except ImportError:
    # Try to find it in the current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    mcp_integration_path = os.path.join(current_dir, 'mcp_integration.py')
    
    if os.path.exists(mcp_integration_path):
        # Import from file path
        spec = importlib.util.spec_from_file_location("mcp_integration", mcp_integration_path)
        mcp_integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_integration)
        MCPIntegration = mcp_integration.MCPIntegration
    else:
        # Create a dummy class if integration is not available
        class MCPIntegration:
            def __init__(self):
                print("Warning: MCP Integration module not available")
                self.available = False
                
            def process_voice_command(self, command):
                return {"error": "MCP Integration not available"}

# Try to import message hook support
try:
    from message_hook_support import integrate_hooks_with_app
except ImportError:
    # Create a dummy function if the module is not available
    def integrate_hooks_with_app(app, extension):
        print("Warning: Message hook support not available")
        return False

class HextrixMCPExtension:
    """Extension to add MCP capabilities to the main AI application"""
    
    def __init__(self, app_instance=None):
        """Initialize the MCP extension"""
        self.app = app_instance
        self.mcp = MCPIntegration()
        
        # Register command patterns
        self.command_patterns = [
            # System commands
            (r"(?i)list (windows|android|native) apps", self.handle_list_apps),
            (r"(?i)run (.*) app", self.handle_run_app),
            (r"(?i)open (.*) app", self.handle_run_app),
            (r"(?i)launch (.*) app", self.handle_run_app),
            (r"(?i)start (.*) app", self.handle_run_app),
            
            # File operations
            (r"(?i)find files? (.*)", self.handle_find_files),
            (r"(?i)search files? for (.*)", self.handle_find_files),
            (r"(?i)find (images|photos|pictures) (.*)", self.handle_find_media),
            (r"(?i)find (videos|movies) (.*)", self.handle_find_media),
            (r"(?i)find (documents|docs) (.*)", self.handle_find_media),
            
            # Direct voice command processing
            (r"(?i)voice command: (.*)", self.handle_voice_command),
        ]
        
        # Status flags
        self.initialized = True
        
    def handle_message(self, message):
        """Process a message to see if it matches any system commands"""
        if not hasattr(self, 'initialized') or not self.initialized:
            return None
            
        # Check message against command patterns
        for pattern, handler in self.command_patterns:
            match = re.search(pattern, message)
            if match:
                # Extract groups from the match
                groups = match.groups()
                # Call the handler with the matched groups
                return handler(*groups)
                
        # No command matched
        return None
    
    def handle_list_apps(self, app_type):
        """Handle request to list applications"""
        app_type = app_type.lower()
        
        if app_type == "windows":
            apps = self.mcp.list_windows_apps()
            if isinstance(apps, dict) and "error" in apps:
                return f"Error listing Windows apps: {apps['error']}"
                
            return f"Windows Applications:\n" + "\n".join([f"- {app['name']}" for app in apps])
            
        elif app_type == "android":
            apps = self.mcp.list_android_apps()
            if isinstance(apps, dict) and "error" in apps:
                return f"Error listing Android apps: {apps['error']}"
                
            return f"Android Applications:\n" + "\n".join([f"- {app['name']}" for app in apps])
            
        elif app_type == "native":
            apps = self.mcp.list_native_apps()
            if isinstance(apps, dict) and "error" in apps:
                return f"Error listing native apps: {apps['error']}"
                
            return f"Native Applications:\n" + "\n".join([f"- {app['name']}" for app in apps])
            
        return f"Unknown app type: {app_type}"
    
    def handle_run_app(self, app_name):
        """Handle request to run an application"""
        # First try native apps
        result = self.mcp.launch_native_app(app_name)
        if not isinstance(result, dict) or "error" not in result:
            return f"Launched native application: {app_name}"
            
        # Then try Windows apps
        result = self.mcp.run_windows_app(app_name)
        if not isinstance(result, dict) or "error" not in result:
            return f"Launched Windows application: {app_name}"
            
        # Finally try Android apps
        result = self.mcp.launch_android_app(app_name)
        if not isinstance(result, dict) or "error" not in result:
            return f"Launched Android application: {app_name}"
            
        return f"Could not find or launch application: {app_name}"
    
    def handle_find_files(self, query):
        """Handle request to find files"""
        result = self.mcp.search_files(query)
        
        if isinstance(result, dict) and "error" in result:
            return f"Error searching for files: {result['error']}"
            
        if not result:
            return f"No files found matching: {query}"
            
        return f"Files matching '{query}':\n" + "\n".join([f"- {file}" for file in result[:10]]) + \
               (f"\n... and {len(result) - 10} more files" if len(result) > 10 else "")
    
    def handle_find_media(self, media_type, query):
        """Handle request to find media files"""
        # Map media type to internal representation
        if media_type in ["images", "photos", "pictures"]:
            internal_type = "images"
        elif media_type in ["videos", "movies"]:
            internal_type = "videos"
        elif media_type in ["documents", "docs"]:
            internal_type = "documents"
        else:
            internal_type = "all"
            
        result = self.mcp.find_media(query, internal_type)
        
        if isinstance(result, dict) and "error" in result:
            return f"Error searching for {media_type}: {result['error']}"
            
        if not result:
            return f"No {media_type} found matching: {query}"
            
        return f"{media_type.capitalize()} matching '{query}':\n" + "\n".join([f"- {file}" for file in result[:10]]) + \
               (f"\n... and {len(result) - 10} more files" if len(result) > 10 else "")
    
    def handle_voice_command(self, command):
        """Process a direct voice command"""
        result = self.mcp.process_voice_command(command)
        
        if isinstance(result, dict) and "error" in result:
            return f"Error processing voice command: {result['error']}"
            
        if isinstance(result, dict) and "success" in result and result["success"]:
            action = result.get("action", "unknown action")
            app = result.get("app", "")
            
            if action == "launch_native":
                return f"Launched native application: {app}"
            elif action == "launch_windows":
                return f"Launched Windows application: {app}"
            elif action == "launch_android":
                return f"Launched Android application: {app}"
            else:
                return f"Successfully performed {action} on {app}"
                
        return f"Command processed but returned: {result}"

# Function to inject this extension into the main app
def inject_mcp_extension(app_instance):
    """Inject MCP extension into the main app"""
    # Create extension instance
    extension = HextrixMCPExtension(app_instance)
    
    # Store extension in the app instance
    if not hasattr(app_instance, 'extensions'):
        app_instance.extensions = {}
    app_instance.extensions['mcp'] = extension
    
    # Integrate with message hook support
    try:
        integrate_hooks_with_app(app_instance, extension)
        print("MCP extension integrated with message hooks")
    except Exception as e:
        print(f"Warning: Could not integrate MCP with message hooks: {e}")
        # Fallback: try to register message hook if app has the method
        if hasattr(app_instance, 'register_message_hook'):
            app_instance.register_message_hook(extension.handle_message)
        
    return extension

# Main function for testing
if __name__ == "__main__":
    # Create an instance without app reference for testing
    extension = HextrixMCPExtension()
    
    # Test command handling
    test_commands = [
        "list windows apps",
        "run notepad app",
        "find files report",
        "find images vacation",
        "voice command: open calculator"
    ]
    
    for cmd in test_commands:
        print(f"\nTesting: {cmd}")
        result = extension.handle_message(cmd)
        print(f"Result: {result}") 
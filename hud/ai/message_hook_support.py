#!/usr/bin/env python3
# Message Hook Support Module for Hextrix AI
# This module adds message hook support to the app

import types

def add_message_hooks_to_app(app_instance):
    """Add message hook methods to an app instance
    
    This adds the following methods to the app instance:
    - register_message_hook(hook_function)
    - process_message_hooks(message)
    
    These methods allow the app to process messages through registered hooks
    before normal processing, allowing extensions to intercept and handle messages.
    """
    # Initialize message hooks list if not present
    if not hasattr(app_instance, 'message_hooks'):
        app_instance.message_hooks = []
    
    # Add register_message_hook method
    def register_message_hook(self, hook_function):
        """Register a message hook function to be called for each message
        
        The hook function should accept a message string and return either:
        - None: if the message should be processed normally
        - A response string: if the hook handled the message
        """
        if not hasattr(self, 'message_hooks'):
            self.message_hooks = []
        self.message_hooks.append(hook_function)
        return True
    
    # Add process_message_hooks method
    def process_message_hooks(self, message):
        """Process all registered message hooks with the given message
        
        Returns None if no hook handled the message, otherwise returns
        the response from the first hook that handled the message.
        """
        if not hasattr(self, 'message_hooks'):
            return None
        
        for hook in self.message_hooks:
            result = hook(message)
            if result:
                return result
        
        return None
    
    # Bind methods to the app instance
    app_instance.register_message_hook = types.MethodType(register_message_hook, app_instance)
    app_instance.process_message_hooks = types.MethodType(process_message_hooks, app_instance)
    
    return True

def patch_app_processing_functions(app_instance, mcp_extension):
    """Patch the app's message processing functions to use the hooks
    
    This modified the app's message processing to first check with the 
    registered hooks before normal processing.
    """
    # Store the original message processing function
    if hasattr(app_instance, 'process_ai_response'):
        original_process = app_instance.process_ai_response
        
        # Create a patched version that checks hooks first
        def patched_process_ai_response(self, user_text):
            # Check hooks first
            hook_result = self.process_message_hooks(user_text)
            if hook_result:
                # If a hook handled it, return that result
                return hook_result
            
            # Otherwise, call the original function
            return original_process(user_text)
        
        # Replace the original function with our patched version
        app_instance.process_ai_response = types.MethodType(patched_process_ai_response, app_instance)
    
    return True

def integrate_hooks_with_app(app_instance, extension_instance):
    """Integrate message hooks with the app instance
    
    This is the main entry point to add hook support to an app instance
    and connect it with an extension that implements hooks.
    """
    # Add hook methods to the app
    add_message_hooks_to_app(app_instance)
    
    # Patch message processing to use hooks
    patch_app_processing_functions(app_instance, extension_instance)
    
    # Register the extension's message hook
    if hasattr(extension_instance, 'handle_message'):
        app_instance.register_message_hook(extension_instance.handle_message)
    
    return True 
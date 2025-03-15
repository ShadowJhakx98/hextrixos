async def process_command(self, command: str, source: Union[str, IntegrationType] = None, 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a command through all active integrations or a specific one.
        
        Args:
            command: The command string to process
            source: The source integration type (optional)
            context: Additional context for processing the command
            
        Returns:
            Dictionary containing responses from each integration
        """
        responses = {}
        
        # Convert string source to IntegrationType if needed
        if isinstance(source, str):
            try:
                source = IntegrationType(source)
            except ValueError:
                source = None
        
        # If source specified, only use that integration
        if source and source in self.active_integrations:
            integration = self.integrations[source]
            response = await integration.process_command(command, context)
            responses[source.value] = response
            return responses
        
        # Otherwise, process through all active integrations
        for integration_type in self.active_integrations:
            integration = self.integrations[integration_type]
            try:
                response = await integration.process_command(command, context)
                responses[integration_type.value] = response
            except Exception as e:
                logger.error(f"Error processing command through {integration_type.value}: {str(e)}")
                responses[integration_type.value] = f"Error: {str(e)}"
        
        return responses
    
    async def discover_all_devices(self) -> Dict[str, List[Dict[str, Any]]]:
        """Discover devices across all active integrations."""
        all_devices = {}
        
        for integration_type in self.active_integrations:
            integration = self.integrations[integration_type]
            try:
                devices = await integration.discover_devices()
                all_devices[integration_type.value] = devices
            except Exception as e:
                logger.error(f"Error discovering devices through {integration_type.value}: {str(e)}")
                all_devices[integration_type.value] = []
        
        return all_devices
    
    async def shutdown(self):
        """Shutdown and disconnect all active integrations."""
        for integration_type in list(self.active_integrations):
            integration = self.integrations[integration_type]
            try:
                await integration.disconnect()
                logger.info(f"Disconnected {integration_type.value}")
            except Exception as e:
                logger.error(f"Error disconnecting {integration_type.value}: {str(e)}")
        
        self.active_integrations.clear()
        self.integrations.clear()

# Example usage and setup functions

def setup_alexa_skill(skill_builder):
    """Set up and register the Alexa skill handler."""
    skill_builder.add_request_handler(KairoMindAlexaSkill())
    return skill_builder

async def setup_integrations(config_path=None):
    """Set up all integrations based on configuration."""
    # Load configuration
    config = {}
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    # Create manager and initialize all available integrations
    manager = KairoMindIntegrationManager(config)
    await manager.initialize_integrations()
    
    return manager

# Utility functions for cross-platform integration

def map_capability_to_platforms(capability: DeviceCapability) -> Dict[IntegrationType, str]:
    """Map a generic capability to platform-specific capabilities."""
    # This helps translate between different platforms' terminology
    mapping = {
        DeviceCapability.LIGHT: {
            IntegrationType.ALEXA: "Alexa.BrightnessController",
            IntegrationType.GOOGLE_HOME: "action.devices.traits.Brightness",
            IntegrationType.HOME_ASSISTANT: "light",
            IntegrationType.HOMEKIT: "LightBulb",
            IntegrationType.MATTER: "OnOff"
        },
        DeviceCapability.SWITCH: {
            IntegrationType.ALEXA: "Alexa.PowerController",
            IntegrationType.GOOGLE_HOME: "action.devices.traits.OnOff",
            IntegrationType.HOME_ASSISTANT: "switch",
            IntegrationType.HOMEKIT: "Switch",
            IntegrationType.MATTER: "OnOff"
        },
        # Add mappings for other capabilities
    }
    
    return mapping.get(capability, {})

async def execute_cross_platform_command(
    manager: KairoMindIntegrationManager, 
    command_type: str,
    target_devices: List[Dict[str, Any]],
    parameters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Execute a command across multiple platforms and devices."""
    results = {}
    
    for device in target_devices:
        device_id = device.get("id")
        platform = device.get("platform")
        
        if not device_id or not platform:
            continue
        
        try:
            # Convert to IntegrationType
            integration_type = IntegrationType(platform)
            
            if integration_type not in manager.active_integrations:
                results[device_id] = f"Integration {platform} not active"
                continue
            
            integration = manager.integrations[integration_type]
            
            # Build context based on platform
            context = {"device_id": device_id}
            
            if integration_type == IntegrationType.HOME_ASSISTANT:
                context["entity_id"] = device_id
                context["service"] = command_type
                context["service_data"] = parameters
            elif integration_type == IntegrationType.ALEXA:
                context["endpoint_id"] = device_id
                context["directive"] = command_type
                context["payload"] = parameters
            # Add context building for other platforms
            
            # Execute command
            response = await integration.process_command(command_type, context)
            results[device_id] = response
            
        except Exception as e:
            logger.error(f"Error executing command on {device_id}: {str(e)}")
            results[device_id] = f"Error: {str(e)}"
    
    return results

# Webhook handler for external integrations
async def handle_webhook(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming webhooks from various platforms."""
    platform = request_data.get("platform")
    event_type = request_data.get("event_type")
    payload = request_data.get("payload", {})
    
    logger.info(f"Received webhook from {platform}, event: {event_type}")
    
    # Initialize proper integration to handle the webhook
    try:
        config = {}  # Load from somewhere
        manager = KairoMindIntegrationManager(config)
        
        # Only initialize the relevant integration
        if platform in [t.value for t in IntegrationType]:
            integration_type = IntegrationType(platform)
            await manager.initialize_integration(integration_type)
            
            # Process the webhook through the integration
            context = {
                "event_type": event_type,
                "webhook_payload": payload
            }
            
            response = await manager.process_command(
                f"handle_{event_type}_event", 
                source=integration_type,
                context=context
            )
            
            await manager.shutdown()
            return {"success": True, "response": response}
        else:
            return {"success": False, "error": f"Unsupported platform: {platform}"}
    
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return {"success": False, "error": str(e)}

# Main function to run the server
def run_server(config_path=None, host="0.0.0.0", port=8080):
    """Run the KairoMind integration server."""
    import uvicorn
    from fastapi import FastAPI, Request
    
    app = FastAPI(title="KairoMind Integration Server")
    integration_manager = None
    
    @app.on_event("startup")
    async def startup_event():
        nonlocal integration_manager
        integration_manager = await setup_integrations(config_path)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        if integration_manager:
            await integration_manager.shutdown()
    
    @app.post("/webhook")
    async def webhook_endpoint(request: Request):
        data = await request.json()
        return await handle_webhook(data)
    
    @app.post("/command")
    async def command_endpoint(request: Request):
        data = await request.json()
        command = data.get("command")
        source = data.get("source")
        context = data.get("context")
        
        if not command:
            return {"success": False, "error": "No command provided"}
        
        response = await integration_manager.process_command(command, source, context)
        return {"success": True, "response": response}
    
    @app.get("/devices")
    async def devices_endpoint():
        devices = await integration_manager.discover_all_devices()
        return {"success": True, "devices": devices}
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KairoMind Integration Server")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    
    run_server(args.config, args.host, args.port)

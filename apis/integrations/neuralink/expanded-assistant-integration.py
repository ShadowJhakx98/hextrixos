"""
kairomind_integration.py

A comprehensive integration framework for KairoMind that connects with multiple
smart home platforms and brain-computer interfaces.
"""

import asyncio
import json
import logging
import os
import requests
import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable

# Third-party imports for various integrations
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import homeassistant.remote as haremote
from homeassistant.core import HomeAssistant
from gactions.actions import ActionsSdkApp
from pyHomeKit import accessories as hk_accessories
import matter_controller
from neuralink_sdk import NeuralinkInterface, BrainSignalProcessor, ThoughtPatternDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Enum for supported integration types."""
    ALEXA = "alexa"
    GOOGLE_HOME = "google_home"
    HOME_ASSISTANT = "home_assistant"
    HOMEKIT = "homekit"
    MATTER = "matter"
    NEURALINK = "neuralink"

class DeviceCapability(Enum):
    """Enum for device capabilities across platforms."""
    SWITCH = "switch"
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    LOCK = "lock"
    SENSOR = "sensor"
    MEDIA = "media"
    CAMERA = "camera"
    SCENE = "scene"

class IntegrationBase(ABC):
    """Abstract base class for all integrations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration parameters."""
        self.config = config
        self.is_connected = False
        self._executor = ThreadPoolExecutor(max_workers=5)
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the platform."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the platform."""
        pass
    
    @abstractmethod
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process a command and return a response."""
        pass
    
    @abstractmethod
    async def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover available devices on the platform."""
        pass
    
    def run_in_background(self, func, *args, **kwargs):
        """Run a function in a background thread."""
        return self._executor.submit(func, *args, **kwargs)

class AlexaIntegration(IntegrationBase):
    """Integration with Amazon Alexa."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.skill_id = config.get("skill_id", "")
        self.endpoint = config.get("endpoint", "")
        self.auth_token = config.get("auth_token", "")
    
    async def connect(self) -> bool:
        """Connect to Alexa Skills API."""
        try:
            # In a real implementation, you'd verify connectivity with Amazon's services
            logger.info("Connecting to Alexa Skills API")
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Alexa: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Alexa Skills API."""
        self.is_connected = False
        return True
    
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process an Alexa command."""
        from kairomind import KairoMind  # Import to avoid circular dependencies
        
        if not self.is_connected:
            await self.connect()
        
        intent_name = context.get("intent_name") if context else command
        slots = context.get("slots", {}) if context else {}
        
        logger.info(f"Processing Alexa command: {intent_name} with slots: {slots}")
        
        kairomind = KairoMind(self.config.get("kairomind_config", {}))
        response = await kairomind.process_command(command, source="alexa", context=context)
        
        return response
    
    async def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover Alexa-compatible devices."""
        # In a real implementation, you would query the Alexa API
        devices = []
        try:
            # Placeholder for actual API call
            logger.info("Discovering Alexa devices")
            # Mock data for demonstration
            devices = [
                {"id": "alexa_light_1", "name": "Living Room Light", "type": DeviceCapability.LIGHT.value},
                {"id": "alexa_thermostat_1", "name": "Home Thermostat", "type": DeviceCapability.THERMOSTAT.value}
            ]
        except Exception as e:
            logger.error(f"Error discovering Alexa devices: {str(e)}")
        
        return devices

class KairoMindAlexaSkill(AbstractRequestHandler):
    """Alexa skill handler for KairoMind."""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        """Check if this handler can handle the request."""
        # You can implement more specific logic based on request type
        return True
    
    def handle(self, handler_input: HandlerInput) -> Response:
        """Handle the Alexa request."""
        try:
            request = handler_input.request_envelope.request
            
            # Extract intent and slots information
            intent_name = request.intent.name if hasattr(request, 'intent') else "Unknown"
            slots = {}
            if hasattr(request, 'intent') and hasattr(request.intent, 'slots'):
                slots = {name: slot.value for name, slot in request.intent.slots.items()}
            
            context = {
                "intent_name": intent_name,
                "slots": slots,
                "request_id": request.request_id,
                "timestamp": request.timestamp,
                "locale": handler_input.request_envelope.request.locale
            }
            
            # Initialize AlexaIntegration
            config = {
                "skill_id": os.environ.get("ALEXA_SKILL_ID", ""),
                "auth_token": os.environ.get("ALEXA_AUTH_TOKEN", ""),
                "kairomind_config": {}  # Add any config needed for KairoMind
            }
            
            alexa_integration = AlexaIntegration(config)
            
            # Process the command
            speech_text = asyncio.run(alexa_integration.process_command(intent_name, context))
            
            # Build and return the response
            return handler_input.response_builder.speak(speech_text).response
            
        except Exception as e:
            logger.error(f"Error handling Alexa request: {str(e)}")
            return handler_input.response_builder.speak("Sorry, I encountered an error processing your request.").response

class GoogleHomeIntegration(IntegrationBase):
    """Integration with Google Home/Google Assistant."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.project_id = config.get("project_id", "")
        self.client_id = config.get("client_id", "")
        self.client_secret = config.get("client_secret", "")
        self.app = None
    
    async def connect(self) -> bool:
        """Connect to Google Actions SDK."""
        try:
            # In a real implementation, you would authenticate with Google
            logger.info("Connecting to Google Home/Assistant")
            self.app = ActionsSdkApp()
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Google Home: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Google Home."""
        self.app = None
        self.is_connected = False
        return True
    
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process a Google Home command."""
        from kairomind import KairoMind  # Import to avoid circular dependencies
        
        if not self.is_connected:
            await self.connect()
        
        intent = context.get("intent") if context else command
        parameters = context.get("parameters", {}) if context else {}
        
        logger.info(f"Processing Google Home command: {intent} with parameters: {parameters}")
        
        kairomind = KairoMind(self.config.get("kairomind_config", {}))
        response = await kairomind.process_command(command, source="google_home", context=context)
        
        return response
    
    async def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover Google Home devices."""
        # In a real implementation, you would query the Google Home API
        devices = []
        try:
            logger.info("Discovering Google Home devices")
            # Mock data for demonstration
            devices = [
                {"id": "google_speaker_1", "name": "Kitchen Speaker", "type": DeviceCapability.MEDIA.value},
                {"id": "google_light_1", "name": "Bedroom Light", "type": DeviceCapability.LIGHT.value}
            ]
        except Exception as e:
            logger.error(f"Error discovering Google Home devices: {str(e)}")
        
        return devices

class HomeAssistantIntegration(IntegrationBase):
    """Integration with Home Assistant."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 8123)
        self.token = config.get("token", "")
        self.ha_instance = None
    
    async def connect(self) -> bool:
        """Connect to Home Assistant instance."""
        try:
            logger.info(f"Connecting to Home Assistant at {self.host}:{self.port}")
            
            # Using the Home Assistant API
            self.ha_instance = haremote.API(
                self.host, 
                self.token,
                port=self.port,
                use_ssl=self.config.get("use_ssl", False)
            )
            
            # Test connection
            test = self.ha_instance.get_states()
            if test:
                self.is_connected = True
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to connect to Home Assistant: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Home Assistant."""
        self.ha_instance = None
        self.is_connected = False
        return True
    
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process a Home Assistant command."""
        from kairomind import KairoMind  # Import to avoid circular dependencies
        
        if not self.is_connected:
            await self.connect()
        
        entity_id = context.get("entity_id") if context else None
        service = context.get("service") if context else None
        
        logger.info(f"Processing Home Assistant command: {command} for entity: {entity_id} service: {service}")
        
        # If specific entity and service provided, call it directly
        if entity_id and service:
            domain = entity_id.split('.')[0]
            try:
                result = self.ha_instance.call_service(
                    domain, 
                    service, 
                    {"entity_id": entity_id, **(context.get("service_data", {}) if context else {})}
                )
                return f"Successfully executed {service} on {entity_id}."
            except Exception as e:
                logger.error(f"Error calling Home Assistant service: {str(e)}")
                return f"Error: {str(e)}"
        
        # Otherwise, let KairoMind interpret the command
        kairomind = KairoMind(self.config.get("kairomind_config", {}))
        response = await kairomind.process_command(command, source="home_assistant", context=context)
        
        return response
    
    async def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover Home Assistant devices/entities."""
        devices = []
        
        if not self.is_connected:
            await self.connect()
        
        try:
            # Get all states from Home Assistant
            states = self.ha_instance.get_states()
            
            for state in states:
                entity_id = state.entity_id
                domain = entity_id.split('.')[0]
                
                # Map Home Assistant domains to DeviceCapability
                capability_map = {
                    "light": DeviceCapability.LIGHT,
                    "switch": DeviceCapability.SWITCH,
                    "climate": DeviceCapability.THERMOSTAT,
                    "lock": DeviceCapability.LOCK,
                    "sensor": DeviceCapability.SENSOR,
                    "media_player": DeviceCapability.MEDIA,
                    "camera": DeviceCapability.CAMERA,
                    "scene": DeviceCapability.SCENE
                }
                
                capability = capability_map.get(domain, domain)
                
                devices.append({
                    "id": entity_id,
                    "name": state.attributes.get("friendly_name", entity_id),
                    "type": capability.value if isinstance(capability, DeviceCapability) else capability,
                    "state": state.state,
                    "attributes": state.attributes
                })
                
        except Exception as e:
            logger.error(f"Error discovering Home Assistant devices: {str(e)}")
        
        return devices

class HomeKitIntegration(IntegrationBase):
    """Integration with Apple HomeKit."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.pin_code = config.get("pin_code", "12345678")
        self.setup_id = config.get("setup_id", "")
        self.accessories = []
    
    async def connect(self) -> bool:
        """Initialize HomeKit bridge."""
        try:
            logger.info("Initializing HomeKit bridge")
            
            # In a real implementation, you would set up a HomeKit bridge
            # and start advertising accessories
            
            # Mock accessories for demonstration
            self.accessories = [
                hk_accessories.Lightbulb("KairoMind Light", "00001", self.pin_code),
                hk_accessories.Thermostat("KairoMind Thermostat", "00002", self.pin_code)
            ]
            
            # Start HomeKit server in background thread
            self.run_in_background(self._run_homekit_server)
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize HomeKit bridge: {str(e)}")
            return False
    
    def _run_homekit_server(self):
        """Run HomeKit server in background thread."""
        # This would be a real implementation using the HomeKit libraries
        logger.info("HomeKit server running...")
        while self.is_connected:
            time.sleep(1)
        logger.info("HomeKit server stopped.")
    
    async def disconnect(self) -> bool:
        """Disconnect HomeKit bridge."""
        self.is_connected = False
        self.accessories = []
        return True
    
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process a HomeKit command."""
        from kairomind import KairoMind  # Import to avoid circular dependencies
        
        if not self.is_connected:
            await self.connect()
        
        accessory_id = context.get("accessory_id") if context else None
        characteristic = context.get("characteristic") if context else None
        value = context.get("value") if context else None
        
        logger.info(f"Processing HomeKit command: {command} for accessory: {accessory_id}")
        
        # If specific accessory and characteristic provided, set it directly
        if accessory_id and characteristic is not None and value is not None:
            for accessory in self.accessories:
                if accessory.id == accessory_id:
                    try:
                        accessory.set_characteristic(characteristic, value)
                        return f"Set {characteristic} to {value} on {accessory.name}"
                    except Exception as e:
                        logger.error(f"Error setting HomeKit characteristic: {str(e)}")
                        return f"Error: {str(e)}"
        
        # Otherwise, let KairoMind interpret the command
        kairomind = KairoMind(self.config.get("kairomind_config", {}))
        response = await kairomind.process_command(command, source="homekit", context=context)
        
        return response
    
    async def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover HomeKit accessories."""
        devices = []
        
        if not self.is_connected:
            await self.connect()
        
        for accessory in self.accessories:
            # Map HomeKit accessory categories to DeviceCapability
            category_map = {
                1: DeviceCapability.LIGHT,  # Lightbulb
                2: DeviceCapability.SWITCH,  # Switch
                3: DeviceCapability.THERMOSTAT,  # Thermostat
                6: DeviceCapability.LOCK,  # Door Lock
                10: DeviceCapability.SENSOR,  # Sensor
                8: DeviceCapability.MEDIA,  # Media Player
                17: DeviceCapability.CAMERA,  # Camera
            }
            
            capability = category_map.get(accessory.category, str(accessory.category))
            
            devices.append({
                "id": accessory.id,
                "name": accessory.name,
                "type": capability.value if isinstance(capability, DeviceCapability) else capability,
                "room": accessory.room if hasattr(accessory, "room") else None,
                "manufacturer": accessory.manufacturer if hasattr(accessory, "manufacturer") else "KairoMind"
            })
        
        return devices

class MatterIntegration(IntegrationBase):
    """Integration with Matter protocol devices."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.fabric_id = config.get("fabric_id", "")
        self.controller_id = config.get("controller_id", "")
        self.controller = None
    
    async def connect(self) -> bool:
        """Initialize Matter controller."""
        try:
            logger.info("Initializing Matter controller")
            
            # In a real implementation, you would initialize a Matter controller
            self.controller = matter_controller.Controller(
                fabric_id=self.fabric_id,
                controller_id=self.controller_id
            )
            
            # Start commissioning mode for new devices
            if self.config.get("auto_commission", False):
                self.controller.start_commissioning()
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Matter controller: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect Matter controller."""
        if self.controller:
            try:
                self.controller.stop()
            except Exception as e:
                logger.error(f"Error stopping Matter controller: {str(e)}")
        
        self.controller = None
        self.is_connected = False
        return True
    
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process a Matter command."""
        from kairomind import KairoMind  # Import to avoid circular dependencies
        
        if not self.is_connected:
            await self.connect()
        
        node_id = context.get("node_id") if context else None
        cluster = context.get("cluster") if context else None
        attribute = context.get("attribute") if context else None
        value = context.get("value") if context else None
        
        logger.info(f"Processing Matter command: {command} for node: {node_id}")
        
        # If specific node, cluster, and attribute provided, set it directly
        if node_id and cluster and attribute and value is not None:
            try:
                result = self.controller.write_attribute(node_id, cluster, attribute, value)
                return f"Set {cluster}.{attribute} to {value} on node {node_id}"
            except Exception as e:
                logger.error(f"Error setting Matter attribute: {str(e)}")
                return f"Error: {str(e)}"
        
        # Otherwise, let KairoMind interpret the command
        kairomind = KairoMind(self.config.get("kairomind_config", {}))
        response = await kairomind.process_command(command, source="matter", context=context)
        
        return response
    
    async def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover Matter devices."""
        devices = []
        
        if not self.is_connected:
            await self.connect()
        
        try:
            # In a real implementation, you would query the Matter controller
            # for connected devices
            nodes = self.controller.get_nodes()
            
            for node in nodes:
                # Map Matter device types to DeviceCapability
                # These would be based on Matter clusters and device types
                device_map = {
                    "onoff": DeviceCapability.SWITCH,
                    "levelcontrol": DeviceCapability.LIGHT,
                    "thermostat": DeviceCapability.THERMOSTAT,
                    "doorlock": DeviceCapability.LOCK,
                    "temperaturesensor": DeviceCapability.SENSOR,
                }
                
                # Determine primary capability based on supported clusters
                primary_capability = None
                for cluster in node.clusters:
                    if cluster in device_map:
                        primary_capability = device_map[cluster]
                        break
                
                if not primary_capability:
                    primary_capability = "unknown"
                
                devices.append({
                    "id": node.node_id,
                    "name": node.name if hasattr(node, "name") else f"Matter Device {node.node_id}",
                    "type": primary_capability.value if isinstance(primary_capability, DeviceCapability) else primary_capability,
                    "vendor_id": node.vendor_id,
                    "product_id": node.product_id,
                    "clusters": node.clusters
                })
        
        except Exception as e:
            logger.error(f"Error discovering Matter devices: {str(e)}")
        
        return devices

class NeuralinkIntegration(IntegrationBase):
    """Integration with Neuralink brain-computer interface."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.device_id = config.get("device_id", "")
        self.calibration_profile = config.get("calibration_profile", "default")
        self.sensitivity = config.get("sensitivity", 0.7)
        self.interface = None
        self.signal_processor = None
        self.thought_detector = None
        self.callback = None
    
    async def connect(self) -> bool:
        """Initialize Neuralink interface."""
        try:
            logger.info("Initializing Neuralink interface")
            
            # In a real implementation, you would initialize a Neuralink interface
            self.interface = NeuralinkInterface(device_id=self.device_id)
            self.signal_processor = BrainSignalProcessor(
                sensitivity=self.sensitivity,
                filter_settings=self.config.get("filter_settings", {})
            )
            self.thought_detector = ThoughtPatternDetector(
                calibration_profile=self.calibration_profile
            )
            
            # Connect to device
            connected = self.interface.connect()
            if not connected:
                logger.error("Failed to connect to Neuralink device")
                return False
            
            # Start background signal processing
            self.run_in_background(self._process_signals)
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Neuralink interface: {str(e)}")
            return False
    
    def _process_signals(self):
        """Process brain signals in background thread."""
        logger.info("Started Neuralink signal processing")
        while self.is_connected:
            try:
                # Get raw signals from interface
                raw_signals = self.interface.get_signals()
                
                # Process signals
                processed_signals = self.signal_processor.process(raw_signals)
                
                # Detect thought patterns
                detected_thoughts = self.thought_detector.detect(processed_signals)
                
                # If thoughts detected and callback set, trigger it
                if detected_thoughts and self.callback:
                    asyncio.run(self.callback(detected_thoughts))
                
                time.sleep(0.01)  # 10ms sampling interval
            except Exception as e:
                logger.error(f"Error in Neuralink signal processing: {str(e)}")
                time.sleep(1)  # Back off on error
        
        logger.info("Stopped Neuralink signal processing")
    
    async def disconnect(self) -> bool:
        """Disconnect Neuralink interface."""
        self.is_connected = False  # Stop background processing first
        
        if self.interface:
            try:
                self.interface.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting Neuralink interface: {str(e)}")
        
        self.interface = None
        self.signal_processor = None
        self.thought_detector = None
        self.callback = None
        
        return True
    
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process a Neuralink command or thought pattern."""
        from kairomind import KairoMind  # Import to avoid circular dependencies
        
        if not self.is_connected:
            await self.connect()
        
        thought_pattern = context.get("thought_pattern") if context else None
        confidence = context.get("confidence", 0.0) if context else 0.0
        
        logger.info(f"Processing Neuralink command: {command} with thought pattern: {thought_pattern}")
        
        # If this is a direct thought command with sufficient confidence
        if thought_pattern and confidence >= self.config.get("min_confidence", 0.7):
            # Map thought patterns to actions
            thought_map = self.config.get("thought_map", {})
            if thought_pattern in thought_map:
                action = thought_map[thought_pattern]
                return f"Executing thought-mapped action: {action}"
        
        # Otherwise, let KairoMind interpret the command
        kairomind = KairoMind(self.config.get("kairomind_config", {}))
        response = await kairomind.process_command(command, source="neuralink", context=context)
        
        return response
    
    async def discover_devices(self) -> List[Dict[str, Any]]:
        """Get information about connected Neuralink devices."""
        devices = []
        
        if not self.is_connected:
            await self.connect()
        
        try:
            # Get device information
            device_info = self.interface.get_device_info()
            
            devices.append({
                "id": device_info.get("id", self.device_id),
                "name": device_info.get("name", "Neuralink Device"),
                "type": "neuralink",
                "firmware_version": device_info.get("firmware_version", "unknown"),
                "battery_level": device_info.get("battery_level", 0),
                "signal_strength": device_info.get("signal_strength", 0),
                "active_channels": device_info.get("active_channels", 0),
                "thought_patterns": self.thought_detector.get_available_patterns()
            })
        
        except Exception as e:
            logger.error(f"Error getting Neuralink device info: {str(e)}")
        
        return devices
    
    def register_thought_callback(self, callback: Callable[[List[Dict[str, Any]]], None]):
        """Register a callback for detected thought patterns."""
        self.callback = callback

class KairoMindIntegrationManager:
    """Manager for all KairoMind integrations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the integration manager."""
        self.config = config or {}
        self.integrations: Dict[IntegrationType, IntegrationBase] = {}
        self.active_integrations = set()
    
    async def initialize_integrations(self, integration_types: List[IntegrationType] = None):
        """Initialize and connect specified integrations."""
        # If no specific types provided, use all from config
        if not integration_types:
            integration_types = [
                IntegrationType(key) for key in self.config.keys() 
                if key in [t.value for t in IntegrationType]
            ]
        
        for integration_type in integration_types:
            await self.initialize_integration(integration_type)
    
    async def initialize_integration(self, integration_type: IntegrationType) -> bool:
        """Initialize and connect a specific integration."""
        if integration_type in self.integrations:
            # Already initialized
            return True
        
        integration_config = self.config.get(integration_type.value, {})
        if not integration_config:
            logger.warning(f"No configuration found for {integration_type.value}")
            return False
        
        # Create integration instance based on type
        integration = None
        if integration_type == IntegrationType.ALEXA:
            integration = AlexaIntegration(integration_config)
        elif integration_type == IntegrationType.GOOGLE_HOME:
            integration = GoogleHomeIntegration(integration_config)
        elif integration_type == IntegrationType.HOME_ASSISTANT:
            integration = HomeAssistantIntegration(integration_config)
        elif integration_type == IntegrationType.HOMEKIT:
            integration = HomeKitIntegration(integration_config)
        elif integration_type == IntegrationType.MATTER:
            integration = MatterIntegration(integration_config)
        elif integration_type == IntegrationType.NEURALINK:
            integration = NeuralinkIntegration(integration_config)
        
        if not integration:
            logger.error(f"Unknown integration type: {integration_type.value}")
            return False
        
        # Try to connect
        connected = await integration.connect()
        if connected:
            self.integrations[integration_type] = integration
            self.active_integrations.add(integration_type)
            logger.info(f"Successfully initialized and connected {integration_type.value}")
            return True
        else:
            logger.error(f"Failed to connect {integration_type.value}")
            return False
    
    async def process_command(self, command: str, source: Union[str, IntegrationType] = None, 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a command through all
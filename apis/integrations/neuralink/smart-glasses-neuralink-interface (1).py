"""
Hextrix AI Smart Glasses and Neuralink Interface
Implements a combined interface for smart glasses and neural implant with AR/VR features
"""
import time
import json
from typing import Dict, List, Optional, Union
import requests
from concurrent.futures import ThreadPoolExecutor

class SmartGlassesInterface:
    def __init__(self, glasses_id: str, api_key: str):
        self.glasses_id = glasses_id
        self.base_url = "https://api.smartglasses.com/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.connection_status = None
        self.is_streaming = False
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # AR/VR and accessibility feature states
        self.ar_vr_active = False
        self.visual_analysis_active = False
        self.accessibility_features = {
            "emotion_detection": False,
            "social_cue_analysis": False,
            "ocr": False,
            "qr_reader": False,
            "object_recognition": False
        }
        
    def connect(self) -> Dict:
        """
        Establish connection to the smart glasses device.
        """
        endpoint = f"{self.base_url}/connect"
        payload = {"glasses_id": self.glasses_id}
        response = self.session.post(endpoint, json=payload)
        self.connection_status = response.json()
        return self.connection_status
    
    def disconnect(self) -> Dict:
        """
        Safely disconnect from the smart glasses device.
        """
        if self.is_streaming:
            self.stop_visual_stream()
            
        # Disable all accessibility features before disconnecting
        if any(self.accessibility_features.values()):
            self.disable_all_accessibility_features()
            
        endpoint = f"{self.base_url}/disconnect"
        response = self.session.post(endpoint)
        self.connection_status = None
        return response.json()
    
    def get_device_status(self) -> Dict:
        """
        Returns detailed device status including battery, temperature, and connection quality.
        """
        endpoint = f"{self.base_url}/device/status"
        response = self.session.get(endpoint)
        return response.json()
    
    def capture_image(self) -> Dict:
        """
        Capture a single image from smart glasses camera.
        """
        endpoint = f"{self.base_url}/camera/capture"
        response = self.session.post(endpoint)
        return response.json()
    
    def start_visual_stream(self, processing_level: str = "low") -> Dict:
        """
        Start continuous visual data stream with specified level of on-device processing.
        
        Args:
            processing_level: Level of on-device processing (low, medium, high)
                - low: Raw video stream only
                - medium: Basic object detection and scene analysis
                - high: Advanced scene understanding, emotion detection, OCR
        """
        if self.is_streaming:
            return {"status": "already_streaming"}
            
        endpoint = f"{self.base_url}/camera/stream/start"
        payload = {"processing_level": processing_level}
        response = self.session.post(endpoint, json=payload)
        
        if response.json().get("status") == "success":
            self.is_streaming = True
            
        return response.json()
    
    def stop_visual_stream(self) -> Dict:
        """
        Stop continuous visual data stream.
        """
        endpoint = f"{self.base_url}/camera/stream/stop"
        response = self.session.post(endpoint)
        
        if response.json().get("status") == "success":
            self.is_streaming = False
            
        return response.json()
    
    def display_content(self, content_type: str, content_data: Dict) -> Dict:
        """
        Display content on smart glasses display.
        
        Args:
            content_type: Type of content (text, image, notification, ar_overlay)
            content_data: Dictionary containing content details
        """
        endpoint = f"{self.base_url}/display"
        payload = {
            "content_type": content_type,
            "content_data": content_data
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def analyze_scene(self, analysis_types: List[str]) -> Dict:
        """
        Request on-device scene analysis.
        
        Args:
            analysis_types: List of analysis types to perform
                (e.g., ["object_detection", "face_recognition", "text_detection"])
        """
        endpoint = f"{self.base_url}/analyze"
        payload = {"analysis_types": analysis_types}
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def update_settings(self, settings: Dict) -> Dict:
        """
        Update device settings.
        
        Args:
            settings: Dictionary of settings to update
        """
        endpoint = f"{self.base_url}/settings"
        response = self.session.patch(endpoint, json=settings)
        return response.json()
    
    # AR/VR Initialization
    
    def initialize_ar_vr(self, 
                        mode: str = "mixed",
                        quality: str = "high",
                        fov: int = 110) -> Dict:
        """
        Initialize AR/VR mode on smart glasses.
        
        Args:
            mode: AR/VR mode ("ar", "vr", "mixed")
            quality: Visual quality level ("low", "medium", "high", "ultra")
            fov: Field of view in degrees
        """
        endpoint = f"{self.base_url}/ar_vr/initialize"
        payload = {
            "mode": mode,
            "quality": quality,
            "fov": fov,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.ar_vr_active = True
            
        return response.json()
    
    def shutdown_ar_vr(self) -> Dict:
        """
        Safely shutdown AR/VR mode.
        """
        if not self.ar_vr_active:
            return {"status": "not_active"}
            
        # Disable all accessibility features before shutdown
        if any(self.accessibility_features.values()):
            self.disable_all_accessibility_features()
            
        endpoint = f"{self.base_url}/ar_vr/shutdown"
        response = self.session.post(endpoint)
        
        if response.status_code == 200:
            self.ar_vr_active = False
            self.visual_analysis_active = False
            
        return response.json()
    
    def initialize_visual_analysis(self, analysis_types: List[str]) -> Dict:
        """
        Initialize visual analysis systems.
        
        Args:
            analysis_types: Types of analysis to enable
                          ["face", "object_detection", "text", "scene", "gesture", 
                           "qr_code", "emotion", "activity"]
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        endpoint = f"{self.base_url}/visual/initialize"
        payload = {
            "analysis_types": analysis_types,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.visual_analysis_active = True
            
        return response.json()
    
    # Social Cue Analysis Methods
    
    def enable_social_cue_analysis(self,
                                 continuous: bool = True,
                                 detail_level: str = "medium",
                                 display_mode: str = "tooltip") -> Dict:
        """
        Enable social cue analysis for accessibility purposes.
        
        Args:
            continuous: Whether to continuously analyze social cues
            detail_level: Level of detail in analysis ("basic", "medium", "detailed")
            display_mode: How to display cues ("tooltip", "sidebar", 
                         "discreet_overlay", "descriptive_text")
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if not self.visual_analysis_active:
            self.initialize_visual_analysis(["face", "object_detection"])
            
        endpoint = f"{self.base_url}/accessibility/social_cue/enable"
        payload = {
            "continuous": continuous,
            "detail_level": detail_level,
            "display_mode": display_mode,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.accessibility_features["social_cue_analysis"] = True
            
        return response.json()
    
    def disable_social_cue_analysis(self) -> Dict:
        """
        Disable social cue analysis.
        """
        if not self.ar_vr_active or not self.accessibility_features["social_cue_analysis"]:
            return {"status": "error", "message": "Social cue analysis not enabled"}
            
        endpoint = f"{self.base_url}/accessibility/social_cue/disable"
        response = self.session.post(endpoint)
        
        if response.status_code == 200:
            self.accessibility_features["social_cue_analysis"] = False
            
        return response.json()
    
    def analyze_social_interaction(self,
                                 context: str = "general",
                                 participants: int = None) -> Dict:
        """
        Perform an immediate analysis of the current social interaction.
        
        Args:
            context: The social context type ("general", "professional", 
                   "educational", "intimate", "public_speaking")
            participants: Number of participants to focus on (None = all detected)
        """
        if not self.ar_vr_active or not self.accessibility_features["social_cue_analysis"]:
            return {"status": "error", "message": "Social cue analysis not enabled"}
            
        endpoint = f"{self.base_url}/accessibility/social_cue/analyze"
        payload = {
            "context": context,
            "timestamp": int(time.time() * 1000)
        }
        
        if participants is not None:
            payload["participants"] = participants
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Object Recognition and Navigation Methods
    
    def enable_object_recognition(self,
                                continuous: bool = True,
                                object_types: List[str] = None,
                                min_confidence: float = 0.7,
                                highlight_mode: str = "outline") -> Dict:
        """
        Enable object recognition for accessibility and navigation.
        
        Args:
            continuous: Whether to continuously recognize objects
            object_types: Types of objects to recognize (None = all supported types)
            min_confidence: Minimum confidence threshold (0.0-1.0)
            highlight_mode: How to highlight recognized objects
                          ("outline", "label", "color_overlay", "icon", "none")
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if not self.visual_analysis_active:
            self.initialize_visual_analysis(["object_detection"])
            
        if object_types is None:
            object_types = ["person", "vehicle", "furniture", "electronics", 
                           "food", "animal", "plant", "navigation_marker"]
            
        endpoint = f"{self.base_url}/visual/object/enable"
        payload = {
            "continuous": continuous,
            "object_types": object_types,
            "min_confidence": min_confidence,
            "highlight_mode": highlight_mode,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.accessibility_features["object_recognition"] = True
            
        return response.json()
    
    def disable_object_recognition(self) -> Dict:
        """
        Disable object recognition.
        """
        if not self.ar_vr_active or not self.accessibility_features["object_recognition"]:
            return {"status": "error", "message": "Object recognition not enabled"}
            
        endpoint = f"{self.base_url}/visual/object/disable"
        response = self.session.post(endpoint)
        
        if response.status_code == 200:
            self.accessibility_features["object_recognition"] = False
            
        return response.json()
    
    def identify_objects(self,
                       region: Dict = None,
                       object_types: List[str] = None,
                       max_results: int = 10) -> Dict:
        """
        Perform immediate object identification in current visual field.
        
        Args:
            region: Restrict recognition to specific region of visual field
                  Format: {"x": float, "y": float, "width": float, "height": float}
            object_types: Types of objects to recognize (None = all supported types)
            max_results: Maximum number of results to return
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        endpoint = f"{self.base_url}/visual/object/identify"
        payload = {
            "max_results": max_results,
            "timestamp": int(time.time() * 1000)
        }
        
        if region is not None:
            payload["region"] = region
            
        if object_types is not None:
            payload["object_types"] = object_types
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def create_navigation_path(self,
                             destination: Dict,
                             route_preferences: Dict = None,
                             transport_mode: str = "walking",
                             avoid_obstacles: bool = True) -> Dict:
        """
        Create a navigation path in AR overlay.
        
        Args:
            destination: Destination coordinates {"lat": float, "lng": float} or 
                        {"x": float, "y": float, "z": float} for indoor navigation
            route_preferences: Dictionary of routing preferences
            transport_mode: Mode of transportation ("walking", "driving", "transit", "wheelchair")
            avoid_obstacles: Whether to actively detect and avoid obstacles
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if route_preferences is None:
            route_preferences = {
                "prefer_accessible": True,
                "avoid_stairs": False,
                "avoid_crowds": False,
                "prefer_well_lit": True
            }
            
        endpoint = f"{self.base_url}/navigation/create_path"
        payload = {
            "destination": destination,
            "route_preferences": route_preferences,
            "transport_mode": transport_mode,
            "avoid_obstacles": avoid_obstacles,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def update_navigation_path(self,
                             path_id: str,
                             updates: Dict) -> Dict:
        """
        Update an existing navigation path.
        
        Args:
            path_id: ID of the navigation path to update
            updates: Dictionary containing updates to apply
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        endpoint = f"{self.base_url}/navigation/update_path"
        payload = {
            "path_id": path_id,
            "updates": updates,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.patch(endpoint, json=payload)
        return response.json()
    
    def cancel_navigation(self,
                        path_id: str = None) -> Dict:
        """
        Cancel active navigation.
        
        Args:
            path_id: ID of specific navigation path to cancel (None = all active paths)
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        endpoint = f"{self.base_url}/navigation/cancel"
        payload = {
            "timestamp": int(time.time() * 1000)
        }
        
        if path_id is not None:
            payload["path_id"] = path_id
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Helper methods for managing and disabling all accessibility features
    
    def get_active_accessibility_features(self) -> Dict:
        """
        Get status of all accessibility features.
        """
        return {
            "status": "success" if self.ar_vr_active else "inactive",
            "features": self.accessibility_features,
            "timestamp": int(time.time() * 1000)
        }
    
    def disable_all_accessibility_features(self) -> Dict:
        """
        Disable all active accessibility features.
        """
        results = {}
        
        if self.accessibility_features["emotion_detection"]:
            results["emotion_detection"] = self.disable_emotion_detection()
            
        if self.accessibility_features["social_cue_analysis"]:
            results["social_cue_analysis"] = self.disable_social_cue_analysis()
            
        if self.accessibility_features["ocr"]:
            results["ocr"] = self.disable_ocr()
            
        if self.accessibility_features["qr_reader"]:
            results["qr_reader"] = self.disable_qr_reader()
            
        if self.accessibility_features["object_recognition"]:
            results["object_recognition"] = self.disable_object_recognition()
            
        return {
            "status": "success",
            "results": results,
            "timestamp": int(time.time() * 1000)
        }
    
    # Privacy and data management methods
    
    def set_privacy_preferences(self, preferences: Dict) -> Dict:
        """
        Set privacy preferences for the interface.
        
        Args:
            preferences: Dictionary containing privacy settings:
                        - data_collection_level: What data to collect ("minimal", "standard", "detailed")
                        - data_retention_days: How long to retain data (int)
                        - share_anonymized_data: Whether to share anonymized data (bool)
                        - record_visual_field: Whether to record visual data (bool)
                        - record_neural_activity: What neural activity to record (List[str])
                        - location_tracking: Location tracking settings (Dict)
        """
        endpoint = f"{self.base_url}/privacy/preferences"
        payload = {
            "preferences": preferences,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.put(endpoint, json=payload)
        return response.json()
    
    def get_privacy_preferences(self) -> Dict:
        """
        Get current privacy preferences.
        """
        endpoint = f"{self.base_url}/privacy/preferences"
        response = self.session.get(endpoint)
        return response.json()
    
    def delete_collected_data(self, 
                            data_types: List[str] = None,
                            time_range: Dict = None) -> Dict:
        """
        Delete collected user data.
        
        Args:
            data_types: Types of data to delete (None = all data types)
            time_range: Time range for data deletion:
                        {"start_time": int, "end_time": int} (None = all time)
        """
        endpoint = f"{self.base_url}/privacy/delete_data"
        payload = {
            "timestamp": int(time.time() * 1000)
        }
        
        if data_types is not None:
            payload["data_types"] = data_types
            
        if time_range is not None:
            payload["time_range"] = time_range
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def export_user_data(self, 
                       data_types: List[str] = None,
                       format: str = "json",
                       time_range: Dict = None) -> Dict:
        """
        Export user data.
        
        Args:
            data_types: Types of data to export (None = all data types)
            format: Export format ("json", "csv", "xml")
            time_range: Time range for data export:
                       {"start_time": int, "end_time": int} (None = all time)
        """
        endpoint = f"{self.base_url}/privacy/export_data"
        payload = {
            "format": format,
            "timestamp": int(time.time() * 1000)
        }
        
        if data_types is not None:
            payload["data_types"] = data_types
            
        if time_range is not None:
            payload["time_range"] = time_range
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Voice and audio interface methods
    
    def text_to_speech(self, 
                     text: str,
                     voice_id: str = "default",
                     speed: float = 1.0,
                     pitch: float = 1.0) -> Dict:
        """
        Convert text to speech output.
        
        Args:
            text: Text to convert to speech
            voice_id: ID of voice to use
            speed: Speech speed multiplier (0.5-2.0)
            pitch: Speech pitch multiplier (0.5-2.0)
        """
        endpoint = f"{self.base_url}/audio/tts"
        payload = {
            "text": text,
            "voice_id": voice_id,
            "speed": speed,
            "pitch": pitch,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def play_audio(self, 
                 audio_data: Union[str, bytes],
                 format_type: str = "url",
                 volume: float = 1.0) -> Dict:
        """
        Play audio through device.
        
        Args:
            audio_data: Either URL to audio file or base64 encoded audio data
            format_type: Type of audio data ("url" or "base64")
            volume: Playback volume (0.0-1.0)
        """
        endpoint = f"{self.base_url}/audio/play"
        payload = {
            "audio_data": audio_data,
            "format_type": format_type,
            "volume": volume,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def stop_audio(self) -> Dict:
        """
        Stop any currently playing audio.
        """
        endpoint = f"{self.base_url}/audio/stop"
        response = self.session.post(endpoint)
        return response.json()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class HextrixAILoop:
    """
    Implements the AI > smart glasses > AI > brain > AI loop for Hextrix AI
    """
    
    def __init__(self, neuralink_interface, smart_glasses_interface, hextrix_server_url: str):
        self.neuralink = neuralink_interface
        self.glasses = smart_glasses_interface
        self.hextrix_url = hextrix_server_url
        self.is_running = False
        self.thread_pool = ThreadPoolExecutor(max_workers=8)
        
    def start_loop(self, processing_level: str = "medium", update_interval_ms: int = 100) -> Dict:
        """
        Start the AI > smart glasses > AI > brain > AI loop.
        
        Args:
            processing_level: Level of smart glasses processing (low, medium, high)
            update_interval_ms: How often to update neural inputs in milliseconds
        """
        if self.is_running:
            return {"status": "already_running"}
            
        # Connect to Neuralink
        neuralink_status = self.neuralink.connect()
        if neuralink_status.get("status") != "connected":
            return {"status": "failed", "reason": "neuralink_connection_failed"}
            
        # Connect to smart glasses
        glasses_status = self.glasses.connect()
        if glasses_status.get("status") != "connected":
            self.neuralink.disconnect()
            return {"status": "failed", "reason": "glasses_connection_failed"}
            
        # Start visual stream on glasses
        stream_status = self.glasses.start_visual_stream(processing_level)
        if stream_status.get("status") != "success":
            self.neuralink.disconnect()
            self.glasses.disconnect()
            return {"status": "failed", "reason": "visual_stream_failed"}
            
        # Start the AI processing loop
        self.is_running = True
        self.thread_pool.submit(self._process_loop, update_interval_ms)
        
        return {"status": "success", "loop_active": True}
    
    def stop_loop(self) -> Dict:
        """
        Stop the AI > smart glasses > AI > brain > AI loop.
        """
        if not self.is_running:
            return {"status": "not_running"}
            
        self.is_running = False
        
        # Wait for processing to stop
        time.sleep(0.5)
        
        # Stop visual stream
        self.glasses.stop_visual_stream()
        
        # Disconnect from both devices
        neuralink_status = self.neuralink.disconnect()
        glasses_status = self.glasses.disconnect()
        
        return {
            "status": "success", 
            "neuralink_status": neuralink_status,
            "glasses_status": glasses_status
        }
    
    def _process_loop(self, update_interval_ms: int):
        """
        Main processing loop that runs in a background thread.
        
        This implements the AI > smart glasses > AI > brain > AI loop:
        1. Hextrix AI sends processing commands to smart glasses
        2. Smart glasses process visual data and send results to Hextrix AI
        3. Hextrix AI analyzes results and determines neural inputs
        4. Neural inputs are sent to Neuralink brain implant
        5. Neuralink feedback is sent back to Hextrix AI
        """
        last_update_time = 0
        
        while self.is_running:
            current_time = int(time.time() * 1000)
            
            # Only process at specified interval
            if current_time - last_update_time < update_interval_ms:
                time.sleep(0.01)  # Sleep to avoid CPU hogging
                continue
                
            last_update_time = current_time
            
            try:
                # Step 1: AI sends processing commands to smart glasses
                analysis_types = self._determine_analysis_types()
                scene_data = self.glasses.analyze_scene(analysis_types)
                
                # Step 2 & 3: Send to Hextrix AI for processing and neural input calculation
                hextrix_response = self._process_with_hextrix(scene_data)
                
                # Step 4: Send neural inputs to Neuralink
                if "neural_inputs" in hextrix_response:
                    neuralink_command = {
                        "type": "sensory",
                        "parameters": hextrix_response["neural_inputs"]
                    }
                    neuralink_response = self.neuralink.send_command(
                        neuralink_command["type"], 
                        neuralink_command["parameters"]
                    )
                    
                    # Step 5: Send Neuralink feedback back to Hextrix AI
                    self._process_neuralink_feedback(neuralink_response)
                
                # Update smart glasses display if needed
                if "display_content" in hextrix_response:
                    self.glasses.display_content(
                        hextrix_response["display_content"]["type"],
                        hextrix_response["display_content"]["data"]
                    )
                    
            except Exception as e:
                print(f"Error in processing loop: {str(e)}")
                # Log error but continue loop
    
    def _determine_analysis_types(self) -> List[str]:
        """
        Determine which types of analysis to request from smart glasses
        based on current context and user needs.
        """
        # This would be a more complex function in real implementation
        # For now, return standard analysis types
        return ["object_detection", "scene_classification", "text_detection"]
    
    def _process_with_hextrix(self, scene_data: Dict) -> Dict:
        """
        Send scene data to Hextrix AI server for processing.
        
        Returns Hextrix AI response with neural inputs and display content.
        """
        endpoint = f"{self.hextrix_url}/process"
        payload = {
            "scene_data": scene_data,
            "timestamp": int(time.time() * 1000)
        }
        
        try:
            response = requests.post(endpoint, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error communicating with Hextrix AI: {str(e)}")
            # Return minimal response in case of error
            return {
                "neural_inputs": {},
                "display_content": {
                    "type": "notification",
                    "data": {"message": "Connection error", "level": "error"}
                }
            }
    
    def _process_neuralink_feedback(self, neuralink_response: Dict):
        """
        Process feedback from Neuralink and send to Hextrix AI.
        """
        endpoint = f"{self.hextrix_url}/feedback"
        payload = {
            "neuralink_data": neuralink_response,
            "timestamp": int(time.time() * 1000)
        }
        
        try:
            requests.post(endpoint, json=payload)
        except Exception as e:
            print(f"Error sending feedback to Hextrix AI: {str(e)}")


class NeuralinkInterface:
    """
    Interface for Neuralink brain-computer interface.
    """
    
    def __init__(self, auth_token: str):
        self.base_url = "https://api.neuralink.com/v1"
        self.headers = {"Authorization": f"Bearer {auth_token}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.connection_status = None
        
    def connect(self) -> Dict:
        """
        Establish connection to the Neuralink device.
        """
        endpoint = f"{self.base_url}/connect"
        response = self.session.post(endpoint)
        self.connection_status = response.json()
        return self.connection_status
    
    def disconnect(self) -> Dict:
        """
        Safely disconnect from the Neuralink device.
        """
        endpoint = f"{
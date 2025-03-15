"""
Enhanced Neuralink API interface with AR/VR and retinal projection capabilities
Including visual analysis, OCR, QR reading, and emotional/sentiment analysis for accessibility
Note: Actual implementation requires authorized access to Neuralink BCI
"""
import requests
import json
import time
from typing import Dict, List, Optional, Union, Tuple, Any

class NeuralinkInterface:
    def __init__(self, auth_token: str):
        self.base_url = "https://api.neuralink.com/v1"
        self.headers = {"Authorization": f"Bearer {auth_token}"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.connection_status = None
        self.ar_vr_active = False
        self.hud_elements = {}
        self.visual_analysis_active = False
        self.accessibility_features = {
            "emotion_detection": False,
            "social_cue_analysis": False,
            "ocr": False,
            "qr_reader": False,
            "object_recognition": False
        }
        
    def get_neural_activity(self) -> Dict:
        """
        Returns current neural activity data stream status and metrics.
        """
        # Placeholder for actual BCI data stream
        return {"status": "connected", "data_rate": "1.6Gbps"}
    
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
    
    def calibrate(self) -> Dict:
        """
        Initiate calibration sequence for BCI.
        """
        endpoint = f"{self.base_url}/calibrate"
        response = self.session.post(endpoint)
        return response.json()
    
    def stream_data(self, duration_ms: int = 1000) -> List[Dict]:
        """
        Stream neural data for specified duration in milliseconds.
        """
        endpoint = f"{self.base_url}/stream?duration={duration_ms}"
        response = self.session.get(endpoint)
        return response.json()
    
    def send_command(self, command_type: str, parameters: Dict) -> Dict:
        """
        Send specific command to the BCI.
        
        Args:
            command_type: Type of command (e.g., "motor", "sensory", "cognitive")
            parameters: Command-specific parameters
        """
        endpoint = f"{self.base_url}/command"
        payload = {
            "type": command_type,
            "parameters": parameters,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def get_device_logs(self, start_time: Optional[int] = None, 
                       end_time: Optional[int] = None, 
                       limit: int = 100) -> List[Dict]:
        """
        Retrieve device logs within specified timeframe.
        
        Args:
            start_time: Unix timestamp in milliseconds (optional)
            end_time: Unix timestamp in milliseconds (optional)
            limit: Maximum number of log entries to return
        """
        params = {"limit": limit}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
            
        endpoint = f"{self.base_url}/logs"
        response = self.session.get(endpoint, params=params)
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
    
    def get_user_profile(self) -> Dict:
        """
        Get current user profile and preferences.
        """
        endpoint = f"{self.base_url}/user/profile"
        response = self.session.get(endpoint)
        return response.json()
    
    def train_model(self, training_data: Dict, model_type: str) -> Dict:
        """
        Train or fine-tune a neural interpretation model.
        
        Args:
            training_data: Dictionary containing training examples
            model_type: Type of model to train (e.g., "motor", "speech")
        """
        endpoint = f"{self.base_url}/train"
        payload = {
            "model_type": model_type,
            "training_data": training_data
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # AR/VR Retinal Projection Methods
    
    def initialize_ar_vr(self, resolution: Tuple[int, int] = (1920, 1080), 
                         fov: int = 110,
                         refresh_rate: int = 120) -> Dict:
        """
        Initialize AR/VR capabilities with retinal projection.
        
        Args:
            resolution: Display resolution as (width, height) in pixels
            fov: Field of view in degrees
            refresh_rate: Display refresh rate in Hz
        """
        endpoint = f"{self.base_url}/ar_vr/initialize"
        payload = {
            "resolution": resolution,
            "fov": fov,
            "refresh_rate": refresh_rate,
            "projection_type": "retinal"
        }
        response = self.session.post(endpoint, json=payload)
        if response.status_code == 200:
            self.ar_vr_active = True
        return response.json()
    
    def terminate_ar_vr(self) -> Dict:
        """
        Safely terminate AR/VR projection.
        """
        if not self.ar_vr_active:
            return {"status": "inactive", "message": "AR/VR was not active"}
        
        endpoint = f"{self.base_url}/ar_vr/terminate"
        response = self.session.post(endpoint)
        if response.status_code == 200:
            self.ar_vr_active = False
            self.hud_elements = {}
            self.visual_analysis_active = False
            for feature in self.accessibility_features:
                self.accessibility_features[feature] = False
        return response.json()
    
    def render_frame(self, frame_data: Union[bytes, str], 
                    format_type: str = "encoded",
                    blend_mode: str = "overlay") -> Dict:
        """
        Render a single frame to the retinal projection.
        
        Args:
            frame_data: Either base64 encoded image data or a URL to image
            format_type: Either "encoded" (base64) or "url"
            blend_mode: How to blend with real world ("overlay", "replace", "additive")
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        endpoint = f"{self.base_url}/ar_vr/render"
        payload = {
            "frame_data": frame_data,
            "format_type": format_type,
            "blend_mode": blend_mode,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def start_video_stream(self, stream_url: str, 
                          position: Tuple[float, float] = (0.0, 0.0),
                          size: Tuple[float, float] = (0.7, 0.4)) -> Dict:
        """
        Start streaming video content to AR/VR display.
        
        Args:
            stream_url: URL of the video stream
            position: Normalized position in view (0,0 is center)
            size: Normalized size of video (1.0 is full view)
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        endpoint = f"{self.base_url}/ar_vr/video/start"
        payload = {
            "stream_url": stream_url,
            "position": position,
            "size": size,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def stop_video_stream(self) -> Dict:
        """
        Stop active video stream.
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        endpoint = f"{self.base_url}/ar_vr/video/stop"
        response = self.session.post(endpoint)
        return response.json()
    
    # HUD (Heads-Up Display) Methods
    
    def create_hud_element(self, element_id: str, 
                          element_type: str,
                          content: Dict,
                          position: Tuple[float, float],
                          size: Tuple[float, float],
                          opacity: float = 0.8,
                          anchor: str = "center") -> Dict:
        """
        Create a HUD element in the AR/VR view.
        
        Args:
            element_id: Unique identifier for the element
            element_type: Type of element ("text", "image", "metric", "notification", "menu")
            content: Element content (varies by type)
            position: Normalized position in view (0,0 is center)
            size: Normalized size (1.0 is full view)
            opacity: Element opacity (0.0-1.0)
            anchor: Anchor point ("center", "top_left", "bottom_right", etc.)
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        endpoint = f"{self.base_url}/ar_vr/hud/create"
        payload = {
            "element_id": element_id,
            "element_type": element_type,
            "content": content,
            "position": position,
            "size": size,
            "opacity": opacity,
            "anchor": anchor,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.hud_elements[element_id] = payload
            
        return response.json()
    
    def update_hud_element(self, element_id: str, 
                          updates: Dict) -> Dict:
        """
        Update an existing HUD element.
        
        Args:
            element_id: ID of element to update
            updates: Dictionary of properties to update
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if element_id not in self.hud_elements:
            return {"status": "error", "message": f"Element {element_id} not found"}
        
        endpoint = f"{self.base_url}/ar_vr/hud/update"
        payload = {
            "element_id": element_id,
            "updates": updates,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.patch(endpoint, json=payload)
        
        if response.status_code == 200:
            self.hud_elements[element_id].update(updates)
            
        return response.json()
    
    def delete_hud_element(self, element_id: str) -> Dict:
        """
        Remove a HUD element.
        
        Args:
            element_id: ID of element to remove
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if element_id not in self.hud_elements:
            return {"status": "error", "message": f"Element {element_id} not found"}
        
        endpoint = f"{self.base_url}/ar_vr/hud/delete"
        payload = {
            "element_id": element_id,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.delete(endpoint, json=payload)
        
        if response.status_code == 200:
            del self.hud_elements[element_id]
            
        return response.json()
    
    def create_retinal_notification(self, 
                                  message: str,
                                  level: str = "info",
                                  duration_ms: int = 3000,
                                  position: Tuple[float, float] = (0.7, 0.1)) -> Dict:
        """
        Display a temporary notification in the retinal projection.
        
        Args:
            message: Notification text
            level: Importance level ("info", "warning", "alert", "error")
            duration_ms: Display duration in milliseconds
            position: Normalized position in view (0,0 is center)
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        notification_id = f"notification_{int(time.time() * 1000)}"
        
        return self.create_hud_element(
            element_id=notification_id,
            element_type="notification",
            content={
                "message": message,
                "level": level,
                "duration_ms": duration_ms
            },
            position=position,
            size=(0.3, 0.1),
            opacity=0.9
        )
    
    def calibrate_retinal_projection(self) -> Dict:
        """
        Calibrate the retinal projection for optimal visual quality.
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        endpoint = f"{self.base_url}/ar_vr/calibrate"
        response = self.session.post(endpoint)
        return response.json()
    
    def set_environment(self, environment_type: str,
                       parameters: Dict = None) -> Dict:
        """
        Set the AR/VR environment type.
        
        Args:
            environment_type: Type of environment ("passthrough", "mixed", "virtual")
            parameters: Environment-specific parameters
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        if parameters is None:
            parameters = {}
            
        endpoint = f"{self.base_url}/ar_vr/environment"
        payload = {
            "environment_type": environment_type,
            "parameters": parameters,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def create_3d_object(self, object_id: str,
                        model_data: Union[str, Dict],
                        position: Tuple[float, float, float],
                        rotation: Tuple[float, float, float],
                        scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
                        physics_enabled: bool = False) -> Dict:
        """
        Create a 3D object in the AR/VR space.
        
        Args:
            object_id: Unique identifier for the object
            model_data: Either a URL to a 3D model or model definition
            position: 3D position coordinates (x, y, z)
            rotation: Rotation in degrees (pitch, yaw, roll)
            scale: Scale factors (x, y, z)
            physics_enabled: Whether object should have physics simulation
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        endpoint = f"{self.base_url}/ar_vr/objects/create"
        payload = {
            "object_id": object_id,
            "model_data": model_data,
            "position": position,
            "rotation": rotation,
            "scale": scale,
            "physics_enabled": physics_enabled,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def get_gaze_target(self) -> Dict:
        """
        Get information about what the user is currently looking at.
        Returns gaze coordinates and any targeted objects/elements.
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        endpoint = f"{self.base_url}/ar_vr/gaze"
        response = self.session.get(endpoint)
        return response.json()
    
    # Visual Analysis Methods (Google Lens-like functionality)
    
    def initialize_visual_analysis(self, 
                                 features: List[str] = None) -> Dict:
        """
        Initialize visual analysis capabilities.
        
        Args:
            features: List of visual analysis features to enable:
                      ["object_detection", "ocr", "qr_code", "landmark", 
                       "logo", "face", "label", "web_search"]
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if features is None:
            features = ["object_detection", "ocr", "qr_code"]
            
        endpoint = f"{self.base_url}/visual/initialize"
        payload = {
            "features": features,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.visual_analysis_active = True
            
        return response.json()
    
    def analyze_visual_field(self, 
                           features: List[str] = None,
                           region: Dict = None) -> Dict:
        """
        Analyze the current visual field and return results.
        
        Args:
            features: Specific features to analyze in this request
            region: Restrict analysis to specific region of visual field
                   Format: {"x": float, "y": float, "width": float, "height": float}
                   where x,y,width,height are normalized (0.0-1.0)
        """
        if not self.ar_vr_active or not self.visual_analysis_active:
            return {"status": "error", "message": "Visual analysis not initialized"}
            
        endpoint = f"{self.base_url}/visual/analyze"
        payload = {
            "timestamp": int(time.time() * 1000)
        }
        
        if features is not None:
            payload["features"] = features
            
        if region is not None:
            payload["region"] = region
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def start_continuous_visual_analysis(self, 
                                       interval_ms: int = 500,
                                       features: List[str] = None,
                                       callback_id: str = "default_visual_callback") -> Dict:
        """
        Start continuous analysis of the visual field at specified interval.
        
        Args:
            interval_ms: Time between analyses in milliseconds
            features: Specific features to analyze
            callback_id: Identifier for callback handling results
        """
        if not self.ar_vr_active or not self.visual_analysis_active:
            return {"status": "error", "message": "Visual analysis not initialized"}
            
        endpoint = f"{self.base_url}/visual/continuous/start"
        payload = {
            "interval_ms": interval_ms,
            "callback_id": callback_id,
            "timestamp": int(time.time() * 1000)
        }
        
        if features is not None:
            payload["features"] = features
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def stop_continuous_visual_analysis(self, 
                                      callback_id: str = "default_visual_callback") -> Dict:
        """
        Stop continuous visual analysis.
        
        Args:
            callback_id: Identifier for callback to stop
        """
        if not self.ar_vr_active or not self.visual_analysis_active:
            return {"status": "error", "message": "Visual analysis not initialized"}
            
        endpoint = f"{self.base_url}/visual/continuous/stop"
        payload = {
            "callback_id": callback_id,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # OCR Methods
    
    def enable_ocr(self, 
                 continuous: bool = False,
                 languages: List[str] = None,
                 display_mode: str = "highlight") -> Dict:
        """
        Enable Optical Character Recognition on visual field.
        
        Args:
            continuous: Whether to continuously scan for text
            languages: List of language codes to recognize
            display_mode: How to display recognized text 
                        ("highlight", "overlay", "sidebar", "tooltip")
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if not self.visual_analysis_active:
            self.initialize_visual_analysis(["ocr"])
            
        if languages is None:
            languages = ["en"]
            
        endpoint = f"{self.base_url}/visual/ocr/enable"
        payload = {
            "continuous": continuous,
            "languages": languages,
            "display_mode": display_mode,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.accessibility_features["ocr"] = True
            
        return response.json()
    
    def disable_ocr(self) -> Dict:
        """
        Disable OCR functionality.
        """
        if not self.ar_vr_active or not self.accessibility_features["ocr"]:
            return {"status": "error", "message": "OCR not enabled"}
            
        endpoint = f"{self.base_url}/visual/ocr/disable"
        response = self.session.post(endpoint)
        
        if response.status_code == 200:
            self.accessibility_features["ocr"] = False
            
        return response.json()
    
    def extract_text(self, 
                   region: Dict = None,
                   languages: List[str] = None) -> Dict:
        """
        Extract text from current visual field or specific region.
        
        Args:
            region: Restrict OCR to specific region of visual field
                  Format: {"x": float, "y": float, "width": float, "height": float}
            languages: List of language codes to recognize
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if languages is None:
            languages = ["en"]
            
        endpoint = f"{self.base_url}/visual/ocr/extract"
        payload = {
            "languages": languages,
            "timestamp": int(time.time() * 1000)
        }
        
        if region is not None:
            payload["region"] = region
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def translate_text(self, 
                     text: str,
                     source_lang: str,
                     target_lang: str) -> Dict:
        """
        Translate extracted text.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        endpoint = f"{self.base_url}/visual/ocr/translate"
        payload = {
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # QR Code Reader Methods
    
    def enable_qr_reader(self, 
                        continuous: bool = True,
                        types: List[str] = None,
                        auto_action: bool = False) -> Dict:
        """
        Enable QR code and barcode detection.
        
        Args:
            continuous: Whether to continuously scan for codes
            types: Types of codes to detect ["qr", "barcode", "data_matrix", etc]
            auto_action: Whether to automatically perform actions for known code types
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if not self.visual_analysis_active:
            self.initialize_visual_analysis(["qr_code"])
            
        if types is None:
            types = ["qr", "barcode"]
            
        endpoint = f"{self.base_url}/visual/qr/enable"
        payload = {
            "continuous": continuous,
            "types": types,
            "auto_action": auto_action,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.accessibility_features["qr_reader"] = True
            
        return response.json()
    
    def disable_qr_reader(self) -> Dict:
        """
        Disable QR code reading functionality.
        """
        if not self.ar_vr_active or not self.accessibility_features["qr_reader"]:
            return {"status": "error", "message": "QR reader not enabled"}
            
        endpoint = f"{self.base_url}/visual/qr/disable"
        response = self.session.post(endpoint)
        
        if response.status_code == 200:
            self.accessibility_features["qr_reader"] = False
            
        return response.json()
    
    def scan_qr_code(self, 
                   region: Dict = None) -> Dict:
        """
        Manually trigger a QR code scan.
        
        Args:
            region: Restrict scanning to specific region of visual field
                  Format: {"x": float, "y": float, "width": float, "height": float}
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        endpoint = f"{self.base_url}/visual/qr/scan"
        payload = {
            "timestamp": int(time.time() * 1000)
        }
        
        if region is not None:
            payload["region"] = region
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Emotion and Social Cue Analysis Methods
    
    def enable_emotion_detection(self,
                               continuous: bool = True,
                               sensitivity: float = 0.7,
                               display_mode: str = "subtle_overlay") -> Dict:
        """
        Enable emotion detection for accessibility.
        
        Args:
            continuous: Whether to continuously analyze emotions
            sensitivity: Detection sensitivity (0.0-1.0)
            display_mode: How to display emotions ("subtle_overlay", "text_labels", 
                        "color_coded", "icon_based", "detailed")
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if not self.visual_analysis_active:
            self.initialize_visual_analysis(["face"])
            
        endpoint = f"{self.base_url}/accessibility/emotion/enable"
        payload = {
            "continuous": continuous,
            "sensitivity": sensitivity,
            "display_mode": display_mode,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.accessibility_features["emotion_detection"] = True
            
        return response.json()
    
    def disable_emotion_detection(self) -> Dict:
        """
        Disable emotion detection.
        """
        if not self.ar_vr_active or not self.accessibility_features["emotion_detection"]:
            return {"status": "error", "message": "Emotion detection not enabled"}
            
        endpoint = f"{self.base_url}/accessibility/emotion/disable"
        response = self.session.post(endpoint)
        
        if response.status_code == 200:
            self.accessibility_features["emotion_detection"] = False
            
        return response.json()
    
    def configure_emotion_detection(self, 
                                  settings: Dict) -> Dict:
        """
        Configure emotion detection settings.
        
        Args:
            settings: Dictionary with configuration options:
                     - emotions_to_track: List of emotions to detect
                     - highlight_intensity: How strongly to highlight (0.0-1.0)
                     - notification_threshold: Threshold for explicit notifications
                     - contextual_cues: Whether to provide social context analysis
                     - facial_feature_focus: Which facial features to focus on
        """
        if not self.ar_vr_active or not self.accessibility_features["emotion_detection"]:
            return {"status": "error", "message": "Emotion detection not enabled"}
            
        endpoint = f"{self.base_url}/accessibility/emotion/configure"
        payload = {
            "settings": settings,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.patch(endpoint, json=payload)
        return response.json()
    
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
        Set privacy preferences for the BCI interface.
        
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
    
    # Error handling and diagnostic methods
    
    def get_diagnostic_info(self) -> Dict:
        """
        Get detailed diagnostic information about the device and connection.
        """
        endpoint = f"{self.base_url}/diagnostics"
        response = self.session.get(endpoint)
        return response.json()
    
    def report_issue(self, 
                   issue_type: str,
                   description: str,
                   severity: str = "medium",
                   include_logs: bool = True) -> Dict:
        """
        Report an issue with the device or interface.
        
        Args:
            issue_type: Type of issue ("hardware", "software", "connectivity", "other")
            description: Detailed description of the issue
            severity: Issue severity ("low", "medium", "high", "critical")
            include_logs: Whether to include recent logs with the report
        """
        endpoint = f"{self.base_url}/report_issue"
        payload = {
            "issue_type": issue_type,
            "description": description,
            "severity": severity,
            "include_logs": include_logs,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def run_self_test(self, test_types: List[str] = None) -> Dict:
        """
        Run self-diagnostic tests.
        
        Args:
            test_types: Types of tests to run (None = all tests)
                      ["connectivity", "calibration", "sensors", "electrodes", 
                       "data_processing", "power", "thermal"]
        """
        endpoint = f"{self.base_url}/self_test"
        payload = {
            "timestamp": int(time.time() * 1000)
        }
        
        if test_types is not None:
            payload["test_types"] = test_types
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Personalization methods
    
    def save_preferences(self, 
                       category: str,
                       preferences: Dict) -> Dict:
        """
        Save user preferences for a specific category.
        
        Args:
            category: Preference category 
                     ("accessibility", "ar_vr", "notifications", "ui", "privacy")
            preferences: Dictionary of preference settings
        """
        endpoint = f"{self.base_url}/preferences/{category}"
        payload = {
            "preferences": preferences,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.put(endpoint, json=payload)
        return response.json()
    
    def get_preferences(self, category: str) -> Dict:
        """
        Get user preferences for a specific category.
        
        Args:
            category: Preference category
        """
        endpoint = f"{self.base_url}/preferences/{category}"
        response = self.session.get(endpoint)
        return response.json()
    
    def create_custom_command(self, 
                            command_id: str,
                            command_type: str,
                            neural_pattern: Dict,
                            action: Dict,
                            description: str = None) -> Dict:
        """
        Create a custom neural command mapping.
        
        Args:
            command_id: Unique identifier for the command
            command_type: Type of command ("thought", "motor", "hybrid")
            neural_pattern: Neural pattern definition
            action: Action to perform when pattern is detected
            description: Optional description of the command
        """
        endpoint = f"{self.base_url}/custom_commands/create"
        payload = {
            "command_id": command_id,
            "command_type": command_type,
            "neural_pattern": neural_pattern,
            "action": action,
            "timestamp": int(time.time() * 1000)
        }
        
        if description is not None:
            payload["description"] = description
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def get_custom_commands(self) -> Dict:
        """
        Get all custom command mappings.
        """
        endpoint = f"{self.base_url}/custom_commands"
        response = self.session.get(endpoint)
        return response.json()
    
    def delete_custom_command(self, command_id: str) -> Dict:
        """
        Delete a custom command mapping.
        
        Args:
            command_id: ID of the command to delete
        """
        endpoint = f"{self.base_url}/custom_commands/{command_id}"
        response = self.session.delete(endpoint)
        return response.json()
    
    # Voice and audio interface methods
    
    def text_to_speech(self, 
                     text: str,
                     voice_id: str = "default",
                     speed: float = 1.0,
                     pitch: float = 1.0) -> Dict:
        """
        Convert text to speech output for neural interface.
        
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
        Play audio through neural interface.
        
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

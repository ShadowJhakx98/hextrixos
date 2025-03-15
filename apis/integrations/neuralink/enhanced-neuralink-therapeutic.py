"""
Enhanced Neuralink API interface with AR/VR and retinal projection capabilities
Extended with therapeutic applications for ADHD and anxiety disorders
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
        self.therapeutic_session_active = False
        self.therapeutic_session_data = {}
        self.current_therapy_type = None
        
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
    
    # ------ THERAPEUTIC APPLICATIONS EXTENSION ------
    
    def initialize_therapeutic_session(self, 
                                      therapy_type: str,
                                      user_profile: Dict,
                                      session_parameters: Dict = None) -> Dict:
        """
        Initialize a therapeutic session for ADHD, anxiety, or other conditions.
        
        Args:
            therapy_type: Type of therapy ("adhd_focus", "anxiety_reduction", 
                         "exposure_therapy", "mindfulness", "social_cue_training")
            user_profile: User profile with condition details and preferences
            session_parameters: Optional parameters for the session
        
        Returns:
            Session initialization status and session ID
        """
        if not self.ar_vr_active:
            # Auto-initialize AR/VR with optimal therapeutic settings
            self.initialize_ar_vr(resolution=(2560, 1440), refresh_rate=90)
        
        if session_parameters is None:
            session_parameters = {}
            
        endpoint = f"{self.base_url}/therapeutic/initialize"
        payload = {
            "therapy_type": therapy_type,
            "user_profile": user_profile,
            "session_parameters": session_parameters,
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.therapeutic_session_active = True
            self.therapeutic_session_data = response.json()
            self.current_therapy_type = therapy_type
            
        return response.json()
    
    def terminate_therapeutic_session(self, save_progress: bool = True) -> Dict:
        """
        Safely terminate the current therapeutic session.
        
        Args:
            save_progress: Whether to save session progress and metrics
            
        Returns:
            Session termination status and summary
        """
        if not self.therapeutic_session_active:
            return {"status": "inactive", "message": "No therapeutic session is active"}
        
        endpoint = f"{self.base_url}/therapeutic/terminate"
        payload = {
            "save_progress": save_progress,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        
        if response.status_code == 200:
            self.therapeutic_session_active = False
            self.current_therapy_type = None
            session_summary = response.json()
            self.therapeutic_session_data = {}
            return session_summary
        
        return response.json()
    
    def get_therapeutic_metrics(self) -> Dict:
        """
        Get real-time metrics for the current therapeutic session.
        Includes focus levels, anxiety indicators, and other relevant data.
        
        Returns:
            Current session metrics and analysis
        """
        if not self.therapeutic_session_active:
            return {"status": "inactive", "message": "No therapeutic session is active"}
        
        endpoint = f"{self.base_url}/therapeutic/metrics"
        params = {
            "session_id": self.therapeutic_session_data.get("session_id")
        }
        response = self.session.get(endpoint, params=params)
        return response.json()
    
    # ADHD-specific therapeutic functions
    
    def create_focus_environment(self, 
                                environment_preset: str = "study",
                                customization: Dict = None) -> Dict:
        """
        Create an immersive environment optimized for focus and concentration.
        
        Args:
            environment_preset: Preset environment type
                               ("study", "work", "creative", "exam")
            customization: Custom environment parameters
            
        Returns:
            Environment creation status
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        if customization is None:
            customization = {}
            
        # Default settings based on research for ADHD focus enhancement
        default_settings = {
            "ambient_noise": "white_noise",
            "noise_level": 0.2,
            "visual_distractions": "minimal",
            "color_palette": "calm_neutral",
            "lighting": "soft_diffused",
            "environment_boundaries": "clearly_defined",
            "organization": "structured"
        }
        
        # Override defaults with any custom settings
        settings = {**default_settings, **customization}
        
        endpoint = f"{self.base_url}/therapeutic/adhd/environment"
        payload = {
            "environment_preset": environment_preset,
            "settings": settings,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def setup_multi_window_workspace(self, 
                                    windows: List[Dict],
                                    layout_type: str = "grid") -> Dict:
        """
        Create a multi-window workspace optimized for ADHD users.
        Research shows positioning multiple windows simultaneously reduces
        distraction during task switching.
        
        Args:
            windows: List of window configurations (content, size, position)
            layout_type: Organization style ("grid", "circular", "priority_based")
            
        Returns:
            Workspace creation status
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
        
        endpoint = f"{self.base_url}/therapeutic/adhd/workspace"
        payload = {
            "windows": windows,
            "layout_type": layout_type,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def create_focus_reminder(self, 
                            reminder_type: str = "tactile",
                            interval_sec: int = 300,
                            adaptive: bool = True) -> Dict:
        """
        Set up attention renewal prompts based on self-monitoring technologies
        like MotivAider that have shown effectiveness in ADHD studies.
        
        Args:
            reminder_type: Type of reminder ("tactile", "visual", "auditory")
            interval_sec: Time between reminders in seconds
            adaptive: Whether to adjust reminder timing based on neural data
            
        Returns:
            Reminder system status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
        
        endpoint = f"{self.base_url}/therapeutic/adhd/reminder"
        payload = {
            "reminder_type": reminder_type,
            "interval_sec": interval_sec,
            "adaptive": adaptive,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def start_working_memory_training(self, 
                                     difficulty_level: int = 1,
                                     session_duration_min: int = 15,
                                     training_type: str = "n_back") -> Dict:
        """
        Launch computerized working memory training program
        shown to improve working memory capacity in ADHD studies.
        
        Args:
            difficulty_level: Starting difficulty (1-10)
            session_duration_min: Training duration in minutes
            training_type: Training paradigm ("n_back", "dual_task", "sequence_memory")
            
        Returns:
            Training session status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
        
        endpoint = f"{self.base_url}/therapeutic/adhd/memory_training"
        payload = {
            "difficulty_level": difficulty_level,
            "session_duration_min": session_duration_min,
            "training_type": training_type,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Anxiety-specific therapeutic functions
    
    def create_exposure_scenario(self, 
                               scenario_type: str,
                               intensity_level: int = 1,
                               customization: Dict = None) -> Dict:
        """
        Create a controlled exposure therapy scenario for anxiety disorders.
        Provides gradual exposure to anxiety-triggering situations in a safe space.
        
        Args:
            scenario_type: Type of scenario ("social", "phobia", "ptsd", "panic")
            intensity_level: Intensity from 1 (mild) to 10 (intense)
            customization: Custom scenario parameters
            
        Returns:
            Scenario creation status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
        
        if customization is None:
            customization = {}
            
        endpoint = f"{self.base_url}/therapeutic/anxiety/exposure"
        payload = {
            "scenario_type": scenario_type,
            "intensity_level": intensity_level,
            "customization": customization,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def start_mindfulness_session(self, 
                                session_type: str = "guided",
                                duration_min: int = 10,
                                environment: str = "nature") -> Dict:
        """
        Launch a VR mindfulness and meditation session for anxiety reduction.
        
        Args:
            session_type: Type of session ("guided", "unguided", "body_scan")
            duration_min: Session duration in minutes
            environment: Virtual environment setting
            
        Returns:
            Mindfulness session status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
        
        endpoint = f"{self.base_url}/therapeutic/anxiety/mindfulness"
        payload = {
            "session_type": session_type,
            "duration_min": duration_min,
            "environment": environment,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def create_social_cue_trainer(self, 
                                difficulty: str = "beginner",
                                scenario: str = "conversation",
                                feedback_mode: str = "real_time") -> Dict:
        """
        Create an AR-based social interaction trainer that provides
        feedback on social cues and group dynamics.
        
        Args:
            difficulty: Difficulty level ("beginner", "intermediate", "advanced")
            scenario: Social scenario type
            feedback_mode: When to provide feedback ("real_time", "post_interaction")
            
        Returns:
            Social trainer status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
        
        endpoint = f"{self.base_url}/therapeutic/anxiety/social_trainer"
        payload = {
            "difficulty": difficulty,
            "scenario": scenario,
            "feedback_mode": feedback_mode,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Sensory control functions
    
    def customize_sensory_environment(self, 
                                     audio_settings: Dict = None,
                                     visual_settings: Dict = None,
                                     haptic_settings: Dict = None) -> Dict:
        """
        Customize the sensory environment for optimal neural state.
        Both ADHD and anxiety patients benefit from controlled sensory input.
        
        Args:
            audio_settings: Audio environment settings
            visual_settings: Visual environment settings
            haptic_settings: Haptic feedback settings
            
        Returns:
            Sensory customization status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
        
        settings = {}
        
        if audio_settings:
            settings["audio"] = audio_settings
        if visual_settings:
            settings["visual"] = visual_settings
        if haptic_settings:
            settings["haptic"] = haptic_settings
            
        endpoint = f"{self.base_url}/therapeutic/sensory/customize"
        payload = {
            "settings": settings,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def create_real_time_feedback_system(self, 
                                        metrics: List[str],
                                        feedback_types: List[str],
                                        thresholds: Dict) -> Dict:
        """
        Create a real-time neural feedback system that provides cues
        based on detected attentional state or anxiety levels.
        
        Args:
            metrics: Neural metrics to monitor
                   ("attention", "anxiety", "focus", "cognitive_load")
            feedback_types: Types of feedback to provide
                          ("visual", "auditory", "haptic")
            thresholds: Threshold values for triggering feedback
            
        Returns:
            Feedback system status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
        
        endpoint = f"{self.base_url}/therapeutic/feedback/create"
        payload = {
            "metrics": metrics,
            "feedback_types": feedback_types,
            "thresholds": thresholds,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def update_feedback_thresholds(self, 
                                  metric_updates: Dict) -> Dict:
        """
        Update thresholds for the real-time neural feedback system.
        
        Args:
            metric_updates: Dictionary mapping metrics to new threshold values
            
        Returns:
            Update status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
            
        endpoint = f"{self.base_url}/therapeutic/feedback/update"
        payload = {
            "metric_updates": metric_updates,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.patch(endpoint, json=payload)
        return response.json()
    
    def pause_feedback_system(self, duration_sec: int = None) -> Dict:
        """
        Temporarily pause the feedback system.
        
        Args:
            duration_sec: Duration to pause in seconds (None for indefinite)
            
        Returns:
            Pause status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
            
        endpoint = f"{self.base_url}/therapeutic/feedback/pause"
        payload = {
            "duration_sec": duration_sec,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def resume_feedback_system(self) -> Dict:
        """
        Resume a paused feedback system.
        
        Returns:
            Resume status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
            
        endpoint = f"{self.base_url}/therapeutic/feedback/resume"
        payload = {
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Progress tracking and reporting
    
    def get_therapeutic_progress(self, 
                               time_period: str = "all",
                               metrics: List[str] = None) -> Dict:
        """
        Get progress reports for therapeutic interventions.
        
        Args:
            time_period: Time period to analyze ("day", "week", "month", "all")
            metrics: Specific metrics to include (None for all)
            
        Returns:
            Progress data and analysis
        """
        endpoint = f"{self.base_url}/therapeutic/progress"
        params = {
            "time_period": time_period,
            "user_id": self.get_user_profile().get("user_id")
        }
        
        if metrics:
            params["metrics"] = ",".join(metrics)
            
        response = self.session.get(endpoint, params=params)
        return response.json()
    
    def generate_therapeutic_report(self, 
                                  report_type: str = "summary",
                                  time_period: str = "week",
                                  include_recommendations: bool = True) -> Dict:
        """
        Generate a comprehensive report on therapeutic progress.
        
        Args:
            report_type: Type of report ("summary", "detailed", "clinical")
            time_period: Time period to analyze
            include_recommendations: Whether to include AI recommendations
            
        Returns:
            Generated report
        """
        endpoint = f"{self.base_url}/therapeutic/report"
        payload = {
            "report_type": report_type,
            "time_period": time_period,
            "include_recommendations": include_recommendations,
            "user_id": self.get_user_profile().get("user_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Cognitive behavioral therapy functions
    
    def start_cbt_exercise(self, 
                         exercise_type: str,
                         difficulty: str = "moderate",
                         customization: Dict = None) -> Dict:
        """
        Start a cognitive behavioral therapy exercise.
        
        Args:
            exercise_type: Type of CBT exercise
                        ("thought_record", "behavioral_activation", 
                         "exposure_hierarchy", "cognitive_restructuring")
            difficulty: Difficulty level
            customization: Custom exercise parameters
            
        Returns:
            Exercise session status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
            
        if customization is None:
            customization = {}
            
        endpoint = f"{self.base_url}/therapeutic/cbt/start"
        payload = {
            "exercise_type": exercise_type,
            "difficulty": difficulty,
            "customization": customization,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def record_thought_pattern(self, 
                             situation: str,
                             thoughts: List[str],
                             emotions: Dict[str, int],
                             behaviors: List[str],
                             alternative_thoughts: List[str] = None) -> Dict:
        """
        Record a thought pattern for CBT thought records.
        
        Args:
            situation: Description of the situation
            thoughts: List of automatic thoughts
            emotions: Dictionary mapping emotions to intensity (0-100)
            behaviors: List of resulting behaviors
            alternative_thoughts: List of alternative balanced thoughts
            
        Returns:
            Recorded thought pattern status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
            
        endpoint = f"{self.base_url}/therapeutic/cbt/thought_record"
        payload = {
            "situation": situation,
            "thoughts": thoughts,
            "emotions": emotions,
            "behaviors": behaviors,
            "alternative_thoughts": alternative_thoughts,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Neurofeedback training
    
    def start_neurofeedback_training(self, 
                                   target_states: List[str],
                                   session_duration_min: int = 20,
                                   difficulty: str = "adaptive",
                                   feedback_mode: str = "game") -> Dict:
        """
        Start a neurofeedback training session using real-time neural data.
        
        Args:
            target_states: Neural states to target
                         ("focus", "calm", "executive_function", "flow")
            session_duration_min: Session duration in minutes
            difficulty: Difficulty level ("beginner", "intermediate", "advanced", "adaptive")
            feedback_mode: How to present feedback ("simple", "game", "immersive")
            
        Returns:
            Neurofeedback session status
        """
        if not self.therapeutic_session_active:
            return {"status": "error", "message": "Therapeutic session not active"}
            
        endpoint = f"{self.base_url}/therapeutic/neurofeedback/start"
        payload = {
            "target_states": target_states,
            "session_duration_min": session_duration_min,
            "difficulty": difficulty,
            "feedback_mode": feedback_mode,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def pause_neurofeedback(self) -> Dict:
        """
        Pause an ongoing neurofeedback session.
        
        Returns:
            Pause status
        """
        endpoint = f"{self.base_url}/therapeutic/neurofeedback/pause"
        payload = {
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def resume_neurofeedback(self) -> Dict:
        """
        Resume a paused neurofeedback session.
        
        Returns:
            Resume status
        """
        endpoint = f"{self.base_url}/therapeutic/neurofeedback/resume"
        payload = {
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def end_neurofeedback(self) -> Dict:
        """
        End a neurofeedback session and get results.
        
        Returns:
            Session results and stats
        """
        endpoint = f"{self.base_url}/therapeutic/neurofeedback/end"
        payload = {
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Breathing and physiological regulation
    
    def start_breathing_exercise(self, 
                               pattern: str = "4-7-8",
                               duration_min: int = 5,
                               guidance_type: str = "visual",
                               environment: str = "calm") -> Dict:
        """
        Start a guided breathing exercise for anxiety management.
        
        Args:
            pattern: Breathing pattern 
                    ("4-7-8", "box_breathing", "diaphragmatic", "alternate_nostril")
            duration_min: Duration in minutes
            guidance_type: Type of guidance ("visual", "auditory", "haptic", "combined")
            environment: Virtual environment setting
            
        Returns:
            Breathing exercise status
        """
        if not self.ar_vr_active:
            self.initialize_ar_vr()
            
        endpoint = f"{self.base_url}/therapeutic/breathing/start"
        payload = {
            "pattern": pattern,
            "duration_min": duration_min,
            "guidance_type": guidance_type,
            "environment": environment,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def monitor_physiological_state(self, 
                                  metrics: List[str] = None) -> Dict:
        """
        Get real-time physiological state metrics.
        
        Args:
            metrics: Specific metrics to monitor (None for all available)
                   ("heart_rate", "heart_rate_variability", "respiration_rate",
                    "skin_conductance", "neural_activity")
            
        Returns:
            Current physiological metrics
        """
        if metrics is None:
            metrics = ["heart_rate", "heart_rate_variability", "respiration_rate"]
            
        endpoint = f"{self.base_url}/therapeutic/physiological/current"
        params = {
            "metrics": ",".join(metrics),
            "session_id": self.therapeutic_session_data.get("session_id")
        }
        response = self.session.get(endpoint, params=params)
        return response.json()
    
    # Emergency intervention
    
    def trigger_calming_protocol(self, 
                               intensity: str = "moderate",
                               override_settings: bool = True) -> Dict:
        """
        Trigger an emergency calming protocol for acute anxiety episodes.
        
        Args:
            intensity: Intervention intensity ("mild", "moderate", "strong")
            override_settings: Whether to override current settings
            
        Returns:
            Protocol activation status
        """
        endpoint = f"{self.base_url}/therapeutic/emergency/calm"
        payload = {
            "intensity": intensity,
            "override_settings": override_settings,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def trigger_focus_protocol(self, 
                             intensity: str = "moderate",
                             duration_min: int = 30,
                             override_settings: bool = True) -> Dict:
        """
        Trigger an emergency focus protocol for critical tasks.
        
        Args:
            intensity: Intervention intensity ("mild", "moderate", "strong")
            duration_min: Duration in minutes
            override_settings: Whether to override current settings
            
        Returns:
            Protocol activation status
        """
        endpoint = f"{self.base_url}/therapeutic/emergency/focus"
        payload = {
            "intensity": intensity,
            "duration_min": duration_min,
            "override_settings": override_settings,
            "session_id": self.therapeutic_session_data.get("session_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Integration with external therapeutic systems
    
    def connect_external_therapeutic_system(self, 
                                          system_type: str,
                                          connection_params: Dict) -> Dict:
        """
        Connect to an external therapeutic system.
        
        Args:
            system_type: Type of external system
                       ("therapist_dashboard", "medical_record", "wearable", "smart_home")
            connection_params: Connection parameters
            
        Returns:
            Connection status
        """
        endpoint = f"{self.base_url}/therapeutic/external/connect"
        payload = {
            "system_type": system_type,
            "connection_params": connection_params,
            "user_id": self.get_user_profile().get("user_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def share_therapeutic_data(self, 
                             data_types: List[str],
                             recipient_id: str,
                             time_period: str = "session",
                             anonymize: bool = False) -> Dict:
        """
        Share therapeutic data with an authorized recipient (e.g., therapist).
        
        Args:
            data_types: Types of data to share
                      ("metrics", "progress", "sessions", "neural_activity")
            recipient_id: ID of authorized recipient
            time_period: Period of data to share
            anonymize: Whether to anonymize personal data
            
        Returns:
            Data sharing status
        """
        endpoint = f"{self.base_url}/therapeutic/data/share"
        payload = {
            "data_types": data_types,
            "recipient_id": recipient_id,
            "time_period": time_period,
            "anonymize": anonymize,
            "user_id": self.get_user_profile().get("user_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Session scheduling and reminders
    
    def schedule_therapeutic_session(self, 
                                   therapy_type: str,
                                   schedule_time: str,
                                   recurrence: str = "once",
                                   parameters: Dict = None) -> Dict:
        """
        Schedule a future therapeutic session.
        
        Args:
            therapy_type: Type of therapy session
            schedule_time: ISO format datetime string
            recurrence: Recurrence pattern ("once", "daily", "weekly", "custom")
            parameters: Session parameters
            
        Returns:
            Scheduling status
        """
        if parameters is None:
            parameters = {}
            
        endpoint = f"{self.base_url}/therapeutic/schedule/create"
        payload = {
            "therapy_type": therapy_type,
            "schedule_time": schedule_time,
            "recurrence": recurrence,
            "parameters": parameters,
            "user_id": self.get_user_profile().get("user_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    def create_therapeutic_reminder(self, 
                                  reminder_type: str,
                                  schedule: Dict,
                                  message: str = None,
                                  notification_params: Dict = None) -> Dict:
        """
        Create a reminder for therapeutic activities.
        
        Args:
            reminder_type: Type of reminder ("medication", "practice", "session")
            schedule: Scheduling information
            message: Custom reminder message
            notification_params: Notification delivery parameters
            
        Returns:
            Reminder creation status
        """
        if notification_params is None:
            notification_params = {
                "mode": "mixed",
                "priority": "normal"
            }
            
        endpoint = f"{self.base_url}/therapeutic/reminder/create"
        payload = {
            "reminder_type": reminder_type,
            "schedule": schedule,
            "message": message,
            "notification_params": notification_params,
            "user_id": self.get_user_profile().get("user_id"),
            "timestamp": int(time.time() * 1000)
        }
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Therapeutic API metadata and versioning
    
    def get_therapeutic_api_version(self) -> Dict:
        """
        Get version information for the therapeutic API.
        
        Returns:
            API version information
        """
        endpoint = f"{self.base_url}/therapeutic/version"
        response = self.session.get(endpoint)
        return response.json()
    
    def get_available_therapeutic_modules(self) -> Dict:
        """
        Get information about available therapeutic modules and capabilities.
        
        Returns:
            Available modules and capabilities
        """
        endpoint = f"{self.base_url}/therapeutic/modules"
        response = self.session.get(endpoint)
        return response.json()

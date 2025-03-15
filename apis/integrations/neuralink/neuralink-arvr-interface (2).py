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

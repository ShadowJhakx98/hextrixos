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
    
    def analyze_social_situation(self) -> Dict:
        """
        Perform on-demand analysis of current social situation.
        Returns detailed information about group dynamics, social context, etc.
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        endpoint = f"{self.base_url}/accessibility/social_cue/analyze"
        response = self.session.post(endpoint)
        return response.json()
    
    # Object Recognition and Scene Understanding
    
    def enable_object_recognition(self,
                                continuous: bool = True,
                                min_confidence: float = 0.7,
                                max_objects: int = 10,
                                highlight_objects: bool = True) -> Dict:
        """
        Enable object recognition for accessibility.
        
        Args:
            continuous: Whether to continuously recognize objects
            min_confidence: Minimum confidence threshold (0.0-1.0)
            max_objects: Maximum objects to track simultaneously
            highlight_objects: Whether to visually highlight recognized objects
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        if not self.visual_analysis_active:
            self.initialize_visual_analysis(["object_detection"])
            
        endpoint = f"{self.base_url}/accessibility/object/enable"
        payload = {
            "continuous": continuous,
            "min_confidence": min_confidence,
            "max_objects": max_objects,
            "highlight_objects": highlight_objects,
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
            
        endpoint = f"{self.base_url}/accessibility/object/disable"
        response = self.session.post(endpoint)
        
        if response.status_code == 200:
            self.accessibility_features["object_recognition"] = False
            
        return response.json()
    
    def identify_objects(self,
                       region: Dict = None,
                       classes: List[str] = None) -> Dict:
        """
        Perform on-demand object identification.
        
        Args:
            region: Restrict analysis to specific region of visual field
            classes: List of object classes to specifically detect
        """
        if not self.ar_vr_active:
            return {"status": "error", "message": "AR/VR not initialized"}
            
        endpoint = f"{self.base_url}/accessibility/object/identify"
        payload = {
            "timestamp": int(time.time() * 1000)
        }
        
        if region is not None:
            payload["region"] = region
            
        if classes is not None:
            payload["classes"] = classes
            
        response = self.session.post(endpoint, json=payload)
        return response.json()
    
    # Facial Expression and Emotion HUD Integration
    
    def create_emotion_hud(self, 
                         position: Tuple[float, float] = (0.9, 0.1),
                         size: Tuple[float, float] = (0.2, 0.6),
                         style: str = "minimal") -> Dict:
        """
        Create a dedicated HUD for emotional analysis display.
        
        Args:
            position: Normalized position in view (0,0 is center)
            size: Normalized size (1.0 is full view)
            style: Visual style ("minimal", "detailed", "icon_based", "text_only")
        """
        if not self.ar_vr_active or not self.accessibility_features["emotion_detection"]:
            return {"status": "error", "message": "Emotion detection not enabled"}
            
        hud_id = "emotion_hud"
        
        # First check if the HUD already exists
        if hud_id in self.hud_elements:
            return {"status": "exists", "message": "Emotion HUD already exists"}
            
        # Create emotion HUD container
        content = {
            "style": style,
            "sections": [
                {
                    "title": "Detected Emotions",
                    "type": "emotion_list",
                    "max_entries": 5
                },
                {
                    "title": "Primary Emotion",
                    "type": "emotion_gauge",
                    "emotion": None,
                    "intensity": 0.0
                },
                {
                    "title": "Social Context",
                    "type": "text_display",
                    "text": "No social context analyzed yet"
                }
            ],
            "settings": {
                "update_frequency_ms": 500,
                "highlight_changes": True,
                "show_confidence": True
            }
        }
        
        return self.create_hud_element(
            element_id=hud_id,
            element_type="emotion_panel",
            content=content,
            position=position,
            size=size,
            opacity=0.85,
            anchor="top_right"
        )
    
    def update_emotion_hud(self, 
                         emotion_data: Dict) -> Dict:
        """
        Update the emotion HUD with new emotion analysis data.
        
        Args:
            emotion_data: Dictionary containing emotion analysis results
        """
        if not self.ar_vr_active or not self.accessibility_features["emotion_detection"]:
            return {"status": "error", "message": "Emotion detection not enabled"}
            
        hud_id = "emotion_hud"
        
        if hud_id not in self.hud_elements:
            return {"status": "error", "message": "Emotion HUD not created"}
            
        updates = {
            "content": {
                "sections": [
                    {
                        "title": "Detected Emotions",
                        "type": "emotion_list",
                        "entries": emotion_data.get("emotions", [])
                    },
                    {
                        "title": "Primary Emotion",
                        "type": "emotion_gauge",
                        "emotion": emotion_data.get("primary_emotion", {}).get("name"),
                        "intensity": emotion_data.get("primary_emotion", {}).get("intensity", 0.0)
                    },
                    {
                        "title": "Social Context",
                        "type": "text_display",
                        "text": emotion_data.get("social_context", "No social context analyzed")
                    }
                ]
            }
        }
        
        return self.update_hud_element(hud_id, updates)
    
    def create_social_cue_hud(self,
                            position: Tuple[float, float] = (0.9, 0.7),
                            size: Tuple[float, float] = (0.25, 0.25),
                            detail_level: str = "medium") -> Dict:
        """
        Create a dedicated HUD for social cue analysis.
        
        Args:
            position: Normalized position in view (0,0 is center)
            size: Normalized size (1.0 is full view)
            detail_level: Detail level ("basic", "medium", "detailed")
        """
        if not self.ar_vr_active or not self.accessibility_features["social_cue_analysis"]:
            return {"status": "error", "message": "Social cue analysis not enabled"}
            
        hud_id = "social_cue_hud"
        
        # First check if the HUD already exists
        if hud_id in self.hud_elements:
            return {"status": "exists", "message": "Social cue HUD already exists"}
            
        # Create social cue HUD container
        content = {
            "detail_level": detail_level,
            "sections": [
                {
                    "title": "Group Dynamics",
                    "type": "text_display",
                    "text": "Analyzing group dynamics..."
                },
                {
                    "title": "Conversation Tone",
                    "type": "gauge",
                    "value": 0.5,
                    "min_label": "Formal",
                    "max_label": "Casual"
                },
                {
                    "title": "Key Signals",
                    "type": "bullet_list",
                    "items": []
                }
            ],
            "settings": {
                "update_frequency_ms": 1000,
                "display_mode": "tooltip",
                "color_code": True
            }
        }
        
        return self.create_hud_element(
            element_id=hud_id,
            element_type="social_panel",
            content=content,
            position=position,
            size=size,
            opacity=0.8,
            anchor="bottom_right"
        )
    
    def update_social_cue_hud(self, 
                            social_data: Dict) -> Dict:
        """
        Update the social cue HUD with new social analysis data.
        
        Args:
            social_data: Dictionary containing social cue analysis results
        """
        if not self.ar_vr_active or not self.accessibility_features["social_cue_analysis"]:
            return {"status": "error", "message": "Social cue analysis not enabled"}
            
        hud_id = "social_cue_hud"
        
        if hud_id not in self.hud_elements:
            return {"status": "error", "message": "Social cue HUD not created"}
            
        updates = {
            "content": {
                "sections": [
                    {
                        "title": "Group Dynamics",
                        "type": "text_display",
                        "text": social_data.get("group_dynamics", "No group detected")
                    },
                    {
                        "title": "Conversation Tone",
                        "type": "gauge",
                        "value": social_data.get("conversation_tone", 0.5),
                        "min_label": "Formal",
                        "max_label": "Casual"
                    },
                    {
                        "title": "Key Signals",
                        "type": "bullet_list",
                        "items": social_data.get("key_signals", [])
                    }
                ]
            }
        }
        
        return self.update_hud_element(hud_id, updates)
    
    def create_ocr_hud(self,
                     position: Tuple[float, float] = (-0.9, 0.0),
                     size: Tuple[float, float] = (0.2, 0.7),
                     auto_translate: bool = False) -> Dict:
        """
        Create a dedicated HUD for OCR text extraction display.
        
        Args:
            position: Normalized position in view (0,0 is center)
            size: Normalized size (1.0 is full view)
            auto_translate: Whether to automatically translate detected text
        """
        if not self.ar_vr_active or not self.accessibility_features["ocr"]:
            return {"status": "error", "message": "OCR not enabled"}
            
        hud_id = "ocr_hud"
        
        # First check if the HUD already exists
        if hud_id in self.hud_elements:
            return {"status": "exists", "message": "OCR HUD already exists"}
            
        # Create OCR HUD container
        content = {
            "auto_translate": auto_translate,
            "sections": [
                {
                    "title": "Detected Text",
                    "type": "scrolling_text",
                    "text": "No text detected yet",
                    "max_lines": 10
                },
                {
                    "title": "Translation",
                    "type": "text_display",
                    "text": "No translation available",
                    "visible": auto_translate
                },
                {
                    "title": "Actions",
                    "type": "button_group",
                    "buttons": [
                        {"label": "Copy All", "action": "copy_text"},
                        {"label": "Translate", "action": "translate_text"},
                        {"label": "Clear", "action": "clear_text"}
                    ]
                }
            ],
            "settings": {
                "highlight_text_in_view": True,
                "text_grouping": "paragraph",
                "sort_by_relevance": True
            }
        }
        
        return self.create_hud_element(
            element_id=hud_id,
            element_type="ocr_panel",
            content=content,
            position=position,
            size=size,
            opacity=0.9,
            anchor="left"
        )
    
    def update_ocr_hud(self, 
                     ocr_data: Dict) -> Dict:
        """
        Update the OCR HUD with new text extraction data.
        
        Args:
            ocr_data: Dictionary containing OCR analysis results
        """
        if not self.ar_vr_active or not self.accessibility_features["ocr"]:
            return {"status": "error", "message": "OCR not enabled"}
            
        hud_id = "ocr_hud"
        
        if hud_id not in self.hud_elements:
            return {"status": "error", "message": "OCR HUD not created"}
            
        translation = ocr_data.get("translation", {})
        has_translation = bool(translation.get("text"))
        
        updates = {
            "content": {
                "sections": [
                    {
                        "title": "Detected Text",
                        "type": "scrolling_text",
                        "text": ocr_data.get("text", "No text detected"),
                        "regions": ocr_data.get("text_regions", [])
                    },
                    {
                        "title": "Translation",
                        "type": "text_display",
                        "text": translation.get("text", "No translation available"),
                        "source_lang": translation.get("source_lang"),
                        "target_lang": translation.get("target_lang"),
                        "visible": has_translation
                    }
                ]
            }
        }
        
        return self.update_hud_element(hud_id, updates)
    
    def create_qr_hud(self,
                    position: Tuple[float, float] = (-0.9, -0.7),
                    size: Tuple[float, float] = (0.2, 0.2),
                    auto_action: bool = False) -> Dict:
        """
        Create a dedicated HUD for QR code reading.
        
        Args:
            position: Normalized position in view (0,0 is center)
            size: Normalized size (1.0 is full view)
            auto_action: Whether to automatically perform actions for known QR types
        """
        if not self.ar_vr_active or not self.accessibility_features["qr_reader"]:
            return {"status": "error", "message": "QR reader not enabled"}
            
        hud_id = "qr_hud"
        
        # First check if the HUD already exists
        if hud_id in self.hud_elements:
            return {"status": "exists", "message": "QR HUD already exists"}
            
        # Create QR HUD container
        content = {
            "auto_action": auto_action,
            "sections": [
                {
                    "title": "Detected Code",
                    "type": "code_display",
                    "code_type": "None",
                    "code_value": "No code detected"
                },
                {
                    "title": "Actions",
                    "type": "button_group",
                    "buttons": [
                        {"label": "Open URL", "action": "open_url", "enabled": False},
                        {"label": "Copy", "action": "copy_value", "enabled": False},
                        {"label": "Scan", "action": "manual_scan", "enabled": True}
                    ]
                }
            ],
            "settings": {
                "highlight_codes": True,
                "scan_sound": True,
                "vibration_feedback": True
            }
        }
        
        return self.create_hud_element(
            element_id=hud_id,
            element_type="qr_panel",
            content=content,
            position=position,
            size=size,
            opacity=0.9,
            anchor="bottom_left"
        )
    
    def update_qr_hud(self, 
                    qr_data: Dict) -> Dict:
        """
        Update the QR HUD with new QR code detection data.
        
        Args:
            qr_data: Dictionary containing QR code analysis results
        """
        if not self.ar_vr_active or not self.accessibility_features["qr_reader"]:
            return {"status": "error", "message": "QR reader not enabled"}
            
        hud_id = "qr_hud"
        
        if hud_id not in self.hud_elements:
            return {"status": "error", "message": "QR HUD not created"}
            
        code_type = qr_data.get("type", "None")
        code_value = qr_data.get("value", "No code detected")
        is_url = code_value.startswith("http")
        
        updates = {
            "content": {
                "sections": [
                    {
                        "title": "Detected Code",
                        "type": "code_display",
                        "code_type": code_type,
                        "code_value": code_value,
                        "timestamp": qr_data.get("timestamp")
                    },
                    {
                        "title": "Actions",
                        "type": "button_group",
                        "buttons": [
                            {"label": "Open URL", "action": "open_url", "enabled": is_url},
                            {"label": "Copy", "action": "copy_value", "enabled": bool(code_value)},
                            {"label": "Scan", "action": "manual_scan", "enabled": True}
                        ]
                    }
                ]
            }
        }
        
        return self.update_hud_element(hud_id, updates)
    
    # Combined Accessibility Helper Methods
    
    def initialize_accessibility_suite(self,
                                     features: List[str] = None,
                                     hud_style: str = "minimal") -> Dict:
        """
        Initialize all accessibility features at once.
        
        Args:
            features: List of features to enable ["emotion", "social", "ocr", "qr", "object"]
            hud_style: Visual style for all HUDs ("minimal", "detailed", "integrated")
        """
        if not self.ar_vr_active:
            self.initialize_ar_vr()
            
        if features is None:
            features = ["emotion", "social", "ocr", "qr", "object"]
            
        results = {}
        
        # Initialize visual analysis first
        visual_features = []
        if "emotion" in features or "social" in features:
            visual_features.extend(["face"])
        if "ocr" in features:
            visual_features.extend(["ocr"])
        if "qr" in features:
            visual_features.extend(["qr_code"])
        if "object" in features:
            visual_features.extend(["object_detection"])
            
        vis_result = self.initialize_visual_analysis(visual_features)
        results["visual_analysis"] = vis_result
        
        # Enable individual features
        if "emotion" in features:
            results["emotion"] = self.enable_emotion_detection(display_mode=hud_style)
            results["emotion_hud"] = self.create_emotion_hud(style=hud_style)
            
        if "social" in features:
            results["social"] = self.enable_social_cue_analysis(display_mode=hud_style)
            results["social_hud"] = self.create_social_cue_hud(detail_level=hud_style)
            
        if "ocr" in features:
            results["ocr"] = self.enable_ocr(display_mode=hud_style)
            results["ocr_hud"] = self.create_ocr_hud()
            
        if "qr" in features:
            results["qr"] = self.enable_qr_reader()
            results["qr_hud"] = self.create_qr_hud()
            
        if "object" in features:
            results["object"] = self.enable_object_recognition()
            
        return {
            "status": "initialized",
            "enabled_features": [f for f in features if results.get(f, {}).get("status") == "success"],
            "results": results
        }
    
    def disable_accessibility_suite(self) -> Dict:
        """
        Disable all accessibility features at once.
        """
        results = {}
        
        for feature, enabled in self.accessibility_features.items():
            if enabled:
                if feature == "emotion_detection":
                    results[feature] = self.disable_emotion_detection()
                elif feature == "social_cue_analysis":
                    results[feature] = self.disable_social_cue_analysis()
                elif feature == "ocr":
                    results[feature] = self.disable_ocr()
                elif feature == "qr_reader":
                    results[feature] = self.disable_qr_reader()
                elif feature == "object_recognition":
                    results[feature] = self.disable_object_recognition()
        
        # Clean up HUDs
        hud_ids = ["emotion_hud", "social_cue_hud", "ocr_hud", "qr_hud"]
        for hud_id in hud_ids:
            if hud_id in self.hud_elements:
                results[f"{hud_id}_removal"] = self.delete_hud_element(hud_id)
        
        return {
            "status": "disabled",
            "results": results
        }
    
    def toggle_accessibility_feature(self, 
                                   feature: str,
                                   enabled: bool = None) -> Dict:
        """
        Toggle a specific accessibility feature on or off.
        
        Args:
            feature: Feature to toggle ("emotion", "social", "ocr", "qr", "object")
            enabled: Explicitly set enabled state (or toggle if None)
        """
        feature_map = {
            "emotion": "emotion_detection",
            "social": "social_cue_analysis",
            "ocr": "ocr",
            "qr": "qr_reader",
            "object": "object_recognition"
        }
        
        if feature not in feature_map:
            return {"status": "error", "message": f"Unknown feature: {feature}"}
            
        internal_feature = feature_map[feature]
        current_state = self.accessibility_features[internal_feature]
        
        # Determine target state
        if enabled is None:
            target_state = not current_state
        else:
            target_state = enabled
            
        # If no change needed
        if current_state == target_state:
            return {"status": "unchanged", "feature": feature, "enabled": target_state}
            
        # Enable or disable feature
        if target_state:
            if feature == "emotion":
                result = self.enable_emotion_detection()
                if result.get("status") == "success":
                    self.create_emotion_hud()
            elif feature == "social":
                result = self.enable_social_cue_analysis()
                if result.get("status") == "success":
                    self.create_social_cue_hud()
            elif feature == "ocr":
                result = self.enable_ocr()
                if result.get("status") == "success":
                    self.create_ocr_hud()
            elif feature == "qr":
                result = self.enable_qr_reader()
                if result.get("status") == "success":
                    self.create_qr_hud()
            elif feature == "object":
                result = self.enable_object_recognition()
        else:
            if feature == "emotion":
                result = self.disable_emotion_detection()
                if "emotion_hud" in self.hud_elements:
                    self.delete_hud_element("emotion_hud")
            elif feature == "social":
                result = self.disable_social_cue_analysis()
                if "social_cue_hud" in self.hud_elements:
                    self.delete_hud_element("social_cue_hud")
            elif feature == "ocr":
                result = self.disable_ocr()
                if "ocr_hud" in self.hud_elements:
                    self.delete_hud_element("ocr_hud")
            elif feature == "qr":
                result = self.disable_qr_reader()
                if "qr_hud" in self.hud_elements:
                    self.delete_hud_element("qr_hud")
            elif feature == "object":
                result = self.disable_object_recognition()
                
        return {
            "status": "toggled",
            "feature": feature,
            "enabled": target_state,
            "result": result
        }
    
    def get_accessibility_status(self) -> Dict:
        """
        Get the current status of all accessibility features.
        """
        hud_status = {
            "emotion_hud": "emotion_hud" in self.hud_elements,
            "social_cue_hud": "social_cue_hud" in self.hud_elements,
            "ocr_hud": "ocr_hud" in self.hud_elements,
            "qr_hud": "qr_hud" in self.hud_elements
        }
        
        return {
            "features_enabled": self.accessibility_features,
            "huds_active": hud_status,
            "visual_analysis_active": self.visual_analysis_active,
            "ar_vr_active": self.ar_vr_active
        }

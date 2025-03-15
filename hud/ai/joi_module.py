"""
joi_module.py

Implementation of Jerk-Off Instructions (JOI) functionality with 
timing control, intensity adjustment, and safety features.

This module provides guided masturbation sessions with configurable
settings, adaptive intensity, and consent verification.
"""

import os
import json
import time
import logging
import datetime
import random
import threading
import re
from threading import Lock

# Setup logging
logger = logging.getLogger("JOIModule")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class JOIModule:
    def __init__(self, safety_manager=None):
        """
        Initialize JOI Module with safety controls
        
        Args:
            safety_manager: Optional safety manager that handles consent and verification
        """
        self.safety_manager = safety_manager
        self.user_preferences = {}
        self.active_sessions = {}
        self.session_timers = {}
        self.session_threads = {}
        self.template_sessions = {}
        self.safe_words = {}
        self.lock = Lock()
        
        # Load template sessions
        self._load_templates()
    
    def _load_templates(self):
        """Load JOI template sessions from files"""
        try:
            # Create templates directory if it doesn't exist
            os.makedirs('templates', exist_ok=True)
            
            # Load JOI templates if available
            joi_path = 'templates/joi_templates.json'
            if os.path.exists(joi_path):
                with open(joi_path, 'r') as f:
                    self.template_sessions = json.load(f)
            else:
                # Default JOI templates
                self.template_sessions = {
                    "beginner_session": {
                        "name": "Beginner Session",
                        "description": "A gentle, guided session for beginners",
                        "duration_minutes": 10,
                        "intensity": "low",
                        "instruction_sets": [
                            {
                                "phase": "warm_up",
                                "duration_seconds": 120,
                                "instructions": [
                                    "Start by getting comfortable and relaxed",
                                    "Begin with gentle touches to build arousal",
                                    "Focus on your breathing as you start to touch yourself",
                                    "Establish a slow, steady rhythm"
                                ]
                            },
                            {
                                "phase": "build_up",
                                "duration_seconds": 240,
                                "instructions": [
                                    "Gradually increase your pace",
                                    "Pay attention to what feels best",
                                    "Slow down if you get too close",
                                    "Focus on the sensations you're experiencing"
                                ]
                            },
                            {
                                "phase": "plateau",
                                "duration_seconds": 120,
                                "instructions": [
                                    "Maintain a steady pace",
                                    "Focus on your breathing",
                                    "Enjoy the moment without rushing",
                                    "Savor the sensations"
                                ]
                            },
                            {
                                "phase": "peak",
                                "duration_seconds": 90,
                                "instructions": [
                                    "Start to increase your pace",
                                    "Let yourself get closer to the edge",
                                    "Focus on the building pleasure",
                                    "You're getting closer to climax"
                                ]
                            },
                            {
                                "phase": "climax",
                                "duration_seconds": 30,
                                "instructions": [
                                    "Find your perfect rhythm now",
                                    "Let yourself go completely",
                                    "Give in to the sensations",
                                    "Let yourself finish when you're ready"
                                ]
                            }
                        ],
                        "encouragements": [
                            "You're doing great",
                            "That's perfect",
                            "Just like that",
                            "You're doing so well",
                            "Keep going just like that"
                        ]
                    },
                    "edging_session": {
                        "name": "Edging Session",
                        "description": "A session focused on building arousal through edging",
                        "duration_minutes": 15,
                        "intensity": "medium",
                        "instruction_sets": [
                            {
                                "phase": "warm_up",
                                "duration_seconds": 120,
                                "instructions": [
                                    "Start slowly and build arousal gradually",
                                    "Focus on gentle touches and building sensation",
                                    "Take your time getting fully aroused",
                                    "Establish a comfortable rhythm"
                                ]
                            },
                            {
                                "phase": "edge_1",
                                "duration_seconds": 180,
                                "instructions": [
                                    "Begin to increase your pace",
                                    "Get yourself close to the edge",
                                    "When you're nearly there, STOP completely",
                                    "Hold still and feel the sensations recede"
                                ]
                            },
                            {
                                "phase": "recovery_1",
                                "duration_seconds": 60,
                                "instructions": [
                                    "Gentle touches only",
                                    "Let your arousal subside slightly",
                                    "Focus on your breathing",
                                    "Prepare for the next build-up"
                                ]
                            },
                            {
                                "phase": "edge_2",
                                "duration_seconds": 180,
                                "instructions": [
                                    "Start building up again, a bit faster this time",
                                    "Push yourself to the edge again",
                                    "Get as close as you can without going over",
                                    "STOP again when you're right on the edge"
                                ]
                            },
                            {
                                "phase": "recovery_2",
                                "duration_seconds": 60,
                                "instructions": [
                                    "Hands off completely this time",
                                    "Take deep breaths",
                                    "Feel the intense arousal without touching",
                                    "Notice how sensitive you've become"
                                ]
                            },
                            {
                                "phase": "final_edge",
                                "duration_seconds": 180,
                                "instructions": [
                                    "Begin again, building to the final edge",
                                    "Push yourself to the limit one more time",
                                    "This time, hold right at the edge as long as you can",
                                    "Stay right on the brink of climax"
                                ]
                            },
                            {
                                "phase": "climax",
                                "duration_seconds": 120,
                                "instructions": [
                                    "Now give yourself permission to finish",
                                    "Find your perfect rhythm",
                                    "Let yourself go completely",
                                    "Enjoy your well-earned release"
                                ]
                            }
                        ],
                        "encouragements": [
                            "Perfect control",
                            "You're doing amazingly",
                            "That's exactly right",
                            "Feel how intense it's getting",
                            "You're mastering the edge"
                        ]
                    },
                    "intense_session": {
                        "name": "Intense Session",
                        "description": "An intense, faster-paced session",
                        "duration_minutes": 8,
                        "intensity": "high",
                        "instruction_sets": [
                            {
                                "phase": "warm_up",
                                "duration_seconds": 60,
                                "instructions": [
                                    "Start immediately with a medium pace",
                                    "Build arousal quickly",
                                    "Get yourself excited right from the start",
                                    "Establish a brisk rhythm"
                                ]
                            },
                            {
                                "phase": "build_up",
                                "duration_seconds": 120,
                                "instructions": [
                                    "Increase your pace substantially",
                                    "Push your arousal higher and higher",
                                    "Feel the intensity building rapidly",
                                    "Keep pushing your limits"
                                ]
                            },
                            {
                                "phase": "peak_1",
                                "duration_seconds": 60,
                                "instructions": [
                                    "Maximum pace now",
                                    "Push yourself to the edge",
                                    "But don't finish yet",
                                    "Hold back at the last moment"
                                ]
                            },
                            {
                                "phase": "brief_rest",
                                "duration_seconds": 30,
                                "instructions": [
                                    "Brief pause",
                                    "Just a moment to catch your breath",
                                    "But keep yourself ready",
                                    "The pause makes what follows more intense"
                                ]
                            },
                            {
                                "phase": "final_push",
                                "duration_seconds": 90,
                                "instructions": [
                                    "Now go for it at full intensity",
                                    "Give it everything you've got",
                                    "Push yourself past your usual limits",
                                    "Build to an explosive finish"
                                ]
                            },
                            {
                                "phase": "climax",
                                "duration_seconds": 120,
                                "instructions": [
                                    "Now let yourself finish",
                                    "Release all control",
                                    "Experience maximum pleasure",
                                    "Enjoy the intense sensation"
                                ]
                            }
                        ],
                        "encouragements": [
                            "Don't hold back",
                            "Push harder",
                            "That's incredibly intense",
                            "Feel the power building",
                            "You can take even more"
                        ]
                    }
                }
                
                # Save default templates for future use
                with open(joi_path, 'w') as f:
                    json.dump(self.template_sessions, f, indent=2)
            
            logger.info(f"Loaded {len(self.template_sessions)} JOI templates")
            return True
        except Exception as e:
            logger.error(f"Error loading JOI templates: {str(e)}")
            return False
    
    def get_available_sessions(self):
        """Get list of available JOI templates"""
        return {id: {
            "name": session["name"],
            "description": session["description"],
            "duration_minutes": session["duration_minutes"],
            "intensity": session["intensity"]
        } for id, session in self.template_sessions.items()}
    
    def set_user_preferences(self, user_id, preferences, require_consent=True):
        """
        Set user preferences for JOI sessions
        
        Args:
            user_id: User identifier
            preferences: Dict containing user preferences
            require_consent: Whether to require consent
            
        Returns:
            Dict with status information
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "joi"):
                return {
                    "status": "error",
                    "message": "Consent required for JOI features",
                    "requires_consent": True
                }
            
            if not self.safety_manager.verify_age(user_id):
                return {
                    "status": "error", 
                    "message": "Age verification required",
                    "requires_verification": True
                }
        
        with self.lock:
            # Initialize user preferences if they don't exist
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            
            # Update preferences
            for key, value in preferences.items():
                self.user_preferences[user_id][key] = value
            
            # Set safe word if provided
            if "safe_word" in preferences:
                self.safe_words[user_id] = preferences["safe_word"]
            
            logger.info(f"Updated JOI preferences for user {user_id}")
            
            return {
                "status": "success",
                "message": "Preferences updated successfully",
                "preferences": self.user_preferences[user_id]
            }
    
    def get_user_preferences(self, user_id, require_consent=True):
        """
        Get user preferences for JOI sessions
        
        Args:
            user_id: User identifier
            require_consent: Whether to require consent
            
        Returns:
            Dict with user preferences
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "joi"):
                return {
                    "status": "error",
                    "message": "Consent required for JOI features",
                    "requires_consent": True
                }
        
        with self.lock:
            if user_id in self.user_preferences:
                return {
                    "status": "success",
                    "preferences": self.user_preferences[user_id]
                }
            else:
                return {
                    "status": "success",
                    "preferences": {}
                }
    
    def set_safe_word(self, user_id, safe_word):
        """
        Set safe word for immediately stopping JOI session
        
        Args:
            user_id: User identifier
            safe_word: Safe word for stopping session
            
        Returns:
            Dict with status information
        """
        with self.lock:
            self.safe_words[user_id] = safe_word
            
            logger.info(f"Set JOI safe word for user {user_id}")
            
            return {
                "status": "success",
                "message": f"Safe word set successfully: '{safe_word}'",
                "safe_word": safe_word
            }
    
    def start_session(self, user_id, template_id=None, custom_settings=None, require_consent=True):
        """
        Start a JOI session
        
        Args:
            user_id: User identifier
            template_id: Optional ID of predefined session template
            custom_settings: Optional custom session settings
            require_consent: Whether to require consent
            
        Returns:
            Dict with session information
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "joi"):
                return {
                    "status": "error",
                    "message": "Consent required for JOI features",
                    "requires_consent": True
                }
            
            if not self.safety_manager.verify_age(user_id):
                return {
                    "status": "error", 
                    "message": "Age verification required",
                    "requires_verification": True
                }
        
        with self.lock:
            try:
                # Check if user already has an active session
                for session_id, session in self.active_sessions.items():
                    if session["user_id"] == user_id and not session.get("completed", False):
                        return {
                            "status": "error",
                            "message": "User already has an active session",
                            "existing_session_id": session_id
                        }
                
                # Generate session ID
                session_id = f"joi_{user_id}_{int(time.time())}"
                
                # Select session template
                session_template = None
                if template_id and template_id in self.template_sessions:
                    session_template = self.template_sessions[template_id]
                elif custom_settings:
                    # Create custom session
                    session_template = {
                        "name": custom_settings.get("name", "Custom Session"),
                        "description": custom_settings.get("description", "Custom JOI session"),
                        "duration_minutes": custom_settings.get("duration_minutes", 10),
                        "intensity": custom_settings.get("intensity", "medium"),
                        "instruction_sets": custom_settings.get("instruction_sets", [])
                    }
                else:
                    # Select random template
                    template_id = random.choice(list(self.template_sessions.keys()))
                    session_template = self.template_sessions[template_id]
                
                # Apply user preferences if available
                if user_id in self.user_preferences:
                    user_prefs = self.user_preferences[user_id]
                    
                    # Modify session based on preferences
                    if "preferred_intensity" in user_prefs:
                        session_template["intensity"] = user_prefs["preferred_intensity"]
                    
                    if "preferred_duration" in user_prefs:
                        # Adjust duration based on user preference
                        original_duration = session_template["duration_minutes"]
                        preferred_duration = user_prefs["preferred_duration"]
                        
                        if preferred_duration != original_duration:
                            # Scale instruction durations proportionally
                            scale_factor = preferred_duration / original_duration
                            for instruction_set in session_template["instruction_sets"]:
                                instruction_set["duration_seconds"] = int(instruction_set["duration_seconds"] * scale_factor)
                            
                            session_template["duration_minutes"] = preferred_duration
                
                # Initialize session
                now = time.time()
                
                session = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "template_id": template_id,
                    "name": session_template["name"],
                    "description": session_template["description"],
                    "intensity": session_template["intensity"],
                    "duration_minutes": session_template["duration_minutes"],
                    "instruction_sets": session_template["instruction_sets"],
                    "encouragements": session_template.get("encouragements", []),
                    "start_time": now,
                    "end_time": now + (session_template["duration_minutes"] * 60),
                    "current_phase": 0,
                    "current_instruction": 0,
                    "completed": False,
                    "paused": False,
                    "safe_word_used": False,
                    "instructions_given": []
                }
                
                # Calculate overall session timing
                total_seconds = 0
                for instruction_set in session["instruction_sets"]:
                    total_seconds += instruction_set["duration_seconds"]
                
                # Adjust if total doesn't match expected duration
                expected_seconds = session["duration_minutes"] * 60
                if total_seconds != expected_seconds:
                    # Scale instruction durations proportionally
                    scale_factor = expected_seconds / max(1, total_seconds)
                    for instruction_set in session["instruction_sets"]:
                        instruction_set["duration_seconds"] = int(instruction_set["duration_seconds"] * scale_factor)
                
                # Add session to active sessions
                self.active_sessions[session_id] = session
                
                # Start session timer
                self._start_session_timer(session_id)
                
                # Get initial instruction
                initial_instruction = self._get_next_instruction(session)
                
                logger.info(f"Started JOI session {session_id} for user {user_id}")
                
                return {
                    "status": "success",
                    "session_id": session_id,
                    "name": session["name"],
                    "description": session["description"],
                    "duration_minutes": session["duration_minutes"],
                    "intensity": session["intensity"],
                    "initial_instruction": initial_instruction,
                    "current_phase": session["instruction_sets"][0]["phase"],
                    "safe_word": self.safe_words.get(user_id, None)
                }
            except Exception as e:
                logger.error(f"Error starting JOI session: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to start JOI session: {str(e)}"
                }
    
    def _start_session_timer(self, session_id):
        """Start a timer thread for the JOI session"""
        try:
            # Create a new thread for this session
            session_thread = threading.Thread(
                target=self._session_timer_thread,
                args=(session_id,),
                daemon=True
            )
            
            # Store the thread
            self.session_threads[session_id] = session_thread
            
            # Start the thread
            session_thread.start()
            
            logger.info(f"Started timer thread for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error starting session timer: {str(e)}")
            return False
    
    def _session_timer_thread(self, session_id):
        """Thread function for managing JOI session timing"""
        try:
            while True:
                # Check if session still exists
                with self.lock:
                    if session_id not in self.active_sessions:
                        logger.info(f"Session {session_id} no longer exists, ending timer thread")
                        break
                    
                    session = self.active_sessions[session_id]
                    
                    # Check if session is completed
                    if session.get("completed", False):
                        logger.info(f"Session {session_id} is completed, ending timer thread")
                        break
                    
                    # Check if session is paused
                    if session.get("paused", False):
                        # Sleep briefly and continue
                        time.sleep(1)
                        continue
                    
                    # Check if current instruction needs to be updated
                    current_time = time.time()
                    
                    # Calculate time elapsed in current phase
                    current_phase = session["current_phase"]
                    phase_start_time = session.get("phase_start_time", session["start_time"])
                    phase_elapsed = current_time - phase_start_time
                    
                    # Get current phase duration
                    if current_phase < len(session["instruction_sets"]):
                        phase_duration = session["instruction_sets"][current_phase]["duration_seconds"]
                        
                        # Check if phase is complete
                        if phase_elapsed >= phase_duration:
                            # Move to next phase
                            session["current_phase"] = current_phase + 1
                            session["current_instruction"] = 0
                            session["phase_start_time"] = current_time
                            
                            # If that was the last phase, mark session as completed
                            if session["current_phase"] >= len(session["instruction_sets"]):
                                session["completed"] = True
                                logger.info(f"Session {session_id} completed all phases")
                                break
                    
                    # Check if it's time for a new instruction within current phase
                    current_instruction = session["current_instruction"]
                    instruction_interval = phase_duration / max(1, len(session["instruction_sets"][current_phase]["instructions"]))
                    
                    if phase_elapsed >= (current_instruction + 1) * instruction_interval:
                        # Move to next instruction
                        session["current_instruction"] = current_instruction + 1
                    
                # Sleep briefly before checking again
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error in session timer thread: {str(e)}")
    
    def get_next_instruction(self, session_id, user_id, message=None):
        """
        Get the next instruction in a JOI session
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            message: Optional user message to check for safe word
            
        Returns:
            Dict with instruction information
        """
        with self.lock:
            # Check if session exists
            if session_id not in self.active_sessions:
                return {
                    "status": "error",
                    "message": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Check if session belongs to user
            if session["user_id"] != user_id:
                return {
                    "status": "error",
                    "message": "Unauthorized access to session"
                }
            
            # Check if session is completed
            if session.get("completed", False):
                return {
                    "status": "completed",
                    "message": "Session is already completed"
                }
            
            # Check for safe word in message
            if message and user_id in self.safe_words:
                safe_word = self.safe_words[user_id]
                if safe_word and safe_word.lower() in message.lower():
                    session["safe_word_used"] = True
                    session["completed"] = True
                    
                    logger.info(f"Safe word used in JOI session {session_id} by user {user_id}")
                    
                    return {
                        "status": "safe_word",
                        "message": "Safe word detected. Session ended.",
                        "session_ended": True
                    }
            
            # Check if session was previously ended with safe word
            if session.get("safe_word_used", False):
                return {
                    "status": "error",
                    "message": "Session was ended with safe word. Please start a new session."
                }
            
            # Get next instruction
            instruction = self._get_next_instruction(session)
            
            # Add to instructions given
            session["instructions_given"].append({
                "instruction": instruction,
                "timestamp": time.time()
            })
            
            return {
                "status": "success",
                "instruction": instruction,
                "current_phase": session["instruction_sets"][session["current_phase"]]["phase"],
                "phase_progress": self._get_phase_progress(session),
                "session_progress": self._get_session_progress(session)
            }
    
    def _get_next_instruction(self, session):
        """Get the next instruction for the session"""
        try:
            current_phase = session["current_phase"]
            current_instruction = session["current_instruction"]
            
            # Check if we're still within valid phases
            if current_phase >= len(session["instruction_sets"]):
                session["completed"] = True
                return "Session complete. Thank you for participating."
            
            # Get instructions for current phase
            phase_instructions = session["instruction_sets"][current_phase]["instructions"]
            
            # Check if we're still within valid instructions
            if current_instruction >= len(phase_instructions):
                # Use the last instruction or fall back to encouragement
                if phase_instructions:
                    instruction = phase_instructions[-1]
                elif session["encouragements"]:
                    instruction = random.choice(session["encouragements"])
                else:
                    instruction = "Continue at your own pace."
            else:
                instruction = phase_instructions[current_instruction]
            
            # Sometimes add encouragement
            if session["encouragements"] and random.random() < 0.3:
                encouragement = random.choice(session["encouragements"])
                instruction = f"{instruction}. {encouragement}."
            
            # Add intensity modifiers based on phase and session intensity
            instruction = self._add_intensity_modifiers(instruction, session)
            
            return instruction
        except Exception as e:
            logger.error(f"Error getting next instruction: {str(e)}")
            return "Continue at your own pace."
    
    def _add_intensity_modifiers(self, instruction, session):
        """Add intensity modifiers to instruction based on session settings"""
        intensity = session["intensity"]
        current_phase = session["current_phase"]
        total_phases = len(session["instruction_sets"])
        
        # Determine where we are in the session
        progress = current_phase / max(1, total_phases - 1)
        
        # Intensity modifiers
        if intensity == "low":
            modifiers = ["gently", "slowly", "softly", "lightly", "tenderly"]
            if progress > 0.8:  # Near the end
                modifiers = ["steadily", "rhythmically", "consistently"]
        elif intensity == "high":
            modifiers = ["intensely", "firmly", "strongly", "vigorously", "powerfully"]
            if progress > 0.7:  # Near the end
                modifiers = ["rapidly", "fervently", "passionately", "urgently"]
        else:  # Medium intensity
            modifiers = ["steadily", "moderately", "rhythmically", "evenly"]
            if progress > 0.7:  # Near the end
                modifiers = ["firmly", "eagerly", "enthusiastically"]
        
        # Randomly decide whether to add a modifier
        if random.random() < 0.3:
            modifier = random.choice(modifiers)
            
            # Check if instruction already contains the modifier
            if modifier not in instruction.lower():
                # Add modifier appropriately based on instruction content
                if "pace" in instruction.lower():
                    instruction = instruction.replace("pace", f"{modifier} pace")
                elif any(term in instruction.lower() for term in ["continue", "keep", "maintain", "start"]):
                    # Find the term and add modifier after it
                    for term in ["continue", "keep", "maintain", "start"]:
                        if term in instruction.lower():
                            pattern = re.compile(re.escape(term), re.IGNORECASE)
                            instruction = pattern.sub(f"{term} {modifier}", instruction, 1)
                            break
                else:
                    # Just append modifier to end
                    instruction = f"{instruction} {modifier}"
        
        return instruction
    
    def _get_phase_progress(self, session):
        """Get the progress percentage within the current phase"""
        current_phase = session["current_phase"]
        
        if current_phase >= len(session["instruction_sets"]):
            return 100.0
        
        current_time = time.time()
        phase_start_time = session.get("phase_start_time", session["start_time"])
        phase_duration = session["instruction_sets"][current_phase]["duration_seconds"]
        
        elapsed = current_time - phase_start_time
        progress = (elapsed / max(1, phase_duration)) * 100
        
        return min(100.0, max(0.0, progress))
    
    def _get_session_progress(self, session):
        """Get the overall session progress percentage"""
        start_time = session["start_time"]
        end_time = session["end_time"]
        current_time = time.time()
        
        progress = ((current_time - start_time) / max(1, end_time - start_time)) * 100
        
        return min(100.0, max(0.0, progress))
    
    def pause_session(self, session_id, user_id):
        """
        Pause a JOI session
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Dict with status information
        """
        with self.lock:
            # Check if session exists
            if session_id not in self.active_sessions:
                return {
                    "status": "error",
                    "message": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Check if session belongs to user
            if session["user_id"] != user_id:
                return {
                    "status": "error",
                    "message": "Unauthorized access to session"
                }
            
            # Check if session is already paused
            if session.get("paused", False):
                return {
                    "status": "error",
                    "message": "Session is already paused"
                }
            
            # Pause session
            session["paused"] = True
            session["pause_time"] = time.time()
            
            logger.info(f"Paused JOI session {session_id} for user {user_id}")
            
            return {
                "status": "success",
                "message": "Session paused",
                "session_id": session_id,
                "pause_time": session["pause_time"]
            }
    
    def resume_session(self, session_id, user_id):
        """
        Resume a paused JOI session
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Dict with status information
        """
        with self.lock:
            # Check if session exists
            if session_id not in self.active_sessions:
                return {
                    "status": "error",
                    "message": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Check if session belongs to user
            if session["user_id"] != user_id:
                return {
                    "status": "error",
                    "message": "Unauthorized access to session"
                }
            
            # Check if session is paused
            if not session.get("paused", False):
                return {
                    "status": "error",
                    "message": "Session is not paused"
                }
            
            # Calculate pause duration
            pause_duration = time.time() - session.get("pause_time", time.time())
            
            # Adjust timing
            session["start_time"] += pause_duration
            session["end_time"] += pause_duration
            if "phase_start_time" in session:
                session["phase_start_time"] += pause_duration
            
            # Resume session
            session["paused"] = False
            session.pop("pause_time", None)
            
            logger.info(f"Resumed JOI session {session_id} for user {user_id}")
            
            return {
                "status": "success",
                "message": "Session resumed",
                "session_id": session_id,
                "pause_duration_seconds": pause_duration
            }
    
    def end_session(self, session_id, user_id):
        """
        End a JOI session
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Dict with status information
        """
        with self.lock:
            # Check if session exists
            if session_id not in self.active_sessions:
                return {
                    "status": "error",
                    "message": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Check if session belongs to user
            if session["user_id"] != user_id:
                return {
                    "status": "error",
                    "message": "Unauthorized access to session"
                }
            
            # Mark session as completed
            session["completed"] = True
            
            # Calculate session stats
            start_time = session["start_time"]
            end_time = time.time()
            duration_seconds = end_time - start_time
            duration_minutes = round(duration_seconds / 60, 1)
            
            # Gather session summary
            summary = {
                "session_id": session_id,
                "name": session["name"],
                "description": session["description"],
                "intensity": session["intensity"],
                "planned_duration_minutes": session["duration_minutes"],
                "actual_duration_minutes": duration_minutes,
                "instructions_count": len(session["instructions_given"]),
                "phases_completed": session["current_phase"],
                "safe_word_used": session.get("safe_word_used", False)
            }
            
            logger.info(f"Ended JOI session {session_id} for user {user_id}, duration: {duration_minutes} minutes")
            
            return {
                "status": "success",
                "message": "Session ended successfully",
                "summary": summary
            }
    
    def get_session_info(self, session_id, user_id):
        """
        Get information about a JOI session
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Dict with session information
        """
        with self.lock:
            # Check if session exists
            if session_id not in self.active_sessions:
                return {
                    "status": "error",
                    "message": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Check if session belongs to user
            if session["user_id"] != user_id:
                return {
                    "status": "error",
                    "message": "Unauthorized access to session"
                }
            
            # Format session information
            current_time = time.time()
            session_info = {
                "session_id": session_id,
                "name": session["name"],
                "description": session["description"],
                "intensity": session["intensity"],
                "duration_minutes": session["duration_minutes"],
                "start_time": session["start_time"],
                "elapsed_seconds": current_time - session["start_time"],
                "remaining_seconds": max(0, session["end_time"] - current_time),
                "current_phase": session["current_phase"],
                "phase_name": session["instruction_sets"][min(session["current_phase"], len(session["instruction_sets"])-1)]["phase"],
                "paused": session.get("paused", False),
                "completed": session.get("completed", False),
                "safe_word_used": session.get("safe_word_used", False),
                "session_progress": self._get_session_progress(session),
                "phase_progress": self._get_phase_progress(session)
            }
            
            return {
                "status": "success",
                "session": session_info
            }
    
    def get_active_sessions(self, user_id):
        """
        Get all active JOI sessions for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with active sessions information
        """
        with self.lock:
            # Find all sessions for this user
            user_sessions = {}
            
            for session_id, session in self.active_sessions.items():
                if session["user_id"] == user_id:
                    user_sessions[session_id] = {
                        "session_id": session_id,
                        "name": session["name"],
                        "intensity": session["intensity"],
                        "start_time": session["start_time"],
                        "paused": session.get("paused", False),
                        "completed": session.get("completed", False),
                        "session_progress": self._get_session_progress(session)
                    }
            
            return {
                "status": "success",
                "sessions_count": len(user_sessions),
                "sessions": user_sessions
            }
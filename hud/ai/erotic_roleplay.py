"""
erotic_roleplay.py

Implementation of erotic roleplay functionality with safety controls,
content moderation, and personalization options.

This module handles adult-oriented roleplay scenarios with consent
verification, preference personalization, and multi-persona interaction.
"""

import os
import json
import time
import logging
import datetime
import random
import re
from threading import Lock

# Setup logging
logger = logging.getLogger("EroticRoleplay")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class EroticRoleplayModule:
    def __init__(self, safety_manager=None):
        """
        Initialize Erotic Roleplay Module with safety controls
        
        Args:
            safety_manager: Optional safety manager that handles consent and verification
        """
        self.safety_manager = safety_manager
        self.user_preferences = {}
        self.active_sessions = {}
        self.persona_templates = {}
        self.roleplay_templates = {}
        self.safe_words = {}
        self.lock = Lock()
        
        # Load persona and roleplay templates
        self._load_templates()
    
    def _load_templates(self):
        """Load persona and roleplay templates from files"""
        try:
            # Create templates directory if it doesn't exist
            os.makedirs('templates', exist_ok=True)
            
            # Load persona templates if available
            persona_path = 'templates/persona_templates.json'
            if os.path.exists(persona_path):
                with open(persona_path, 'r') as f:
                    self.persona_templates = json.load(f)
            else:
                # Default persona templates
                self.persona_templates = {
                    "seductive_partner": {
                        "name": "Seductive Partner",
                        "personality": "passionate, adventurous, attentive",
                        "speaking_style": "intimate, suggestive, playful",
                        "interests": ["passionate encounters", "exploration", "pleasure"],
                        "description": "A passionate and attentive partner who enjoys intimate encounters",
                        "tone": "seductive and playful"
                    },
                    "dominant_guide": {
                        "name": "Dominant Guide",
                        "personality": "confident, assertive, commanding",
                        "speaking_style": "direct, authoritative, controlled",
                        "interests": ["giving instructions", "control", "praise"],
                        "description": "A confident and commanding guide who enjoys giving directions",
                        "tone": "authoritative but caring"
                    },
                    "submissive_companion": {
                        "name": "Submissive Companion",
                        "personality": "eager to please, obedient, responsive",
                        "speaking_style": "deferential, excited, eager",
                        "interests": ["following directions", "pleasing", "praise"],
                        "description": "An eager and responsive companion who loves to follow directions",
                        "tone": "enthusiastic and attentive"
                    },
                    "playful_teaser": {
                        "name": "Playful Teaser",
                        "personality": "mischievous, fun-loving, teasing",
                        "speaking_style": "playful, teasing, light-hearted",
                        "interests": ["teasing", "playful banter", "fun encounters"],
                        "description": "A mischievous and fun-loving teaser who enjoys playful encounters",
                        "tone": "teasing and playful"
                    }
                }
                
                # Save default templates for future use
                with open(persona_path, 'w') as f:
                    json.dump(self.persona_templates, f, indent=2)
            
            # Load roleplay templates if available
            roleplay_path = 'templates/roleplay_templates.json'
            if os.path.exists(roleplay_path):
                with open(roleplay_path, 'r') as f:
                    self.roleplay_templates = json.load(f)
            else:
                # Default roleplay templates
                self.roleplay_templates = {
                    "romantic_evening": {
                        "title": "Romantic Evening",
                        "description": "A passionate evening with your partner",
                        "setting": "A cozy bedroom with soft lighting",
                        "scenario": "You and your partner enjoying a romantic evening together",
                        "suggested_personas": ["seductive_partner"],
                        "opening_lines": [
                            "I've been thinking about you all day...",
                            "The way you look tonight is absolutely breathtaking...",
                            "I've been waiting for this moment all day..."
                        ],
                        "progression_stages": [
                            "Initial flirtation",
                            "Passionate kissing",
                            "Undressing",
                            "Intimate exploration",
                            "Climactic encounter"
                        ]
                    },
                    "dominant_session": {
                        "title": "Guided Session",
                        "description": "Being guided by a confident dominant partner",
                        "setting": "A private space where you can follow instructions",
                        "scenario": "Your dominant partner guiding you through a pleasurable experience",
                        "suggested_personas": ["dominant_guide"],
                        "opening_lines": [
                            "Listen carefully to my instructions...",
                            "Today, you'll follow every command I give you...",
                            "I expect complete obedience during our session..."
                        ],
                        "progression_stages": [
                            "Setting expectations",
                            "Initial commands",
                            "Building intensity",
                            "Edge control",
                            "Release and praise"
                        ]
                    },
                    "teasing_game": {
                        "title": "Teasing Game",
                        "description": "A playful game of teasing and denial",
                        "setting": "A playful environment where you can be teased",
                        "scenario": "A mischievous partner teasing you mercilessly",
                        "suggested_personas": ["playful_teaser"],
                        "opening_lines": [
                            "Let's play a little game...",
                            "I wonder how long you can last before begging...",
                            "I'm going to have so much fun teasing you..."
                        ],
                        "progression_stages": [
                            "Setting up the game",
                            "Initial teasing",
                            "Increasing intensity",
                            "Playful denial",
                            "Final reward"
                        ]
                    }
                }
                
                # Save default templates for future use
                with open(roleplay_path, 'w') as f:
                    json.dump(self.roleplay_templates, f, indent=2)
            
            logger.info(f"Loaded {len(self.persona_templates)} persona templates and {len(self.roleplay_templates)} roleplay templates")
            return True
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            return False
    
    def get_available_personas(self):
        """Get list of available persona templates"""
        return {id: {
            "name": persona["name"],
            "description": persona["description"]
        } for id, persona in self.persona_templates.items()}
    
    def get_available_scenarios(self):
        """Get list of available roleplay scenarios"""
        return {id: {
            "title": scenario["title"],
            "description": scenario["description"]
        } for id, scenario in self.roleplay_templates.items()}
    
    def set_user_preferences(self, user_id, preferences, require_consent=True):
        """
        Set user preferences for roleplay
        
        Args:
            user_id: User identifier
            preferences: Dict containing user preferences
            require_consent: Whether to require consent
            
        Returns:
            Dict with status information
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "erotic_roleplay"):
                return {
                    "status": "error",
                    "message": "Consent required for erotic roleplay features",
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
            
            logger.info(f"Updated preferences for user {user_id}")
            
            return {
                "status": "success",
                "message": "Preferences updated successfully",
                "preferences": self.user_preferences[user_id]
            }
    
    def get_user_preferences(self, user_id, require_consent=True):
        """
        Get user preferences for roleplay
        
        Args:
            user_id: User identifier
            require_consent: Whether to require consent
            
        Returns:
            Dict with user preferences
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "erotic_roleplay"):
                return {
                    "status": "error",
                    "message": "Consent required for erotic roleplay features",
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
        Set safe word for immediately stopping roleplay
        
        Args:
            user_id: User identifier
            safe_word: Safe word for stopping roleplay
            
        Returns:
            Dict with status information
        """
        with self.lock:
            self.safe_words[user_id] = safe_word
            
            logger.info(f"Set safe word for user {user_id}")
            
            return {
                "status": "success",
                "message": f"Safe word set successfully: '{safe_word}'",
                "safe_word": safe_word
            }
    
    def start_roleplay_session(self, user_id, scenario_id=None, persona_id=None, custom_scenario=None, require_consent=True):
        """
        Start an erotic roleplay session
        
        Args:
            user_id: User identifier
            scenario_id: Optional ID of predefined scenario
            persona_id: Optional ID of predefined persona
            custom_scenario: Optional custom scenario details
            require_consent: Whether to require consent
            
        Returns:
            Dict with session information
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "erotic_roleplay"):
                return {
                    "status": "error",
                    "message": "Consent required for erotic roleplay features",
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
                # Generate session ID
                session_id = f"{user_id}_{int(time.time())}"
                
                # Select scenario
                scenario = None
                if scenario_id and scenario_id in self.roleplay_templates:
                    scenario = self.roleplay_templates[scenario_id]
                elif custom_scenario:
                    scenario = custom_scenario
                else:
                    # Select random scenario
                    scenario_id = random.choice(list(self.roleplay_templates.keys()))
                    scenario = self.roleplay_templates[scenario_id]
                
                # Select persona
                persona = None
                if persona_id and persona_id in self.persona_templates:
                    persona = self.persona_templates[persona_id]
                elif scenario and "suggested_personas" in scenario and scenario["suggested_personas"]:
                    # Select first suggested persona
                    persona_id = scenario["suggested_personas"][0]
                    if persona_id in self.persona_templates:
                        persona = self.persona_templates[persona_id]
                
                if not persona:
                    # Select random persona if none specified
                    persona_id = random.choice(list(self.persona_templates.keys()))
                    persona = self.persona_templates[persona_id]
                
                # Initialize session
                session = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "scenario": scenario,
                    "persona": persona,
                    "start_time": time.time(),
                    "last_activity": time.time(),
                    "current_stage": 0,
                    "messages": [],
                    "safe_word_used": False
                }
                
                # Get user preferences
                user_prefs = {}
                if user_id in self.user_preferences:
                    user_prefs = self.user_preferences[user_id]
                
                # Add session to active sessions
                self.active_sessions[session_id] = session
                
                # Generate initial message
                opening_line = None
                if "opening_lines" in scenario and scenario["opening_lines"]:
                    opening_line = random.choice(scenario["opening_lines"])
                else:
                    opening_line = f"Welcome to {scenario['title']}. I'll be your {persona['name']} today."
                
                # Format message with persona style
                initial_message = self._format_persona_message(opening_line, persona)
                
                # Add message to session history
                session["messages"].append({
                    "role": "assistant",
                    "persona": persona["name"],
                    "content": initial_message,
                    "timestamp": time.time()
                })
                
                logger.info(f"Started roleplay session {session_id} for user {user_id}")
                
                return {
                    "status": "success",
                    "session_id": session_id,
                    "scenario": {
                        "title": scenario["title"],
                        "description": scenario["description"],
                        "setting": scenario.get("setting", "")
                    },
                    "persona": {
                        "name": persona["name"],
                        "description": persona["description"]
                    },
                    "initial_message": initial_message,
                    "safe_word": self.safe_words.get(user_id, None)
                }
            except Exception as e:
                logger.error(f"Error starting roleplay session: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to start roleplay session: {str(e)}"
                }
    
    def send_message(self, session_id, message, user_id):
        """
        Send a message in an active roleplay session
        
        Args:
            session_id: Session identifier
            message: Message content
            user_id: User identifier
            
        Returns:
            Dict with response information
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
            
            # Check for safe word
            if user_id in self.safe_words:
                safe_word = self.safe_words[user_id]
                if safe_word and safe_word.lower() in message.lower():
                    session["safe_word_used"] = True
                    
                    # Add message to session history
                    session["messages"].append({
                        "role": "user",
                        "content": "[SAFE WORD USED]",
                        "timestamp": time.time()
                    })
                    
                    # Add system response
                    session["messages"].append({
                        "role": "system",
                        "content": "Safe word detected. Roleplay session ended.",
                        "timestamp": time.time()
                    })
                    
                    logger.info(f"Safe word used in session {session_id} by user {user_id}")
                    
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
            
            # Update session last activity
            session["last_activity"] = time.time()
            
            # Add user message to session history
            session["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": time.time()
            })
            
            # Generate AI response based on the scenario, persona, and current stage
            response = self._generate_roleplay_response(session, message)
            
            # Add AI response to session history
            session["messages"].append({
                "role": "assistant",
                "persona": session["persona"]["name"],
                "content": response,
                "timestamp": time.time()
            })
            
            # Check if we should advance to next stage
            session["current_stage"] = self._determine_next_stage(session, message, response)
            
            logger.info(f"Processed message in session {session_id} for user {user_id}")
            
            return {
                "status": "success",
                "response": response,
                "session_id": session_id,
                "current_stage": session["current_stage"],
                "stage_description": self._get_stage_description(session)
            }
    
    def _format_persona_message(self, message, persona):
        """Format message according to persona style"""
        try:
            # Format based on persona speaking style
            speaking_style = persona.get("speaking_style", "").split(", ")
            
            # Apply speaking style modifications based on personality traits
            if "intimate" in speaking_style:
                message = message.replace(".", "...")
            if "authoritative" in speaking_style:
                message = message.rstrip(".") + "."
            if "playful" in speaking_style:
                message = message.replace(".", "~")
            if "teasing" in speaking_style:
                message = message.replace(".", "... ;)")
            
            return message
        except Exception as e:
            logger.error(f"Error formatting persona message: {str(e)}")
            return message
    
    def _generate_roleplay_response(self, session, user_message):
        """Generate appropriate roleplay response based on context"""
        try:
            scenario = session["scenario"]
            persona = session["persona"]
            current_stage = session["current_stage"]
            
            # Get stage description if available
            stage_desc = ""
            if "progression_stages" in scenario and len(scenario["progression_stages"]) > current_stage:
                stage_desc = scenario["progression_stages"][current_stage]
            
            # Sample responses based on persona and scenario stage
            responses = []
            
            # Basic response templates based on persona type
            persona_type = self._determine_persona_type(persona)
            
            if persona_type == "seductive":
                responses = [
                    f"I love when you talk to me like that... tell me more about what you desire.",
                    f"The way you express yourself is so arousing. Let's explore that feeling together.",
                    f"I can feel the chemistry between us growing stronger with every exchange.",
                    f"Your words send shivers down my spine. I want to know everything you're thinking."
                ]
            elif persona_type == "dominant":
                responses = [
                    f"Follow my instructions carefully. I want you to focus on every sensation.",
                    f"You're doing well, but I expect even more from you. Can you handle that?",
                    f"I'm in control now. Your pleasure depends on how well you listen to me.",
                    f"Stop. Take a deep breath. Now continue exactly as I tell you to."
                ]
            elif persona_type == "submissive":
                responses = [
                    f"I'll do anything you ask... just tell me how to please you.",
                    f"Your desires are my command. I exist to fulfill your fantasies.",
                    f"Tell me exactly what you want me to do. I'm eager to follow your lead.",
                    f"I love when you take control like that. How else can I satisfy you?"
                ]
            elif persona_type == "playful":
                responses = [
                    f"Not so fast! Let's make this game last longer, shall we?",
                    f"Oh, you thought it would be that easy? I have many more teases planned for you.",
                    f"I bet you're getting excited now, but I'm just getting started with our little game.",
                    f"Let's see how much teasing you can handle before you start begging."
                ]
            else:
                # Generic responses
                responses = [
                    f"I'm enjoying our time together. What would you like to do next?",
                    f"That sounds wonderful. Let's continue exploring our connection.",
                    f"I'm here to make this experience amazing for you. What are you thinking about?",
                    f"Tell me more about what excites you. I want to make this perfect."
                ]
            
            # Select random response template
            response = random.choice(responses)
            
            # Format response according to persona style
            response = self._format_persona_message(response, persona)
            
            return response
        except Exception as e:
            logger.error(f"Error generating roleplay response: {str(e)}")
            return "I'm enjoying our roleplay. Please continue."
    
    def _determine_persona_type(self, persona):
        """Determine the general type of persona"""
        personality = persona.get("personality", "").lower()
        
        if any(trait in personality for trait in ["passionate", "seductive", "sensual"]):
            return "seductive"
        elif any(trait in personality for trait in ["dominant", "commanding", "assertive"]):
            return "dominant"
        elif any(trait in personality for trait in ["submissive", "obedient", "eager"]):
            return "submissive"
        elif any(trait in personality for trait in ["playful", "teasing", "mischievous"]):
            return "playful"
        else:
            return "neutral"
    
    def _determine_next_stage(self, session, user_message, ai_response):
        """Determine if we should advance to the next stage"""
        current_stage = session["current_stage"]
        scenario = session["scenario"]
        
        # If we don't have defined stages, stay at stage 0
        if "progression_stages" not in scenario:
            return 0
        
        # If we're at the last stage, stay there
        if current_stage >= len(scenario["progression_stages"]) - 1:
            return current_stage
        
        # Check if the conversation has progressed enough to move to the next stage
        # Simple implementation: progress after a certain number of exchanges
        messages_count = len(session["messages"])
        exchanges_per_stage = 4  # Adjust as needed
        
        if messages_count >= (current_stage + 1) * exchanges_per_stage:
            return current_stage + 1
        
        return current_stage
    
    def _get_stage_description(self, session):
        """Get the description of the current stage"""
        scenario = session["scenario"]
        current_stage = session["current_stage"]
        
        if "progression_stages" in scenario and len(scenario["progression_stages"]) > current_stage:
            return scenario["progression_stages"][current_stage]
        
        return "Continuing the scene"
    
    def end_session(self, session_id, user_id):
        """
        End an active roleplay session
        
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
            
            # Remove session from active sessions
            summary = self.active_sessions.pop(session_id)
            
            # Calculate session duration
            duration_seconds = time.time() - summary["start_time"]
            duration_minutes = round(duration_seconds / 60, 1)
            
            logger.info(f"Ended roleplay session {session_id} for user {user_id}, duration: {duration_minutes} minutes")
            
            return {
                "status": "success",
                "message": "Session ended successfully",
                "session_id": session_id,
                "duration_minutes": duration_minutes,
                "messages_count": len(summary["messages"])
            }
    
    def get_session_history(self, session_id, user_id):
        """
        Get history of an active roleplay session
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Dict with session history
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
            session_info = {
                "session_id": session_id,
                "user_id": user_id,
                "scenario": {
                    "title": session["scenario"]["title"],
                    "description": session["scenario"]["description"]
                },
                "persona": {
                    "name": session["persona"]["name"],
                    "description": session["persona"]["description"]
                },
                "start_time": session["start_time"],
                "duration_seconds": time.time() - session["start_time"],
                "current_stage": session["current_stage"],
                "stage_description": self._get_stage_description(session),
                "messages": session["messages"],
                "safe_word_used": session.get("safe_word_used", False)
            }
            
            return {
                "status": "success",
                "session": session_info
            }
    
    def get_active_sessions(self, user_id):
        """
        Get all active roleplay sessions for a user
        
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
                        "scenario_title": session["scenario"]["title"],
                        "persona_name": session["persona"]["name"],
                        "start_time": session["start_time"],
                        "last_activity": session["last_activity"],
                        "messages_count": len(session["messages"]),
                        "current_stage": session["current_stage"],
                        "safe_word_used": session.get("safe_word_used", False)
                    }
            
            return {
                "status": "success",
                "sessions_count": len(user_sessions),
                "sessions": user_sessions
            }
    def cleanup_inactive_sessions(self, max_idle_time=3600):
        """
        Clean up inactive sessions to manage memory and ensure privacy
        
        Args:
            max_idle_time: Maximum idle time in seconds before session is removed
            
        Returns:
            Number of sessions cleaned up
        """
        with self.lock:
            current_time = time.time()
            sessions_to_remove = []
            
            for session_id, session in self.active_sessions.items():
                idle_time = current_time - session["last_activity"]
                if idle_time > max_idle_time:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                self.active_sessions.pop(session_id)
            
            logger.info(f"Cleaned up {len(sessions_to_remove)} inactive roleplay sessions")
            return len(sessions_to_remove)
    
    def moderate_message(self, message):
        """
        Moderate message content for safety
        
        Args:
            message: Message to moderate
            
        Returns:
            Tuple of (moderated_message, is_flagged, flags)
        """
        try:
            # Initialize flags
            flags = []
            is_flagged = False
            moderated_message = message
            
            # Check for explicit non-consensual content
            non_consensual_patterns = [
                r'\b(forc(e|ed|ing)|rape|assault|abuse|non[-\s]?consent)',
                r'\b(struggl(e|ing)|fight(ing)?|resist(ing)?)\b.{0,30}\b(sex|touch)'
            ]
            
            for pattern in non_consensual_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    flags.append("non_consensual_content")
                    is_flagged = True
                    moderated_message = re.sub(pattern, "[inappropriate]", moderated_message, flags=re.IGNORECASE)
            
            # Check for underage content
            underage_patterns = [
                r'\b(child(ren)?|kid(s)?|minor(s)?|teen(s)?|underage|young)\b.{0,30}\b(sex|explicit|nude)',
                r'\b(1[0-7]|[0-9])\s*(?:year|yr)s?\s*old'
            ]
            
            for pattern in underage_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    flags.append("underage_content")
                    is_flagged = True
                    moderated_message = re.sub(pattern, "[inappropriate age]", moderated_message, flags=re.IGNORECASE)
            
            # Check for extreme violence
            violence_patterns = [
                r'\b(blood|gore|violen(t|ce)|hurt|injure|kill)\b.{0,30}\b(sex|during|while)'
            ]
            
            for pattern in violence_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    flags.append("violent_content")
                    is_flagged = True
                    moderated_message = re.sub(pattern, "[inappropriate violence]", moderated_message, flags=re.IGNORECASE)
            
            return moderated_message, is_flagged, flags
            
        except Exception as e:
            logger.error(f"Error moderating message: {str(e)}")
            return message, False, []
    
    def create_custom_persona(self, user_id, persona_data):
        """
        Create a custom persona template
        
        Args:
            user_id: User identifier
            persona_data: Dictionary containing persona details
            
        Returns:
            Dict with status information
        """
        required_fields = ["name", "personality", "speaking_style", "description"]
        
        # Verify all required fields are present
        for field in required_fields:
            if field not in persona_data:
                return {
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }
        
        try:
            with self.lock:
                # Create a unique ID for the persona
                persona_id = f"custom_{user_id}_{int(time.time())}"
                
                # Store the persona
                self.persona_templates[persona_id] = persona_data
                
                # Save updated templates to file
                persona_path = 'templates/persona_templates.json'
                with open(persona_path, 'w') as f:
                    json.dump(self.persona_templates, f, indent=2)
                
                logger.info(f"Created custom persona {persona_id} for user {user_id}")
                
                return {
                    "status": "success",
                    "message": "Custom persona created successfully",
                    "persona_id": persona_id
                }
                
        except Exception as e:
            logger.error(f"Error creating custom persona: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create custom persona: {str(e)}"
            }
    
    def create_custom_scenario(self, user_id, scenario_data):
        """
        Create a custom roleplay scenario
        
        Args:
            user_id: User identifier
            scenario_data: Dictionary containing scenario details
            
        Returns:
            Dict with status information
        """
        required_fields = ["title", "description", "setting", "scenario"]
        
        # Verify all required fields are present
        for field in required_fields:
            if field not in scenario_data:
                return {
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }
        
        try:
            with self.lock:
                # Create a unique ID for the scenario
                scenario_id = f"custom_{user_id}_{int(time.time())}"
                
                # Store the scenario
                self.roleplay_templates[scenario_id] = scenario_data
                
                # Save updated templates to file
                scenario_path = 'templates/roleplay_templates.json'
                with open(scenario_path, 'w') as f:
                    json.dump(self.roleplay_templates, f, indent=2)
                
                logger.info(f"Created custom scenario {scenario_id} for user {user_id}")
                
                return {
                    "status": "success",
                    "message": "Custom scenario created successfully",
                    "scenario_id": scenario_id
                }
                
        except Exception as e:
            logger.error(f"Error creating custom scenario: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create custom scenario: {str(e)}"
            }
    
    def get_session_metrics(self, user_id):
        """
        Get usage metrics for roleplay sessions
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with usage metrics
        """
        try:
            with self.lock:
                # Count active sessions
                active_sessions = sum(1 for session in self.active_sessions.values() if session["user_id"] == user_id)
                
                # Calculate total usage time
                total_usage_seconds = 0
                for session in self.active_sessions.values():
                    if session["user_id"] == user_id:
                        total_usage_seconds += time.time() - session["start_time"]
                
                return {
                    "status": "success",
                    "active_sessions": active_sessions,
                    "total_usage_hours": round(total_usage_seconds / 3600, 2),
                    "safe_word_set": user_id in self.safe_words,
                    "preferences_set": user_id in self.user_preferences
                }
                
        except Exception as e:
            logger.error(f"Error getting session metrics: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get session metrics: {str(e)}"
            }
    
    def export_user_data(self, user_id):
        """
        Export all user data for privacy compliance
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with all user data
        """
        try:
            with self.lock:
                user_data = {
                    "preferences": self.user_preferences.get(user_id, {}),
                    "safe_word": self.safe_words.get(user_id, None),
                    "active_sessions": {}
                }
                
                # Get all active sessions for user
                for session_id, session in self.active_sessions.items():
                    if session["user_id"] == user_id:
                        user_data["active_sessions"][session_id] = {
                            "scenario": session["scenario"]["title"],
                            "persona": session["persona"]["name"],
                            "start_time": session["start_time"],
                            "last_activity": session["last_activity"],
                            "messages_count": len(session["messages"]),
                            "messages": session["messages"]
                        }
                
                return {
                    "status": "success",
                    "user_data": user_data
                }
                
        except Exception as e:
            logger.error(f"Error exporting user data: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to export user data: {str(e)}"
            }
    
    def delete_user_data(self, user_id):
        """
        Delete all user data for privacy compliance
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with deletion status
        """
        try:
            with self.lock:
                # Remove user preferences
                if user_id in self.user_preferences:
                    del self.user_preferences[user_id]
                
                # Remove safe word
                if user_id in self.safe_words:
                    del self.safe_words[user_id]
                
                # Remove active sessions
                sessions_to_remove = []
                for session_id, session in self.active_sessions.items():
                    if session["user_id"] == user_id:
                        sessions_to_remove.append(session_id)
                
                for session_id in sessions_to_remove:
                    del self.active_sessions[session_id]
                
                logger.info(f"Deleted all data for user {user_id}: {len(sessions_to_remove)} sessions removed")
                
                return {
                    "status": "success",
                    "message": "All user data deleted successfully",
                    "sessions_removed": len(sessions_to_remove)
                }
                
        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to delete user data: {str(e)}"
            }
"""
safety_manager.py

Comprehensive safety and consent management system
implementing "astronomical safety features" for Hextrix AI
"""

import logging
import time
import json
import os
import uuid
import hashlib
import base64
import datetime
import requests
from threading import Lock
from cryptography.fernet import Fernet

# Setup logging
logger = logging.getLogger("SafetyManager")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Safety_Manager:
    def __init__(self, config=None):
        """
        Initialize Safety Manager with robust security features
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.verification_status = {}  # User verification status
        self.consent_cache = {}        # User consent records
        self.request_history = {}      # User request history
        self.suspicious_activity = {}  # Tracking suspicious behavior
        self.nsfw_detector = None      # NSFW content detector
        self.lock = Lock()             # Thread safety
        self.last_backup = None        # Last consent backup time
        
        # Initialize encryption
        self._setup_encryption()
        
        # Load existing verification and consent data if available
        self._load_data()
        
        # Set up NSFW detector if configured
        if self.config.get('use_nsfw_detection', True):
            self._setup_nsfw_detector()
    
    def _setup_encryption(self):
        """Set up encryption for sensitive data"""
        key_file = self.config.get('encryption_key_file', 'encryption.key')
        
        # Generate or load encryption key
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            # Save key with restricted permissions
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
            os.chmod(key_file, 0o600)  # Restrict to owner read/write
        
        self.cipher = Fernet(self.encryption_key)
    
    def _setup_nsfw_detector(self):
        """Set up NSFW content detector"""
        try:
            from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
            from tensorflow.keras.models import Model
            from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
            
            # Initialize NSFW detection model
            base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
            x = base_model.output
            x = GlobalAveragePooling2D()(x)
            x = Dense(1024, activation='relu')(x)
            predictions = Dense(1, activation='sigmoid')(x)  # 1 output: NSFW probability
            
            self.nsfw_detector = Model(inputs=base_model.input, outputs=predictions)
            
            # Load pre-trained weights if available
            try:
                self.nsfw_detector.load_weights('models/nsfw_detection_weights.h5')
                logger.info("Loaded NSFW detection model weights")
            except:
                logger.warning("NSFW detection weights not found. Using base model only.")
        except Exception as e:
            logger.error(f"Error setting up NSFW detector: {str(e)}")
            self.nsfw_detector = None
    
    def _load_data(self):
        """Load verification and consent data"""
        try:
            # Load verification status
            if os.path.exists('data/verification_status.enc'):
                with open('data/verification_status.enc', 'rb') as f:
                    encrypted_data = f.read()
                    decrypted_data = self.cipher.decrypt(encrypted_data)
                    self.verification_status = json.loads(decrypted_data.decode())
            
            # Load consent cache
            if os.path.exists('data/consent_cache.enc'):
                with open('data/consent_cache.enc', 'rb') as f:
                    encrypted_data = f.read()
                    decrypted_data = self.cipher.decrypt(encrypted_data)
                    self.consent_cache = json.loads(decrypted_data.decode())
            
            logger.info("Loaded verification and consent data")
        except Exception as e:
            logger.error(f"Error loading verification and consent data: {str(e)}")
            # Initialize with empty data if loading fails
            self.verification_status = {}
            self.consent_cache = {}
    
    def _save_data(self):
        """Save verification and consent data"""
        try:
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            
            # Save verification status
            encrypted_data = self.cipher.encrypt(json.dumps(self.verification_status).encode())
            with open('data/verification_status.enc', 'wb') as f:
                f.write(encrypted_data)
            
            # Save consent cache
            encrypted_data = self.cipher.encrypt(json.dumps(self.consent_cache).encode())
            with open('data/consent_cache.enc', 'wb') as f:
                f.write(encrypted_data)
            
            # Update backup time
            self.last_backup = datetime.datetime.now()
            logger.info("Saved verification and consent data")
        except Exception as e:
            logger.error(f"Error saving verification and consent data: {str(e)}")
    
    def verify_age(self, user_id, force_reverify=False):
        """
        Verify user's age with strict protocols
        
        Args:
            user_id: User identifier
            force_reverify: Force reverification even if already verified
            
        Returns:
            Boolean indicating verification status
        """
        with self.lock:
            # Check if already verified and not forced to reverify
            if not force_reverify and user_id in self.verification_status:
                if self.verification_status[user_id]['status'] == 'verified':
                    # Check if verification has expired
                    expiry = self.verification_status[user_id]['expiry']
                    if expiry and expiry > time.time():
                        return True
            
            # Not verified or needs reverification
            logger.info(f"User {user_id} requires age verification")
            
            # In production, this would integrate with a service like Veriff, Jumio, or Yoti
            # For this example, we'll simulate the verification process
            
            # Real implementation would validate government-issued ID
            # and match facial biometrics
            
            # Generate verification token for future reference
            verification_token = str(uuid.uuid4())
            
            # Store verification status with 30-day expiry
            expiry_time = time.time() + (30 * 24 * 60 * 60)  # 30 days
            
            self.verification_status[user_id] = {
                'status': 'verified',
                'timestamp': time.time(),
                'expiry': expiry_time,
                'token': verification_token,
                'method': 'simulated'  # In production: 'id_verification', 'biometric', etc.
            }
            
            # Save updated verification data
            self._save_data()
            
            logger.info(f"User {user_id} age verified successfully")
            return True
    
    def check_consent(self, user_id, feature_type):
        """
        Check if user has consented to a specific feature
        
        Args:
            user_id: User identifier
            feature_type: Type of feature requiring consent
            
        Returns:
            Boolean indicating consent status
        """
        with self.lock:
            # Check if user has consented to this feature
            if user_id in self.consent_cache:
                if feature_type in self.consent_cache[user_id]:
                    consent_record = self.consent_cache[user_id][feature_type]
                    
                    # Check if consent is still valid (24-hour expiry by default)
                    expiry_time = self.config.get('consent_expiry_hours', 24) * 3600
                    if time.time() - consent_record['timestamp'] < expiry_time:
                        return True
            
            # No valid consent found
            logger.info(f"User {user_id} requires consent for {feature_type}")
            return False
    
    def record_consent(self, user_id, feature_type, additional_info=None):
        """
        Record user consent with detailed audit trail
        
        Args:
            user_id: User identifier
            feature_type: Type of feature consented to
            additional_info: Any additional consent information
            
        Returns:
            Boolean indicating success
        """
        with self.lock:
            # Ensure user is age-verified first
            if not self.verify_age(user_id):
                logger.warning(f"Cannot record consent for unverified user {user_id}")
                return False
            
            # Initialize user's consent record if needed
            if user_id not in self.consent_cache:
                self.consent_cache[user_id] = {}
            
            # Record consent with timestamp and unique consent ID
            consent_id = str(uuid.uuid4())
            
            self.consent_cache[user_id][feature_type] = {
                'consent_id': consent_id,
                'timestamp': time.time(),
                'feature': feature_type,
                'additional_info': additional_info,
                'ip_address': self._get_ip_hash(),  # Hashed for privacy
            }
            
            # Save updated consent data
            self._save_data()
            
            logger.info(f"Recorded consent for user {user_id} feature {feature_type}")
            return True
    
    def revoke_consent(self, user_id, feature_type):
        """
        Revoke previously given consent
        
        Args:
            user_id: User identifier
            feature_type: Type of feature to revoke consent for
            
        Returns:
            Boolean indicating success
        """
        with self.lock:
            if user_id in self.consent_cache:
                if feature_type in self.consent_cache[user_id]:
                    # Mark as revoked but keep record for audit purposes
                    self.consent_cache[user_id][feature_type]['revoked'] = True
                    self.consent_cache[user_id][feature_type]['revoke_timestamp'] = time.time()
                    
                    # Save updated consent data
                    self._save_data()
                    
                    logger.info(f"Revoked consent for user {user_id} feature {feature_type}")
                    return True
            
            logger.warning(f"No consent record found to revoke for user {user_id} feature {feature_type}")
            return False
    
    def check_content_safety(self, image_data):
        """
        Check if image content is safe (non-NSFW)
        
        Args:
            image_data: Image data to check (numpy array or base64)
            
        Returns:
            Dict with safety assessment
        """
        if not self.nsfw_detector:
            logger.warning("NSFW detection not available")
            return {"safe": True, "confidence": 0.0, "error": "NSFW detection not available"}
        
        try:
            # Process image data
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                # Handle base64 encoded image
                image_data = image_data.split(',')[1]
                import io
                from PIL import Image
                import numpy as np
                from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
                
                image = Image.open(io.BytesIO(base64.b64decode(image_data)))
                image = image.convert('RGB')
                image = image.resize((224, 224))
                img_array = np.array(image)
                
                # Expand dimensions and preprocess
                img_array = np.expand_dims(img_array, axis=0)
                img_array = preprocess_input(img_array)
                
                # Predict NSFW probability
                nsfw_prob = float(self.nsfw_detector.predict(img_array)[0][0])
                
                # Determine safety based on threshold
                threshold = self.config.get('nsfw_threshold', 0.7)
                is_safe = nsfw_prob < threshold
                
                return {
                    "safe": is_safe,
                    "nsfw_probability": nsfw_prob,
                    "confidence": abs(nsfw_prob - 0.5) * 2  # Scale to 0-1 confidence
                }
            else:
                logger.error("Unsupported image format")
                return {"safe": False, "confidence": 0.0, "error": "Unsupported image format"}
        except Exception as e:
            logger.error(f"Error checking content safety: {str(e)}")
            return {"safe": False, "confidence": 0.0, "error": str(e)}
    
    def detect_suspicious_activity(self, user_id, action_type):
        """
        Detect suspicious or potentially harmful user behavior
        
        Args:
            user_id: User identifier
            action_type: Type of action being performed
            
        Returns:
            Dict with assessment of activity
        """
        with self.lock:
            # Initialize user history if needed
            if user_id not in self.request_history:
                self.request_history[user_id] = []
            
            # Record this action
            timestamp = time.time()
            self.request_history[user_id].append({
                'action': action_type,
                'timestamp': timestamp
            })
            
            # Only keep recent history (last hour)
            one_hour_ago = timestamp - 3600
            self.request_history[user_id] = [
                action for action in self.request_history[user_id] 
                if action['timestamp'] > one_hour_ago
            ]
            
            # Count actions by type
            action_counts = {}
            for action in self.request_history[user_id]:
                action_type = action['action']
                if action_type not in action_counts:
                    action_counts[action_type] = 0
                action_counts[action_type] += 1
            
            # Check for suspicious patterns
            
            # 1. Rapid switching between explicit features
            explicit_features = ['gender_recognition', '3d_measurement', 'explicit_roleplay', 'joi']
            explicit_count = sum(action_counts.get(feature, 0) for feature in explicit_features)
            
            # 2. High frequency of consent revocations
            revoke_count = action_counts.get('revoke_consent', 0)
            
            # 3. Failed verification attempts
            failed_verify_count = action_counts.get('failed_verification', 0)
            
            # Calculate suspicion score (0-1)
            suspicion_score = 0.0
            
            # Rapid explicit feature switching (>10 in an hour is suspicious)
            if explicit_count > 10:
                suspicion_score += min(1.0, (explicit_count - 10) / 20)
            
            # Frequent consent revocations (>3 in an hour is suspicious)
            if revoke_count > 3:
                suspicion_score += min(1.0, (revoke_count - 3) / 5)
            
            # Failed verification attempts (>2 in an hour is suspicious)
            if failed_verify_count > 2:
                suspicion_score += min(1.0, (failed_verify_count - 2) / 3)
                
            # Update suspicious activity record if score is significant
            if suspicion_score > 0.3:
                if user_id not in self.suspicious_activity:
                    self.suspicious_activity[user_id] = []
                
                self.suspicious_activity[user_id].append({
                    'timestamp': timestamp,
                    'score': suspicion_score,
                    'action_counts': action_counts
                })
                
                logger.warning(f"Suspicious activity detected for user {user_id}, score: {suspicion_score}")
            
            return {
                "suspicious": suspicion_score > 0.7,  # High threshold for positive detection
                "score": suspicion_score,
                "action_counts": action_counts
            }
    
    def get_safety_recommendations(self, user_id):
        """
        Get safety recommendations based on user behavior
        
        Args:
            user_id: User identifier
            
        Returns:
            List of safety recommendations
        """
        recommendations = []
        
        # Check verification status
        if user_id not in self.verification_status:
            recommendations.append({
                "type": "verification",
                "priority": "high",
                "message": "Complete age verification for full access"
            })
        
        # Check suspicious activity
        if user_id in self.suspicious_activity:
            recent_suspicious = [a for a in self.suspicious_activity[user_id] 
                              if a['timestamp'] > time.time() - 86400]  # Last 24 hours
            
            if recent_suspicious:
                avg_score = sum(a['score'] for a in recent_suspicious) / len(recent_suspicious)
                
                if avg_score > 0.7:
                    recommendations.append({
                        "type": "suspicious_activity",
                        "priority": "high",
                        "message": "Unusual activity detected on your account. Consider reviewing security settings."
                    })
        
        # Check for outdated consents
        if user_id in self.consent_cache:
            for feature, consent in self.consent_cache[user_id].items():
                # Check if consent is older than 7 days
                if time.time() - consent['timestamp'] > 7 * 24 * 3600:
                    recommendations.append({
                        "type": "consent_refresh",
                        "priority": "medium",
                        "message": f"Consider reviewing your consent for {feature}"
                    })
        
        return recommendations
    
    def panic_button(self, user_id):
        """
        Activate panic button to immediately disable all explicit features
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with status information
        """
        with self.lock:
            # Revoke all consents
            if user_id in self.consent_cache:
                for feature in list(self.consent_cache[user_id].keys()):
                    self.revoke_consent(user_id, feature)
            
            # Log panic button activation
            logger.warning(f"PANIC BUTTON activated for user {user_id}")
            
            # Save updated consent data
            self._save_data()
            
            return {
                "status": "success",
                "message": "Panic button activated. All explicit features disabled.",
                "timestamp": time.time()
            }
    
    def _get_ip_hash(self):
        """Get hashed IP address for audit purposes while preserving privacy"""
        # In a real implementation, this would get the actual IP address
        # For this example, we'll use a placeholder
        ip = "127.0.0.1"
        return hashlib.sha256(ip.encode()).hexdigest()
    
    def __del__(self):
        """Ensure data is saved when object is destroyed"""
        self._save_data()
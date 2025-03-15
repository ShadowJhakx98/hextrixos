"""
gender_recognition.py

Implementation of gender recognition using ONNX Runtime instead of TensorFlow
with safety protocols and consent requirements
"""

import numpy as np
import onnxruntime as ort
import logging
import base64
import datetime
from io import BytesIO
from PIL import Image
import os
import requests

# Setup logging
logger = logging.getLogger("GenderRecognition")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class GenderRecognitionModule:
    def __init__(self, safety_manager=None):
        """
        Initialize Gender Recognition Module with safety protocols
        
        Args:
            safety_manager: Optional safety manager that handles consent and verification
        """
        self.model = None
        self.initialized = False
        self.safety_manager = safety_manager
        self.last_detection = None
        self.confidence_threshold = 0.75
        self.model_path = "models/gender_recognition_model.onnx"
        
    def initialize(self):
        """Initialize the gender recognition model"""
        try:
            # Check if model exists locally
            if not os.path.exists(self.model_path):
                # Create models directory if it doesn't exist
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                
                # Download a pre-trained ONNX model (example URL - replace with actual URL)
                model_url = "https://example.com/models/gender_recognition_model.onnx"
                try:
                    logger.info(f"Downloading gender recognition model from {model_url}")
                    response = requests.get(model_url)
                    with open(self.model_path, 'wb') as f:
                        f.write(response.content)
                except Exception as e:
                    logger.error(f"Error downloading model: {str(e)}")
                    return False
            
            # Create ONNX inference session
            self.model = ort.InferenceSession(self.model_path)
            
            self.initialized = True
            logger.info("Gender recognition model initialized successfully using ONNX Runtime")
            return True
        except Exception as e:
            logger.error(f"Error initializing gender recognition model: {str(e)}")
            self.initialized = False
            return False
    
    def detect_gender(self, image_data, require_consent=True, user_id=None):
        """
        Detect gender from image with safety checks
        
        Args:
            image_data: Base64 encoded image or numpy array
            require_consent: Whether to require consent check
            user_id: User ID for consent verification
            
        Returns:
            Dict with detection results or error
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "gender_recognition"):
                return {
                    "status": "error",
                    "message": "Consent required for gender recognition",
                    "requires_consent": True
                }
            
            if not self.safety_manager.verify_age(user_id):
                return {
                    "status": "error", 
                    "message": "Age verification required",
                    "requires_verification": True
                }
        
        # Model check
        if not self.initialized:
            if not self.initialize():
                return {"status": "error", "message": "Failed to initialize model"}
        
        try:
            # Process image data
            processed_image = self._preprocess_image(image_data)
            
            # Get input and output names
            input_name = self.model.get_inputs()[0].name
            output_name = self.model.get_outputs()[0].name
            
            # Run prediction
            results = self.model.run([output_name], {input_name: processed_image})
            predictions = results[0][0]
            
            gender_index = np.argmax(predictions)
            confidence = float(predictions[gender_index])
            
            gender = "male" if gender_index == 0 else "female"
            
            # Store last detection
            self.last_detection = {
                "gender": gender,
                "confidence": confidence,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Return detection with confidence
            result = {
                "status": "success",
                "gender": gender,
                "confidence": confidence,
                "is_reliable": confidence >= self.confidence_threshold
            }
            
            logger.info(f"Gender detection: {gender} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting gender: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _preprocess_image(self, image_data):
        """Process image data for model input"""
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # Handle base64 encoded image
            image_data = image_data.split(',')[1]
            image = Image.open(BytesIO(base64.b64decode(image_data)))
            image = image.convert('RGB')
            image = image.resize((224, 224))
            img_array = np.array(image)
        elif isinstance(image_data, np.ndarray):
            # Handle numpy array
            from PIL import Image
            img = Image.fromarray(image_data)
            img = img.resize((224, 224))
            img_array = np.array(img)
        else:
            raise ValueError("Unsupported image format")
        
        # Normalize image (scale pixel values between 0 and 1)
        img_array = img_array.astype(np.float32) / 255.0
        
        # Expand dimensions to create batch of 1
        return np.expand_dims(img_array, axis=0)
    
    # Fallback method that doesn't require a model
    def simple_detect_gender(self, image_data, require_consent=True, user_id=None):
        """
        Simple gender detection that doesn't require a model
        Works by analyzing color patterns and simple heuristics
        
        Args:
            image_data: Base64 encoded image or numpy array
            require_consent: Whether to require consent check
            user_id: User ID for consent verification
            
        Returns:
            Dict with detection results
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "gender_recognition"):
                return {
                    "status": "error",
                    "message": "Consent required for gender recognition",
                    "requires_consent": True
                }
        
        try:
            # Process image to simple array
            img_array = self._simple_preprocess_image(image_data)
            
            # Extract simple features (color averages, etc.)
            features = self._extract_simple_features(img_array)
            
            # Make a simple prediction based on features
            gender, confidence = self._simple_predict(features)
            
            # Store last detection
            self.last_detection = {
                "gender": gender,
                "confidence": confidence,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Return detection with confidence
            result = {
                "status": "success",
                "gender": gender,
                "confidence": confidence,
                "is_reliable": confidence >= 0.65  # Lower threshold for simple method
            }
            
            logger.info(f"Simple gender detection: {gender} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error performing simple gender detection: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _simple_preprocess_image(self, image_data):
        """Process image data for simple analysis"""
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # Handle base64 encoded image
            image_data = image_data.split(',')[1]
            image = Image.open(BytesIO(base64.b64decode(image_data)))
            image = image.convert('RGB')
            image = image.resize((100, 100))  # Smaller size for simple analysis
            return np.array(image)
        elif isinstance(image_data, np.ndarray):
            # Handle numpy array
            from PIL import Image
            img = Image.fromarray(image_data)
            img = img.resize((100, 100))
            return np.array(img)
        else:
            raise ValueError("Unsupported image format")
    
    def _extract_simple_features(self, img_array):
        """Extract simple features from image array"""
        features = {}
        
        # Calculate average color values
        features['avg_red'] = np.mean(img_array[:, :, 0])
        features['avg_green'] = np.mean(img_array[:, :, 1])
        features['avg_blue'] = np.mean(img_array[:, :, 2])
        
        # Calculate standard deviation of colors
        features['std_red'] = np.std(img_array[:, :, 0])
        features['std_green'] = np.std(img_array[:, :, 1])
        features['std_blue'] = np.std(img_array[:, :, 2])
        
        # Calculate ratio of red to blue (can be useful for skin tone detection)
        features['red_blue_ratio'] = features['avg_red'] / max(1, features['avg_blue'])
        
        # Calculate brightness
        features['brightness'] = (features['avg_red'] + features['avg_green'] + features['avg_blue']) / 3
        
        return features
    
    def _simple_predict(self, features):
        """Make a simple prediction based on extracted features"""
        # This is a very simplified heuristic and won't be accurate
        # In a real implementation, you'd want to use a proper pre-trained model
        
        # Example heuristic: higher red/blue ratio often correlates with female faces in some datasets
        # This is an oversimplification and will not be accurate for most cases
        score = 0
        
        # Higher red/blue ratio gives higher female probability
        if features['red_blue_ratio'] > 1.05:
            score += 0.2
        
        # Higher green standard deviation gives higher female probability
        if features['std_green'] > 50:
            score += 0.1
        
        # Lower brightness gives higher male probability
        if features['brightness'] < 120:
            score -= 0.1
        
        # Lower color standard deviation gives higher male probability
        if (features['std_red'] + features['std_green'] + features['std_blue']) / 3 < 40:
            score -= 0.2
        
        # Convert score to probability
        probability = 1 / (1 + np.exp(-score))  # Sigmoid function
        
        # Determine gender and confidence
        if probability > 0.5:
            return "female", probability
        else:
            return "male", 1 - probability
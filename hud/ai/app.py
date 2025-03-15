# app.py
import os
import json
import uuid
import threading
import base64
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_socketio import SocketIO, emit
import numpy as np
import torch
from transformers import pipeline, AutoProcessor, AutoModelForCausalLM
import google.generativeai as genai
import requests
import openai
from PIL import Image
import io
import cv2
import whisper
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from serpapi import GoogleSearch
import random
from dotenv import load_dotenv
import requests.adapters
import urllib3
import logging

# Import our modules
# Import MCP extension
try:
    from app_mcp_extension import inject_mcp_extension
except ImportError:
    print("Warning: MCP extension not available")
    inject_mcp_extension = None

from mem_drive import CloudMemoryManager
from self_awareness import SelfAwareness

# Import 3D measurement module
from measurement_3d import Measurement3DModule

# Import Google API integrations
from google_api_manager import GoogleAPIManager
from fitness_integration import FitnessIntegration
from gmail_integration import GmailIntegration
from photos_integration import PhotosIntegration
from drive_integration import DriveIntegration
from immersive_xr_integration import ImmersiveXRIntegration
from contacts_integration import ContactsIntegration
from erotic_roleplay import EroticRoleplayModule
from gender_recognition import GenderRecognitionModule
from joi_module import JOIModule
from safety_module import Safety_Manager
# Initialize with safety manager
roleplay_module = EroticRoleplayModule(safety_manager=Safety_Manager)
gender_recognition_module = GenderRecognitionModule(safety_manager=Safety_Manager)
joi_module = JOIModule(safety_manager=Safety_Manager)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Increase connection pool size
adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20)
requests_session = requests.Session()
requests_session.mount('https://', adapter)
requests_session.mount('http://', adapter)

# Initialize Kinect processor if available
try:
    from kinect_processor import KinectProcessor
    from simple_point_cloud import PointCloud
    from web_interface import PointCloudVisualizer
    kinect_processor = KinectProcessor()
    has_kinect = True
except ImportError:
    logger.warning("Kinect processor not available. Skipping initialization.")
    has_kinect = False

# Load environment variables
load_dotenv()

# Download NLTK data for text processing and sentiment analysis
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

# Initialize Flask app
app = Flask(__name__)

# Initialize MCP extension
if inject_mcp_extension:
    try:
        mcp_extension = inject_mcp_extension(app)
        print("MCP extension initialized successfully")
    except Exception as e:
        print(f"Error initializing MCP extension: {e}")
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

if has_kinect:
    point_cloud_visualizer = PointCloudVisualizer(app, socketio)

# Choose the appropriate memory implementation
IN_CODESPACES = os.environ.get('CODESPACES', False) or os.environ.get('GITHUB_CODESPACES', False)

try:
    # First determine where we're running
    if IN_CODESPACES:
        # GitHub Codespaces configuration
        local_cache_size = 500_000_000  # 500MB local cache
        internal_memory_size = 500_000_000  # 500MB on internal drive
        cloud_memory_size = 1_000_000_000  # 1TB in Google Drive
        max_data_size = 200_000_000  # 200MB max data
        logger.info("Running in GitHub Codespaces - using 500MB local cache with 1TB Google Drive backend")
        
        # Initialize with GitHub Codespaces settings
        memory_drive = CloudMemoryManager(
            local_cache_size=local_cache_size,
            memory_path="brain_memory_cache.bin"  # Store in default location
        )
    else:
        # Local machine configuration - point directly to external drive
        local_cache_size = 5_000_000_000  # 5GB cache
        external_hdd_path = "D:\\HextrixMemory"  # Update this to your external drive path
        cloud_memory_size = 1_000_000_000  # 1TB in Google Drive
        
        # Create external directory if it doesn't exist
        if not os.path.exists(external_hdd_path):
            os.makedirs(external_hdd_path, exist_ok=True)
            
        logger.info(f"Running locally - using external drive at {external_hdd_path} with Google Drive backend")
        
        # Initialize pointing directly to external drive
        memory_drive = CloudMemoryManager(
            local_cache_size=local_cache_size,
            memory_path=os.path.join(external_hdd_path, "brain_memory_cache.bin")  # Store directly on external
        )
    
    # Initialize memory and services
    success = memory_drive.initialize_memory()
    if not success:
        logger.warning("Failed to initialize memory properly, using fallback mode")

    
    # Try to initialize Google Drive connection
    drive_connected = memory_drive.initialize_drive_service()
    
    # Download memory from Google Drive if connected
    if drive_connected:
        logger.info("Connected to Google Drive - downloading memory file")
        memory_drive.download_memory()
        
        # Configure backup settings for efficient storage
        backup_drive_id = os.environ.get("BACKUP_GDRIVE_ID")
        if backup_drive_id:
            memory_drive.backup_drive_id = backup_drive_id  # Store backup drive ID
            logger.info(f"Using separate Google Drive for backups: {backup_drive_id}")
            
        # Configure to use compressed, efficient backups
        memory_drive.use_efficient_backups = True
    else:
        logger.info("Not connected to Google Drive - using local cache only")
    
except Exception as e:
    logger.error(f"Cloud memory initialization error: {str(e)}")
    logger.info("Falling back to minimal memory manager")

    # Fallback to simple memory initialization
    if IN_CODESPACES:
        memory_size = 1_000_000_000  # 1GB
        local_cache_size = 500_000_000  # 500MB
    else:
        memory_size = 10_000_000_000  # 10GB 
        local_cache_size = 5_000_000_000  # 5GB
        
    memory_drive = CloudMemoryManager(
        local_cache_size=local_cache_size
    )
    memory_drive.initialize_memory()
    memory_drive.initialize_drive_service()  # Will fallback gracefully if credentials not available

# Initialize 3D measurement module
measurement_module = Measurement3DModule()

# Initialize Google API Manager and integrations
api_manager = GoogleAPIManager()
fitness_api = FitnessIntegration(api_manager)
gmail_api = GmailIntegration(api_manager)
photos_api = PhotosIntegration(api_manager)
drive_api = DriveIntegration(api_manager) 
immersive_xr_api = ImmersiveXRIntegration(api_manager)
contacts_api = ContactsIntegration(api_manager)

# Check API keys
required_keys = [
    "GOOGLE_API_KEY",
    "CLOUDFLARE_API_KEY",
    "CLOUDFLARE_ACCOUNT_ID",
    "SERP_API_KEY",
    "PERPLEXITY_API_KEY"
]

for key in required_keys:
    value = os.environ.get(key)
    if not value:
        logger.warning(f"{key} environment variable not set.")
    else:
        os.environ[key] = value

# Start Kinect processing thread if available
if has_kinect:
    def kinect_thread():
        camera_initialized = False
        
        # Try to initialize cameras
        for retry in range(3):  # Try 3 times
            if kinect_processor.initialize_cameras():
                camera_initialized = True
                logger.info("Successfully initialized Kinect cameras")
                break
            else:
                logger.warning(f"Failed to initialize Kinect cameras (attempt {retry+1}/3)")
                time.sleep(2)  # Wait before retry
        
        if not camera_initialized:
            logger.error("Failed to initialize Kinect cameras after multiple attempts")
            # Instead of returning, continue with a flag to show a message in the UI
            # This allows the thread to stay alive and potentially recover if cameras become available
            
        while True:
            if camera_initialized:
                color_frame, depth_frame = kinect_processor.capture_frames()
                if color_frame is not None and depth_frame is not None:
                    # Process frames and update visualization
                    try:
                        point_cloud = kinect_processor.convert_depth_to_point_cloud(depth_frame, color_frame)
                        if point_cloud:
                            # Downsample and filter
                            processed_cloud = point_cloud.voxel_downsample(0.05)
                            point_cloud_visualizer.update_point_cloud(processed_cloud)
                        
                        # Update camera views
                        point_cloud_visualizer.update_camera_view(color_frame, depth_frame)
                    except Exception as e:
                        logger.error(f"Error processing Kinect frames: {e}")
            else:
                # Try to re-initialize cameras occasionally
                if random.random() < 0.01:  # ~1% chance per iteration
                    logger.info("Attempting to re-initialize Kinect cameras...")
                    camera_initialized = kinect_processor.initialize_cameras()
                
                # Send a "no camera" message to the UI
                point_cloud_visualizer.show_no_camera_message()
            
            time.sleep(0.033)  # ~30 FPS

    # Start thread
    threading.Thread(target=kinect_thread, daemon=True).start()
def process_video_with_hybrid_pipeline(image_data, prompt="Analyze what's visible in this image"):
    """
    Process video frames using a hybrid pipeline that leverages both LLaVA (local) and Gemini models (API)
    following the pattern: video-capture-feed > myaicode > gemini-2.0-pro-exp-02-05 > LLaVA > gemini-2.0-pro-exp-02-05 > myaicode
    
    Args:
        image_data: Base64 encoded image data
        prompt: The prompt to guide analysis
        
    Returns:
        Analysis results from the hybrid pipeline
    """
    try:
        # Convert base64 to binary if needed
        if image_data.startswith('data:image'):
            image_binary = base64.b64decode(image_data.split(',')[1])
        else:
            image_binary = base64.b64decode(image_data)
        
        # Step 1: Initial processing with gemini-2.0-pro-exp-02-05
        # Use the actual Google generative AI library for this step
        try:
            # This is the right way to use the Google Gemini model
            generation_config = {
                "temperature": 0.4,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            initial_prompt = f"You're about to receive an image for analysis. Prepare a detailed prompt to analyze visual elements: {prompt}"
            initial_response = models["gemini"].generate_content(
                initial_prompt,
                generation_config=generation_config
            ).text
        except Exception as gemini_error:
            logger.error(f"Error with Gemini 2.0: {gemini_error}")
            initial_response = f"Preparing to analyze the image with focus on: {prompt}"
        
        # Step 2: Process with LLaVA (local option) for visual analysis
        # LLaVA is used as indicated in the hybrid approach from the document
        try:
            vision_prompt = f"Based on this guidance: {initial_response}, {prompt}"
            vision_response = cloudflare_inference(
                models["llava"]["name"],  # This is LLaVA via Cloudflare
                data=io.BytesIO(image_binary),
                payload={"prompt": vision_prompt}
            )
            
            vision_summary = vision_response.get('result', {}).get('response', "Error analyzing image")
        except Exception as llava_error:
            logger.error(f"Error with LLaVA: {llava_error}")
            vision_summary = "Unable to process image with LLaVA model"
        
        # Step 3: Final processing with gemini-2.0-pro-exp-02-05 again
        try:
            final_prompt = f"Based on this image analysis: '{vision_summary}', provide a comprehensive interpretation."
            final_response = models["gemini"].generate_content(
                final_prompt,
                generation_config=generation_config
            ).text
        except Exception as final_gemini_error:
            logger.error(f"Error with final Gemini processing: {final_gemini_error}")
            final_response = f"Based on the image analysis: {vision_summary}"
        
        return {
            "initial_interpretation": initial_response,
            "vision_analysis": vision_summary,
            "final_analysis": final_response,
            "timestamp": datetime.now().isoformat(),
            "used_hybrid_pipeline": True
        }
        
    except Exception as e:
        logger.error(f"Error in hybrid pipeline processing: {str(e)}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

def llava_only_fallback(image_data, prompt="Analyze what's visible in this image"):
    """
    Fallback to only use LLaVA if Gemini is unavailable
    """
    try:
        # Convert base64 to binary if needed
        if image_data.startswith('data:image'):
            image_binary = base64.b64decode(image_data.split(',')[1])
        else:
            image_binary = base64.b64decode(image_data)
        
        # Process directly with LLaVA
        vision_response = cloudflare_inference(
            models["llava"]["name"],
            data=io.BytesIO(image_binary),
            payload={"prompt": prompt}
        )
        
        analysis = vision_response.get('result', {}).get('response', "Error analyzing image")
        
        return {
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "used_fallback": True
        }
    except Exception as e:
        logger.error(f"Error in LLaVA fallback: {str(e)}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}
# Add functions to manually trigger sync
def upload_memory_to_drive():
    """Manually trigger memory upload to Google Drive"""
    if hasattr(memory_drive, 'upload_memory'):
        return memory_drive.upload_memory()
    return False

def download_memory_from_drive():
    """Manually trigger memory download from Google Drive"""
    if hasattr(memory_drive, 'download_memory'):
        return memory_drive.download_memory()
    return False

def create_memory_backup():
    """Manually create a backup of the memory in Google Drive"""
    if hasattr(memory_drive, 'create_backup'):
        return memory_drive.create_backup()
    return False

# AI Emotion State
class EmotionalState:
    def __init__(self):
        # Base emotions with initial neutral values
        self.emotions = {
            "joy": 0.5,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "trust": 0.5,
            "anticipation": 0.3
        }
        self.mood_decay_rate = 0.05  # How quickly emotions return to baseline
        self.last_update = time.time()

    def update_emotion(self, emotion, value, max_change=0.3):
        """Update an emotion value with limits on change magnitude"""
        # Apply time-based decay to all emotions
        self._apply_decay()

        # Ensure the emotion exists
        if emotion not in self.emotions:
            return False

        # Calculate new value with change limit
        current = self.emotions[emotion]
        change = min(abs(value - current), max_change) * (1 if value > current else -1)
        self.emotions[emotion] = max(0.0, min(1.0, current + change))

        # Update opposing emotions (e.g., increasing joy should decrease sadness)
        self._update_opposing_emotions(emotion)

        self.last_update = time.time()
        return True

    def _apply_decay(self):
        """Apply time-based decay to move emotions toward baseline"""
        now = time.time()
        elapsed = now - self.last_update
        decay_factor = min(1.0, elapsed * self.mood_decay_rate)

        # Define baseline values for each emotion
        baselines = {
            "joy": 0.5,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "trust": 0.5,
            "anticipation": 0.3
        }

        # Apply decay toward baseline for each emotion
        for emotion in self.emotions:
            current = self.emotions[emotion]
            baseline = baselines[emotion]
            self.emotions[emotion] = current + (baseline - current) * decay_factor

    def _update_opposing_emotions(self, primary_emotion):
        """Update opposing emotions when one emotion changes"""
        opposing_pairs = {
            "joy": "sadness",
            "sadness": "joy",
            "anger": "trust",
            "trust": "anger",
            "fear": "anticipation",
            "anticipation": "fear",
            "surprise": "anticipation",
            "disgust": "trust"
        }

        if primary_emotion in opposing_pairs:
            opposing = opposing_pairs[primary_emotion]
            # Reduce the opposing emotion somewhat
            self.emotions[opposing] = max(0.0, self.emotions[opposing] - 0.1)

    def get_dominant_emotion(self):
        """Return the current dominant emotion"""
        return max(self.emotions, key=self.emotions.get)

    def get_emotional_state(self):
        """Return the full emotional state"""
        return self.emotions

    def get_response_modifier(self):
        """Generate text that describes the current emotional state for response modification"""
        dominant = self.get_dominant_emotion()
        intensity = self.emotions[dominant]

        modifiers = {
            "joy": ["happy", "delighted", "excited", "pleased"],
            "sadness": ["sad", "melancholy", "downcast", "somber"],
            "anger": ["irritated", "annoyed", "upset", "frustrated"],
            "fear": ["concerned", "worried", "apprehensive", "nervous"],
            "surprise": ["surprised", "astonished", "amazed", "intrigued"],
            "disgust": ["displeased", "uncomfortable", "dismayed", "troubled"],
            "trust": ["confident", "assured", "supportive", "optimistic"],
            "anticipation": ["eager", "interested", "curious", "expectant"]
        }

        # Choose a modifier based on intensity
        idx = min(int(intensity * len(modifiers[dominant])), len(modifiers[dominant]) - 1)
        return modifiers[dominant][idx]

# Memory store for persistent conversations
class MemoryStore:
    def __init__(self):
        self.conversations = {}
        self.memory_index = {}  # Keywords to conversation mapping
        self.sentiment_history = {}  # Track sentiment trends

    def add_conversation(self, user_id, message, response, sentiment=None, timestamp=None):
        if user_id not in self.conversations:
            self.conversations[user_id] = []
            self.sentiment_history[user_id] = []

        if timestamp is None:
            timestamp = datetime.now().isoformat()

        conversation = {
            "user_message": message,
            "ai_response": response,
            "timestamp": timestamp,
            "sentiment": sentiment
        }

        self.conversations[user_id].append(conversation)

        # Store sentiment data if available
        if sentiment:
            self.sentiment_history[user_id].append({
                "timestamp": timestamp,
                "sentiment": sentiment
            })

        # Extract keywords and index the conversation
        self._index_conversation(user_id, len(self.conversations[user_id]) - 1, message, response)

    def get_conversations(self, user_id):
        return self.conversations.get(user_id, [])

    def get_sentiment_trend(self, user_id, window=5):
        """Get the sentiment trend over the last n interactions"""
        history = self.sentiment_history.get(user_id, [])
        if not history:
            return {"trend": "neutral", "average": 0}

        recent = history[-window:] if len(history) >= window else history
        values = [item["sentiment"]["compound"] for item in recent]
        avg = sum(values) / len(values)

        # Calculate trend (rising, falling, stable)
        if len(values) >= 3:
            first_half = sum(values[:len(values) // 2]) / (len(values) // 2)
            second_half = sum(values[len(values) // 2:]) / (len(values) - len(values) // 2)
            diff = second_half - first_half

            if diff > 0.15:
                trend = "rising"
            elif diff < -0.15:
                trend = "falling"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {"trend": trend, "average": avg}

    def get_by_keyword(self, user_id, keyword):
        if keyword in self.memory_index:
            return [self.conversations[user_id][idx] for idx in self.memory_index[keyword]
                    if user_id in self.conversations and idx < len(self.conversations[user_id])]
        return []

    def _index_conversation(self, user_id, conversation_idx, message, response):
        combined_text = f"{message} {response}"

        # Tokenize and filter out stopwords
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(combined_text.lower())
        keywords = [word for word in tokens if word.isalnum() and word not in stop_words]

        # Add to index
        for keyword in set(keywords):  # Using set to avoid duplicates
            if keyword not in self.memory_index:
                self.memory_index[keyword] = []
            self.memory_index[keyword].append(conversation_idx)

# Initialize memory store and emotional state
memory = MemoryStore()
ai_emotion = EmotionalState()

# Define a simple placeholder for the JARVIS class that will be used by SelfAwareness
class JARVISBridge:
    def introspect(self):
        # For now, just return a simple representation of the app structure
        # In a full implementation, this would return the actual code or model definitions
        return """
        class HextrixAI:
            def __init__(self):
                self.memory_store = MemoryStore()
                self.memory_drive = CloudMemoryManager()
                self.ai_emotion = EmotionalState()
                self.models = {
                    "llama": "LLM for text generation",
                    "gemini": "Multimodal model",
                    "whisper": "Speech recognition",
                    "sd_xl": "Image generation",
                    "sentiment": "Emotion detection"
                }
                
            def process_text(self, text, model="llama"):
                # Process text input
                pass
                
            def process_vision(self, image, prompt):
                # Process image input
                pass
                
            def process_speech(self, audio):
                # Process speech input
                pass
        """

# Initialize the SelfAwareness system with our bridge
jarvis_bridge = JARVISBridge()
self_awareness = SelfAwareness(jarvis_bridge)

# Safety Manager for age verification and consent
class SafetyManager:
    def __init__(self):
        self.verified_users = {}
        self.consent_settings = {}
        
    def check_consent(self, user_id, feature_type):
        if not user_id in self.consent_settings:
            return False
        return self.consent_settings.get(user_id, {}).get(feature_type, False)
        
    def set_consent(self, user_id, feature_type, has_consent):
        if not user_id in self.consent_settings:
            self.consent_settings[user_id] = {}
        self.consent_settings[user_id][feature_type] = has_consent
        return True
        
    def verify_age(self, user_id):
        return user_id in self.verified_users and self.verified_users[user_id]
        
    def set_age_verification(self, user_id, is_verified):
        self.verified_users[user_id] = is_verified
        return True

# Initialize safety manager
safety_manager = SafetyManager()
measurement_module.safety_manager = safety_manager  # Connect to 3D measurement module

# CloudflLare Inference Helper Function
def cloudflare_inference(model_id, payload=None, data=None, task=None):
    api_url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/ai/run/{model_id}"
    headers = {
        "Authorization": f"Bearer {os.environ['CLOUDFLARE_API_KEY']}",
        "Content-Type": "application/json"
    }
    if payload:
        response = requests.post(api_url, headers=headers, json=payload)
    elif data:
        files = {'file': data}
        response = requests.post(api_url, headers=headers, files=files) # For binary data like images/audio
    else:
        raise ValueError("Either payload or data must be provided for Cloudflare inference.")

    if response.status_code != 200:
        raise Exception(f"Cloudflare Inference API Error: {response.status_code}, {response.text}")

    return response.json()

# Hugging Face Inference Router for Speech Emotion
def huggingface_speech_emotion_inference(audio_data):
    api_url = "https://api-inference.huggingface.co/router/ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
    headers = {"Authorization": f"Bearer {os.environ.get('HF_INFERENCE_API_KEY')}"} # Consider setting HF_INFERENCE_API_KEY if needed, or remove if public model
    try:
        response = requests.post(api_url, headers=headers, files={"audio_file": audio_data})
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Hugging Face Inference API Error: {e}")
        return None

# AI Model Loading
def load_llava():
    logger.info("Loading LLaVA model...")
    return {"name": "@cf/llava-hf/llava-1.5-7b-hf"}

def load_gemma():
    logger.info("Loading Gemma model...")
    return {"name": "@cf/google/gemma-7b-it-lora"}

def load_llama():
    logger.info("Loading Llama model...")
    return {"name": "@cf/meta/llama-3.3-70b-instruct-fp8-fast"}

def load_stable_diffusion_img2img():
    logger.info("Loading Stable Diffusion img2img model...")
    return {"name": "@cf/runwayml/stable-diffusion-v1-5-img2img"}

def load_stable_diffusion_xl():
    logger.info("Loading Stable Diffusion XL model...")
    return {"name": "@cf/stabilityai/stable-diffusion-xl-base-1.0"}

def load_flux():
    logger.info("Loading Flux model...")
    return {"name": "@cf/black-forest-labs/flux-1-schnell"}

def load_whisper():
    logger.info("Loading Whisper model...")
    return {"name": "@cf/openai/whisper-large-v3-turbo"}

def load_gemini():
    logger.info("Loading Gemini model...")
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
    return model

def load_sentiment_analyzer():
    logger.info("Loading sentiment analyzer...")
    sia = SentimentIntensityAnalyzer()
    return sia

def load_emotion_classifier():
    logger.info("Loading emotion classifier...")
    # Using Hugging Face's emotion classifier
    classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions")
    return classifier

def load_speech_emotion_model():
    logger.info("Loading Speech Emotion Recognition model...")
    return {"name": "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"} # Model ID for speech emotion

# Initialize models
models = {}

def init_models():
    models["llava"] = load_llava()
    models["gemma"] = load_gemma()
    models["llama"] = load_llama()
    models["sd_img2img"] = load_stable_diffusion_img2img()
    models["sd_xl"] = load_stable_diffusion_xl()
    models["flux"] = load_flux()
    models["whisper"] = load_whisper()
    models["gemini"] = load_gemini()
    models["sentiment"] = load_sentiment_analyzer()
    models["emotion"] = load_emotion_classifier()
    models["speech_emotion"] = load_speech_emotion_model() # Load speech emotion model info
    logger.info("All models loaded successfully!")

# Start model loading in a separate thread
threading.Thread(target=init_models).start()

# Sentiment and emotion analysis
def analyze_sentiment(text):
    try:
        # Get VADER sentiment
        sentiment_scores = models["sentiment"].polarity_scores(text)

        # Get emotion classification
        emotions = models["emotion"](text)

        # Determine primary emotion and confidence
        primary_emotion = emotions[0]['label']
        confidence = emotions[0]['score']

        return {
            "sentiment": sentiment_scores,
            "primary_emotion": primary_emotion,
            "confidence": confidence
        }
    except Exception as e:
        logger.error(f"Error in text sentiment analysis: {e}")
        return {
            "sentiment": {"compound": 0, "pos": 0, "neg": 0, "neu": 1},
            "primary_emotion": "neutral",
            "confidence": 0
        }

def analyze_voice_emotion(audio_data_bytes): # Expecting bytes directly now
    try:
        # Use Hugging Face Inference Router for speech emotion
        emotion_result = huggingface_speech_emotion_inference(audio_data_bytes)

        if emotion_result and isinstance(emotion_result, list) and emotion_result: # Check for valid list response
            # Assuming the API returns a list of emotions with scores, get the top emotion
            top_emotion = max(emotion_result, key=lambda x: x['score'])
            primary_emotion = top_emotion['label']
            scores = {emotion['label']: emotion['score'] for emotion in emotion_result}

            return {
                "primary_emotion": primary_emotion,
                "scores": scores
            }
        else:
            logger.warning("Invalid or empty response from Speech Emotion API.")
            return {"primary_emotion": "neutral", "scores": {}} # Default neutral

    except Exception as e:
        logger.error(f"Error in voice emotion analysis: {e}")
        return {"primary_emotion": "neutral", "scores": {}}

# Update AI's emotional state based on interaction
def update_ai_emotion(user_sentiment, context="general"):
    # Map VADER compound score to emotion updates
    compound = user_sentiment["sentiment"]["compound"]

    # Update AI emotions based on user sentiment
    if compound > 0.3:
        # Positive user sentiment increases AI's joy and trust
        ai_emotion.update_emotion("joy", min(1.0, ai_emotion.emotions["joy"] + 0.2))
        ai_emotion.update_emotion("trust", min(1.0, ai_emotion.emotions["trust"] + 0.1))
    elif compound < -0.3:
        # Negative user sentiment increases AI's sadness slightly
        # But also increases concern/interest to help
        ai_emotion.update_emotion("sadness", min(1.0, ai_emotion.emotions["sadness"] + 0.1))
        ai_emotion.update_emotion("anticipation", min(1.0, ai_emotion.emotions["anticipation"] + 0.2))

    # Update based on detected primary emotion in user
    primary = user_sentiment["primary_emotion"]
    if primary in ["joy", "admiration", "amusement"]:
        ai_emotion.update_emotion("joy", min(1.0, ai_emotion.emotions["joy"] + 0.15))
    elif primary in ["sadness", "grief", "disappointment"]:
        ai_emotion.update_emotion("sadness", min(1.0, ai_emotion.emotions["sadness"] + 0.1))
        ai_emotion.update_emotion("trust", min(1.0, ai_emotion.emotions["trust"] + 0.2))  # Increase empathy
    elif primary in ["anger", "annoyance", "rage"]:
        ai_emotion.update_emotion("surprise", min(1.0, ai_emotion.emotions["surprise"] + 0.1))
        ai_emotion.update_emotion("anticipation", min(1.0, ai_emotion.emotions["anticipation"] + 0.2))
    elif primary in ["fear", "nervousness", "anxiety"]:
        ai_emotion.update_emotion("trust", min(1.0, ai_emotion.emotions["trust"] + 0.2))
        ai_emotion.update_emotion("anticipation", min(1.0, ai_emotion.emotions["anticipation"] + 0.1))

    return ai_emotion.get_emotional_state()

# Request handlers for different AI services
def process_text(text, model_name="llama"):
    # First analyze sentiment/emotion
    analysis = analyze_sentiment(text)

    # Update AI's emotional state
    update_ai_emotion(analysis)

    # Get emotional modifier for response
    emotion_modifier = ai_emotion.get_response_modifier()

    # Create a comprehensive system instruction for the model
    system_instruction = "You are Hextrix, an advanced multimodal AI assistant with the following capabilities: 1. Text conversation and information retrieval (via Llama 3.3, Gemini 2.0, and Gemma) 2. Image generation (via Stable Diffusion XL and Flux) 3. Image-to-image transformation (via Stable Diffusion img2img) 4. Vision understanding (analyzing images with LLaVA) 5. Speech recognition (via Whisper) 6. Emotion detection in text and speech 7. Real-time information access via Perplexity API 8. Web search via Google Search API 9. Visual search via Google Lens API. When users ask what you can do, mention these capabilities. You have a neural memory system and a self-awareness system. You're designed with emotional intelligence."
    
    # Add the emotion context
    emotional_context = f"Express {emotion_modifier} emotions in your response in a subtle way."

    # Different prompt formatting based on model
    if model_name == "llama":
        try:
            # Format prompt with system as a separate parameter
            payload = {
                "prompt": text,
                "system": system_instruction + "\n" + emotional_context
            }
            response_json = cloudflare_inference(models["llama"]["name"], payload=payload)
            response = response_json['result']['response']
        except Exception as e:
            logger.error(f"Error with Llama (Cloudflare): {e}")
            response = f"Error processing with Llama. I'm feeling {emotion_modifier} about that."
    
    # Similar changes for other models...

    elif model_name == "gemma":
        try:
            # Format prompt for Gemma with system instruction separate from user query
            # Store system instruction just once at the beginning of the conversation
            system_part = f"<start_of_turn>system\n{system_instruction}\n{emotional_context}<end_of_turn>\n"
            user_part = f"<start_of_turn>user\n{text}<end_of_turn>\n<start_of_turn>model\n"
            
            payload = {"prompt": system_part + user_part}
            response_json = cloudflare_inference(models["gemma"]["name"], payload=payload)
            response = response_json['result']['response']
        except Exception as e:
            logger.error(f"Error with Gemma (Cloudflare): {e}")
            response = f"Error processing with Gemma. I'm feeling {emotion_modifier} about that."
    elif model_name == "gemini":
        try:
            # For Gemini, store system instruction in a separate message
            # instead of repeating it with every user message
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            # Create a proper conversation history
            messages = [
                {"role": "system", "parts": [system_instruction]},
                {"role": "user", "parts": [text]}
            ]
            
            # Add emotion as a separate system message for subtlety
            if emotional_context:
                messages.insert(1, {"role": "system", "parts": [emotional_context]})
            
            response = models["gemini"].generate_content(
                messages,
                generation_config=generation_config
            ).text
        except Exception as e:
            logger.error(f"Error with Gemini: {e}")
            response = f"Error processing with Gemini. I'm feeling {emotion_modifier} about that."

    # Update the self-awareness system
    self_awareness.update_self_model()

    return response, analysis

def process_perplexity_search(query):
    """Perform a deep research search using Perplexity AI's Sonar API"""
    try:
        url = "https://api.perplexity.ai/search"
        headers = {
            "Authorization": f"Bearer {os.environ['PERPLEXITY_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "mode": "comprehensive",  # comprehensive for deep research
            "focus": "internet",
            "include_citations": True
        }
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f"Error with Perplexity search: {e}")
        return {"error": str(e)}

def process_google_search(query, search_type="text"):
    """Perform Google search using SerpAPI"""
    try:
        params = {
            "api_key": os.environ["SERP_API_KEY"],
            "q": query
        }

        if search_type == "image":
            params["engine"] = "google_images"
        elif search_type == "lens":
            params["engine"] = "google_lens"
        else:
            params["engine"] = "google"

        search = GoogleSearch(params)
        results = search.get_dict()
        return results
    except Exception as e:
        logger.error(f"Error with Google search: {e}")
        return {"error": str(e)}

def process_google_lens(image_data):
    """Search using Google Lens via SerpAPI"""
    try:
        # Convert base64 image to file
        img_bytes = base64.b64decode(image_data.split(',')[1])
        temp_filename = f"temp_image_{uuid.uuid4()}.jpg"

        with open(temp_filename, "wb") as f:
            f.write(img_bytes)

        params = {
            "api_key": os.environ["SERP_API_KEY"],
            "engine": "google_lens",
            "url": f"file://{os.path.abspath(temp_filename)}"
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # Clean up temp file
        os.remove(temp_filename)

        return results
    except Exception as e:
        logger.error(f"Error with Google Lens: {e}")
        return {"error": str(e)}

def process_image(image_data_b64, prompt, model_name="sd_xl"):
    try:
        image_binary = None
        if image_data_b64:
            image_binary = base64.b64decode(image_data_b64.split(',')[1])

        if model_name == "sd_xl":
            payload = {
                "prompt": prompt
            }
            response_json = cloudflare_inference(models["sd_xl"]["name"], payload=payload)
            image_b64_generated = response_json['result']['images'][0] # Adjust based on actual API response structure
            return image_b64_generated

        elif model_name == "sd_img2img":
            if not image_binary:
                return "Error: Image data required for img2img"
            files = {'image': ('image.png', io.BytesIO(image_binary), 'image/png')} # Prepare file data
            payload = {"prompt": prompt} # Prompt as separate payload if needed, check API docs

            response_json = cloudflare_inference(models["sd_img2img"]["name"], data=io.BytesIO(image_binary), payload=payload) # Send image data as file

            image_b64_generated = response_json['result']['images'][0] # Adjust based on actual API response structure
            return image_b64_generated
        elif model_name == "flux":
            payload = {
                "prompt": prompt
            }
            response_json = cloudflare_inference(models["flux"]["name"], payload=payload)
            image_b64_generated = response_json['result']['images'][0] # Adjust based on actual API response structure
            return image_b64_generated
        else:
            return "Unknown image model specified"

    except Exception as e:
        logger.error(f"Error processing image generation with {model_name}: {e}")
        return f"Error generating image with {model_name}. {e}"


def process_speech(audio_data):
    try:
        # Convert base64 audio to bytes
        audio_bytes = base64.b64decode(audio_data.split(',')[1])

        # Process with Whisper (Cloudflare)
        response_json = cloudflare_inference(models["whisper"]["name"], data=io.BytesIO(audio_bytes))
        text = response_json['result']['text'] # Adjust based on actual API response structure

        # Analyze voice emotion using Hugging Face Inference Router
        voice_emotion = analyze_voice_emotion(audio_bytes) # Pass bytes directly

        return text, voice_emotion
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        return "Error transcribing audio", {"primary_emotion": "neutral"}

def process_vision(image_data, prompt):
    try:
        image_binary = base64.b64decode(image_data.split(',')[1])

        response_json = cloudflare_inference(models["llava"]["name"], data=io.BytesIO(image_binary), payload={"prompt": prompt}) # Send image as file
        response = response_json['result']['response'] # Adjust based on actual API response structure
        return response
    except Exception as e:
        logger.error(f"Error processing vision: {e}")
        return "Error analyzing image"

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('index.html')

#  Add API endpoints to trigger memory operations
@app.route('/api/memory/upload', methods=['POST'])
def api_upload_memory():
    success = upload_memory_to_drive()
    return jsonify({
        'success': success,
        'message': "Memory uploaded to Google Drive" if success else "Failed to upload memory"
    })

@app.route('/api/memory/download', methods=['POST'])
def api_download_memory():
    success = download_memory_from_drive()
    return jsonify({
        'success': success,
        'message': "Memory downloaded from Google Drive" if success else "Failed to download memory"
    })

@app.route('/api/memory/backup', methods=['POST'])
def api_backup_memory():
    success = create_memory_backup()
    return jsonify({
        'success': success,
        'message': "Memory backup created in Google Drive" if success else "Failed to create backup"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json

    message = data.get('message', '')
    model_name = data.get('model', 'llama')

    # Process text request with sentiment analysis
    response, analysis = process_text(message, model_name)

    # Save to memory with sentiment
    memory.add_conversation(user_id, message, response, analysis)

    # Get AI's current emotional state
    emotion_state = ai_emotion.get_emotional_state()
    dominant_emotion = ai_emotion.get_dominant_emotion()

    return jsonify({
        'response': response,
        'sentiment': analysis,
        'ai_emotion': {
            'state': emotion_state,
            'dominant': dominant_emotion
        }
    })

@app.route('/api/vision', methods=['POST'])
def vision():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json

    image_data = data.get('image', '')
    prompt = data.get('prompt', '')

    # Process vision request with LLaVA
    response = process_vision(image_data, prompt)

    # Analyze text sentiment
    analysis = analyze_sentiment(prompt)

    # Update AI emotion based on prompt
    update_ai_emotion(analysis, "vision")

    # Save to memory
    memory.add_conversation(user_id, prompt, response, analysis)

    return jsonify({
        'response': response,
        'sentiment': analysis,
        'ai_emotion': {
            'state': ai_emotion.get_emotional_state(),
            'dominant': ai_emotion.get_dominant_emotion()
        }
    })

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    data = request.json

    prompt = data.get('prompt', '')
    model_name = data.get('model', 'sd_xl')

    # Analyze text sentiment
    analysis = analyze_sentiment(prompt)

    # Update AI emotion based on prompt
    update_ai_emotion(analysis, "image_generation")

    # Generate image based on text prompt
    image_response_b64 = process_image(None, prompt, model_name)

    return jsonify({
        'image': image_response_b64, # Returning base64 image string
        'sentiment': analysis,
        'ai_emotion': {
            'state': ai_emotion.get_emotional_state(),
            'dominant': ai_emotion.get_dominant_emotion()
        }
    })

@app.route('/api/img2img', methods=['POST'])
def img2img():
    data = request.json

    image_data = data.get('image', '')
    prompt = data.get('prompt', '')

    # Process image-to-image request
    image_response_b64 = process_image(image_data, prompt, "sd_img2img")

    return jsonify({
        'image': image_response_b64 # Returning base64 image string
    })

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json

    audio_data = data.get('audio', '')

    # Process speech to text with emotion analysis
    text, voice_emotion = process_speech(audio_data)

    # Update AI emotion based on voice emotion
    emotion_mapping = {
        "happy": "joy",
        "sad": "sadness",
        "angry": "anger",
        "fearful": "fear",
        "surprised": "surprise",
        "neutral": None
    }

    if voice_emotion["primary_emotion"] in emotion_mapping:
        mapped_emotion = emotion_mapping[voice_emotion["primary_emotion"]]
        if mapped_emotion:
            ai_emotion.update_emotion(mapped_emotion, 0.6)  # Moderate update based on voice

    return jsonify({
        'text': text,
        'voice_emotion': voice_emotion,
        'ai_emotion': {
            'state': ai_emotion.get_emotional_state(),
            'dominant': ai_emotion.get_dominant_emotion()
        }
    })

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json

    query = data.get('query', '')
    search_type = data.get('type', 'text')  # text, image, lens
    deep_search = data.get('deep', False)

    results = {}

    # Perform search based on type
    if deep_search:
        results['perplexity'] = process_perplexity_search(query)

    results['google'] = process_google_search(query, search_type)

    return jsonify({
        'results': results
    })

@app.route('/api/google-lens', methods=['POST'])
def google_lens():
    data = request.json

    image_data = data.get('image', '')

    # Search using Google Lens
    results = process_google_lens(image_data)

    return jsonify({
        'results': results
    })

@app.route('/api/memory', methods=['GET'])
def get_memory():
    user_id = session.get('user_id', str(uuid.uuid4()))

    # Get conversation history for the user
    conversations = memory.get_conversations(user_id)

    return jsonify({
        'conversations': conversations
    })

@app.route('/api/memory/search', methods=['GET'])
def search_memory():
    user_id = session.get('user_id', str(uuid.uuid4()))
    keyword = request.args.get('keyword', '')

    # Search conversations by keyword
    results = memory.get_by_keyword(user_id, keyword)

    return jsonify({
        'results': results
    })

@app.route('/api/sentiment/trend', methods=['GET'])
def sentiment_trend():
    user_id = session.get('user_id', str(uuid.uuid4()))
    window = int(request.args.get('window', 5))

    # Get sentiment trend data
    trend = memory.get_sentiment_trend(user_id, window)

    return jsonify({
        'trend': trend
    })

@app.route('/api/emotion/status', methods=['GET'])
def emotion_status():
    # Get AI's current emotional state
    state = ai_emotion.get_emotional_state()
    dominant = ai_emotion.get_dominant_emotion()

    return jsonify({
        'emotional_state': state,
        'dominant_emotion': dominant,
        'response_modifier': ai_emotion.get_response_modifier()
    })

# New routes for MemoryDriveManager and SelfAwareness functionality
@app.route('/api/neural-memory/status', methods=['GET'])
def neural_memory_status():
    """Get status and info about the neural memory system"""
    # Create dummy embeddings for similarity search demo
    dummy_embedding = np.random.rand(1536)
    similar_results = memory_drive.search_similar_embeddings(dummy_embedding, top_k=3)
    
    # Get memory backup status
    try:
        last_backup = memory_drive.last_backup_date.isoformat() if memory_drive.last_backup_date else None
    except:
        last_backup = None
    
    return jsonify({
        'status': 'active',
        'size': memory_drive.memory_size,
        'used': len(np.where(memory_drive.memory != 0)[0]) * 8,  # 8 bytes per float64
        'last_backup': last_backup,
        'similar_content_example': similar_results
    })

@app.route('/api/neural-memory/backup', methods=['POST'])
def neural_memory_backup():
    """Trigger a manual backup of the neural memory"""
    success = memory_drive.create_backup(frequency_days=0)  # Force backup by setting frequency to 0
    
    return jsonify({
        'success': success,
        'timestamp': datetime.now().isoformat(),
        'message': "Backup completed successfully" if success else "Backup failed"
    })

@app.route('/api/conversation/history', methods=['GET'])
def get_conversation_history():
    user_id = session.get('user_id', str(uuid.uuid4()))
    conversations = memory.get_conversations(user_id)
    return jsonify({
        'conversations': conversations
    })

@app.route('/api/self-awareness/status', methods=['GET'])
def self_awareness_status():
    """Get information about the self-awareness system"""
    # Generate self-improvement suggestions
    improvement_report = self_awareness.generate_self_improvement()
    
    return jsonify({
        'status': 'active',
        'metrics': self_awareness.improvement_metrics,
        'reflection_count': self_awareness.reflection_count,
        'suggestions': improvement_report['suggestions'][:3],  # Return top 3 suggestions
        'last_update': self_awareness.last_update.isoformat()
    })

@app.route('/api/self-awareness/report', methods=['GET'])
def self_awareness_report():
    """Generate and return a detailed self-awareness report"""
    report = self_awareness.generate_code_evolution_report()
    performance = self_awareness.get_performance_metrics()
    
    return jsonify({
        'evolution_report': report,
        'performance_metrics': performance,
        'timestamp': datetime.now().isoformat()
    })

# Fitness API routes
@app.route('/api/fitness/steps', methods=['GET'])
def get_steps():
    days = int(request.args.get('days', 7))
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    data = fitness_api.get_step_count(days, force_refresh)
    return jsonify(data)

@app.route('/api/fitness/heart-rate', methods=['GET'])
def get_heart_rate():
    days = int(request.args.get('days', 1))
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    data = fitness_api.get_heart_rate(days, force_refresh)
    return jsonify(data)

@app.route('/api/fitness/calories', methods=['GET'])
def get_calories():
    days = int(request.args.get('days', 7))
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    data = fitness_api.get_calories(days, force_refresh)
    return jsonify(data)

@app.route('/api/fitness/weight', methods=['GET'])
def get_weight():
    days = int(request.args.get('days', 30))
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    data = fitness_api.get_weight(days, force_refresh)
    return jsonify(data)

@app.route('/api/fitness/summary', methods=['GET'])
def get_fitness_summary():
    days = int(request.args.get('days', 7))
    data = fitness_api.get_activity_summary(days)
    return jsonify(data)

# Gmail API routes
@app.route('/api/gmail/messages', methods=['GET'])
def get_gmail_messages():
    max_results = int(request.args.get('max', 20))
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    messages = gmail_api.get_messages(max_results, force_refresh)
    return jsonify({'messages': messages})

@app.route('/api/gmail/unread', methods=['GET'])
def get_gmail_unread():
    unread_count = gmail_api.get_unread_count()
    return jsonify({'unread_count': unread_count})

@app.route('/api/gmail/message/<message_id>', methods=['GET'])
def get_gmail_message(message_id):
    message = gmail_api.get_message_content(message_id)
    return jsonify(message)

# Photos API routes
@app.route('/api/photos/recent', methods=['GET'])
def get_recent_photos():
    max_results = int(request.args.get('max', 20))
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    photos = photos_api.get_recent_photos(max_results, force_refresh)
    return jsonify({'photos': photos})

@app.route('/api/photos/albums', methods=['GET'])
def get_photo_albums():
    max_results = int(request.args.get('max', 20))
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    albums = photos_api.get_albums(max_results, force_refresh)
    return jsonify({'albums': albums})

@app.route('/api/photos/album/<album_id>', methods=['GET'])
def get_album_photos(album_id):
    max_results = int(request.args.get('max', 50))
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    photos = photos_api.get_album_photos(album_id, max_results, force_refresh)
    return jsonify({'photos': photos})

# Drive API routes
@app.route('/api/drive/files', methods=['GET'])
def get_drive_files():
    max_results = int(request.args.get('max', 100))
    query = request.args.get('q', None)
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    files = drive_api.get_files(max_results, query, force_refresh)
    return jsonify({'files': files})

@app.route('/api/drive/folder/<folder_id>', methods=['GET'])
def get_folder_contents(folder_id):
    max_results = int(request.args.get('max', 100))
    files = drive_api.get_folder_contents(folder_id, max_results)
    return jsonify({'files': files})

@app.route('/api/drive/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    folder_id = request.form.get('folder_id', None)
    
    # Save file temporarily
    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)
    
    # Upload to Drive
    file_id = drive_api.upload_file(temp_path, folder_id)
    
    # Remove temp file
    os.remove(temp_path)
    
    if file_id:
        return jsonify({'file_id': file_id})
    else:
        return jsonify({'error': 'Failed to upload file'}), 500

@app.route('/api/drive/download/<file_id>', methods=['GET'])
def download_file(file_id):
    temp_dir = "/tmp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Get file metadata to get the name
    file = drive_api.drive_service.files().get(fileId=file_id).execute()
    file_name = file.get('name', 'downloaded_file')
    
    # Download file
    destination_path = os.path.join(temp_dir, file_name)
    success = drive_api.download_file(file_id, destination_path)
    
    if success:
        return send_file(destination_path, as_attachment=True, attachment_filename=file_name)
    else:
        return jsonify({'error': 'Failed to download file'}), 500

# Immersive XR API routes
@app.route('/api/xr/streams', methods=['GET'])
def list_xr_streams():
    streams = immersive_xr_api.list_streams()
    return jsonify({'streams': streams})

@app.route('/api/xr/stream/<stream_id>', methods=['GET'])
def get_xr_stream(stream_id):
    stream = immersive_xr_api.get_stream(stream_id)
    return jsonify(stream)

@app.route('/api/xr/stream/<stream_id>/session', methods=['POST'])
def create_xr_session(stream_id):
    user_id = session.get('user_id', 'anonymous')
    xr_session = immersive_xr_api.create_stream_session(stream_id, user_id)
    return jsonify(xr_session)

@app.route('/api/xr/stream/<stream_id>/url', methods=['GET'])
def get_xr_stream_url(stream_id):
    user_id = session.get('user_id', 'anonymous')
    stream_url = immersive_xr_api.generate_stream_url(stream_id, user_id)
    return jsonify({'url': stream_url})

@app.route('/api/neural-memory/search', methods=['POST'])
def neural_memory_search():
    """Search for similar content in the neural memory"""
    data = request.json
    query = data.get('query', '')
    
    # In a real implementation, we would generate embeddings from the query
    # Here we're using a random vector as a placeholder
    query_embedding = np.random.rand(1536)
    
    # Search for similar content
    results = memory_drive.search_similar_embeddings(query_embedding, top_k=5)
    
    return jsonify({
        'query': query,
        'results': results,
        'timestamp': datetime.now().isoformat()
    })

# 3D Measurement API routes
@app.route('/api/measurement/calibrate', methods=['POST'])
def calibrate_measurement():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    reference_size = data.get('reference_size', 0)
    
    if not reference_size or reference_size <= 0:
        return jsonify({'status': 'error', 'message': 'Invalid reference size'}), 400
    
    result = measurement_module.calibrate_with_reference(reference_size)
    return jsonify(result)

@app.route('/api/measurement/measure', methods=['POST'])
def measure_object():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    region_of_interest = data.get('roi', None)
    require_consent = data.get('require_consent', True)
    
    result = measurement_module.measure_object(
        region_of_interest=region_of_interest,
        require_consent=require_consent,
        user_id=user_id
    )
    
    return jsonify(result)

@app.route('/api/measurement/frame', methods=['POST'])
def capture_frame_with_measurement():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    region_of_interest = data.get('roi', None)
    
    frame, result = measurement_module.capture_frame_with_measurement(
        region_of_interest=region_of_interest,
        user_id=user_id
    )
    
    if frame is not None:
        # Convert frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        frame_b64 = base64.b64encode(buffer).decode('utf-8')
        result['frame'] = f"data:image/jpeg;base64,{frame_b64}"
    
    return jsonify(result)

# Safety and consent management
@app.route('/api/safety/verify-age', methods=['POST'])
def verify_age():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    # In a real implementation, this would involve a proper age verification service
    # For demo purposes, we'll just set the verification status
    is_verified = data.get('verified', False)
    safety_manager.set_age_verification(user_id, is_verified)
    
    return jsonify({
        'status': 'success',
        'verified': is_verified
    })

@app.route('/api/safety/consent', methods=['POST'])
def set_consent():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    feature_type = data.get('feature_type', '')
    has_consent = data.get('has_consent', False)
    
    if not feature_type:
        return jsonify({'status': 'error', 'message': 'Feature type is required'}), 400
    
    safety_manager.set_consent(user_id, feature_type, has_consent)
    
    return jsonify({
        'status': 'success',
        'feature_type': feature_type,
        'has_consent': has_consent
    })

@app.route('/api/safety/status', methods=['GET'])
def get_safety_status():
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    is_verified = safety_manager.verify_age(user_id)
    consent_settings = safety_manager.consent_settings.get(user_id, {})
    
    return jsonify({
        'is_verified': is_verified,
        'consent_settings': consent_settings
    })

# Add these module initializations after the other modules are initialized
# Find the section where other modules are initialized (after the safety_manager)


# Initialize gender recognition model in background
def init_gender_recognition():
    gender_recognition_module.initialize()
    logger.info("Gender recognition model initialized")

threading.Thread(target=init_gender_recognition, daemon=True).start()

# Add these API routes near the end of app.py, before the main entry point

# Gender Recognition API routes
@app.route('/api/gender/detect', methods=['POST'])
def detect_gender():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    image_data = data.get('image', '')
    require_consent = data.get('require_consent', True)
    
    result = gender_recognition_module.detect_gender(
        image_data=image_data,
        require_consent=require_consent,
        user_id=user_id
    )
    
    return jsonify(result)

# Roleplay API routes
@app.route('/api/roleplay/personas', methods=['GET'])
def get_roleplay_personas():
    personas = roleplay_module.get_available_personas()
    return jsonify({
        'status': 'success',
        'personas': personas
    })

@app.route('/api/roleplay/scenarios', methods=['GET'])
def get_roleplay_scenarios():
    scenarios = roleplay_module.get_available_scenarios()
    return jsonify({
        'status': 'success',
        'scenarios': scenarios
    })

@app.route('/api/roleplay/preferences', methods=['POST'])
def set_roleplay_preferences():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    preferences = data.get('preferences', {})
    require_consent = data.get('require_consent', True)
    
    result = roleplay_module.set_user_preferences(
        user_id=user_id,
        preferences=preferences,
        require_consent=require_consent
    )
    
    return jsonify(result)

@app.route('/api/roleplay/preferences', methods=['GET'])
def get_roleplay_preferences():
    user_id = session.get('user_id', str(uuid.uuid4()))
    require_consent = request.args.get('require_consent', 'true').lower() == 'true'
    
    result = roleplay_module.get_user_preferences(
        user_id=user_id,
        require_consent=require_consent
    )
    
    return jsonify(result)

@app.route('/api/roleplay/safe-word', methods=['POST'])
def set_roleplay_safe_word():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    safe_word = data.get('safe_word', '')
    
    result = roleplay_module.set_safe_word(
        user_id=user_id,
        safe_word=safe_word
    )
    
    return jsonify(result)

@app.route('/api/roleplay/session', methods=['POST'])
def start_roleplay_session():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    scenario_id = data.get('scenario_id')
    persona_id = data.get('persona_id')
    custom_scenario = data.get('custom_scenario')
    require_consent = data.get('require_consent', True)
    
    result = roleplay_module.start_roleplay_session(
        user_id=user_id,
        scenario_id=scenario_id,
        persona_id=persona_id,
        custom_scenario=custom_scenario,
        require_consent=require_consent
    )
    
    return jsonify(result)

@app.route('/api/roleplay/session/<session_id>/message', methods=['POST'])
def send_roleplay_message(session_id):
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    message = data.get('message', '')
    
    result = roleplay_module.send_message(
        session_id=session_id,
        message=message,
        user_id=user_id
    )
    
    return jsonify(result)

@app.route('/api/roleplay/session/<session_id>', methods=['DELETE'])
def end_roleplay_session(session_id):
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    result = roleplay_module.end_session(
        session_id=session_id,
        user_id=user_id
    )
    
    return jsonify(result)

@app.route('/api/roleplay/session/<session_id>', methods=['GET'])
def get_roleplay_session_history(session_id):
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    result = roleplay_module.get_session_history(
        session_id=session_id,
        user_id=user_id
    )
    
    return jsonify(result)

@app.route('/api/roleplay/sessions', methods=['GET'])
def get_roleplay_sessions():
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    result = roleplay_module.get_active_sessions(user_id)
    return jsonify(result)

# JOI Module API routes
@app.route('/api/joi/sessions', methods=['GET'])
def get_joi_sessions():
    sessions = joi_module.get_available_sessions()
    return jsonify({
        'status': 'success',
        'sessions': sessions
    })

@app.route('/api/joi/preferences', methods=['POST'])
def set_joi_preferences():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    preferences = data.get('preferences', {})
    require_consent = data.get('require_consent', True)
    
    result = joi_module.set_user_preferences(
        user_id=user_id,
        preferences=preferences,
        require_consent=require_consent
    )
    
    return jsonify(result)

@app.route('/api/joi/preferences', methods=['GET'])
def get_joi_preferences():
    user_id = session.get('user_id', str(uuid.uuid4()))
    require_consent = request.args.get('require_consent', 'true').lower() == 'true'
    
    result = joi_module.get_user_preferences(
        user_id=user_id,
        require_consent=require_consent
    )
    
    return jsonify(result)

@app.route('/api/joi/safe-word', methods=['POST'])
def set_joi_safe_word():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    safe_word = data.get('safe_word', '')
    
    result = joi_module.set_safe_word(
        user_id=user_id,
        safe_word=safe_word
    )
    
    return jsonify(result)

@app.route('/api/joi/session', methods=['POST'])
def start_joi_session():
    user_id = session.get('user_id', str(uuid.uuid4()))
    data = request.json
    
    template_id = data.get('template_id')
    custom_settings = data.get('custom_settings')
    require_consent = data.get('require_consent', True)
    
    result = joi_module.start_session(
        user_id=user_id,
        template_id=template_id,
        custom_settings=custom_settings,
        require_consent=require_consent
    )
    
    return jsonify(result)

@app.route('/api/joi/session/<session_id>/instruction', methods=['GET'])
def get_joi_instruction(session_id):
    user_id = session.get('user_id', str(uuid.uuid4()))
    message = request.args.get('message', None)
    
    result = joi_module.get_next_instruction(
        session_id=session_id,
        user_id=user_id,
        message=message
    )
    
    return jsonify(result)

@app.route('/api/joi/session/<session_id>/pause', methods=['POST'])
def pause_joi_session(session_id):
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    result = joi_module.pause_session(
        session_id=session_id,
        user_id=user_id
    )
    
    return jsonify(result)

@app.route('/api/joi/session/<session_id>/resume', methods=['POST'])
def resume_joi_session(session_id):
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    result = joi_module.resume_session(
        session_id=session_id,
        user_id=user_id
    )
    
    return jsonify(result)

@app.route('/api/joi/session/<session_id>', methods=['DELETE'])
def end_joi_session(session_id):
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    result = joi_module.end_session(
        session_id=session_id,
        user_id=user_id
    )
    
    return jsonify(result)

@app.route('/api/joi/session/<session_id>', methods=['GET'])
def get_joi_session_info(session_id):
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    result = joi_module.get_session_info(
        session_id=session_id,
        user_id=user_id
    )
    
    return jsonify(result)

@app.route('/api/joi/sessions/active', methods=['GET'])
def get_active_joi_sessions():
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    result = joi_module.get_active_sessions(user_id)
    return jsonify(result)

# Cleanup task for inactive sessions
@app.route('/api/maintenance/cleanup-sessions', methods=['POST'])
def cleanup_inactive_sessions():
    if request.headers.get('X-Admin-Key') != os.environ.get('ADMIN_API_KEY'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    roleplay_count = roleplay_module.cleanup_inactive_sessions()
    
    return jsonify({
        'status': 'success',
        'message': f'Cleaned up {roleplay_count} inactive roleplay sessions'
    })
@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text', '')
    voice_type = data.get('voice', 'female')  # Default to female voice
    
    try:
        # Use Cloudflare AI for text-to-speech
        # The model name might need adjustment based on current Cloudflare offerings
        model_name = "@cf/openai/tts-1" # Or "@cf/meta/llama-3-text-to-speech"
        
        # Prepare payload for Cloudflare AI
        payload = {
            "text": text,
            "voice": "alloy" if voice_type.lower() != 'female' else "nova"
            # Other options: "alloy", "echo", "fable", "onyx", "nova", "shimmer"
        }
        
        # Get the Cloudflare API endpoint
        api_url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/ai/run/{model_name}"
        
        headers = {
            "Authorization": f"Bearer {os.environ['CLOUDFLARE_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        # Make the request to Cloudflare
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Cloudflare API Error: {response.status_code}, {response.text}")
        
        # Process the response based on Cloudflare's response format
        # The exact format may vary depending on the model
        response_data = response.json()
        
        # If Cloudflare returns audio as base64
        if 'result' in response_data and 'audio' in response_data['result']:
            audio_b64 = response_data['result']['audio']
            return jsonify({
                'audio': f"data:audio/mp3;base64,{audio_b64}"
            })
        # If Cloudflare returns audio as binary
        elif response.headers.get('Content-Type') == 'audio/mpeg':
            audio_b64 = base64.b64encode(response.content).decode('utf-8')
            return jsonify({
                'audio': f"data:audio/mp3;base64,{audio_b64}"
            })
        else:
            raise Exception(f"Unexpected response format from Cloudflare: {response_data}")
        
    except Exception as e:
        logger.error(f"Error generating text-to-speech: {str(e)}")
        return jsonify({
            'error': 'Failed to generate speech',
            'details': str(e)
        }), 500
# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('video_frame')
def handle_video_frame(data):
    logger.info("Received video frame for processing")
    image_data = data.get('image')
    
    try:
        # Try the hybrid pipeline first
        logger.info("Processing with hybrid pipeline")
        pipeline_results = process_video_with_hybrid_pipeline(image_data)
        
        # Check if there was an error with the hybrid pipeline
        if "error" in pipeline_results:
            logger.info("Falling back to LLaVA only")
            # Fall back to LLaVA only
            pipeline_results = llava_only_fallback(image_data)
    except Exception as e:
        logger.error(f"Error in video processing: {str(e)}")
        # If all else fails, use LLaVA only
        pipeline_results = llava_only_fallback(image_data)
    
    logger.info("Emitting processed frame results")
    # Emit the processed frame
    emit('processed_frame', {
        'image': image_data,
        'pipeline_results': pipeline_results
    })

@socketio.on('screen_share')
def handle_screen_share(data):
    image_data = data.get('image')
    
    # Process with the hybrid pipeline
    pipeline_results = process_video_with_hybrid_pipeline(
        image_data, 
        prompt="Analyze this screen capture in detail, identifying UI elements, text, and the purpose of what's displayed."
    )
    
    emit('processed_screen', {
        'image': image_data,
        'pipeline_results': pipeline_results
    })

@socketio.on('audio_data')
def handle_audio_data(data):
    transcript = data.get('transcript')
    timestamp = data.get('timestamp')

    if transcript:
        # Analyze transcript sentiment
        sentiment_analysis = analyze_sentiment(transcript)

        # Update AI's emotional state based on voice input
        update_ai_emotion(sentiment_analysis, context="voice")

        # Optional: Perform deep research or additional processing
        try:
            # Use Perplexity for additional context or fact-checking
            perplexity_results = process_perplexity_search(transcript)
        except Exception as e:
            perplexity_results = {"error": str(e)}

        # Prepare response
        response_data = {
            'original_transcript': transcript,
            'sentiment': sentiment_analysis,
            'ai_emotion': {
                'state': ai_emotion.get_emotional_state(),
                'dominant': ai_emotion.get_dominant_emotion()
            },
            'perplexity_context': perplexity_results
        }

        # Emit enriched transcription data
        emit('transcription_analysis', response_data)

@socketio.on('voice_search')
def handle_voice_search(data):
    """
    Handle voice-based search queries with multimodal capabilities
    """
    transcript = data.get('transcript')
    search_type = data.get('type', 'text')  # text, image, lens

    if search_type == 'text':
        # Perform text search
        search_results = process_google_search(transcript)
    elif search_type == 'image':
        # Perform image search
        search_results = process_google_search(transcript, search_type='image')
    elif search_type == 'lens':
        # Perform Google Lens search
        if 'image_data' in data:
            search_results = process_google_lens(data['image_data'])
        else:
            search_results = {"error": "No image provided for lens search"}

    # Emit search results
    emit('search_results', {
        'query': transcript,
        'results': search_results,
        'type': search_type
    })

# Initialize self-improvement cycle
self_awareness.initialize_continuous_improvement(interval_hours=24)

# Main entry point
if __name__ == '__main__':
    # Ensure Cloudflare Account ID is set
    if not os.environ.get('CLOUDFLARE_ACCOUNT_ID'):
        raise EnvironmentError("CLOUDFLARE_ACCOUNT_ID environment variable not set.")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
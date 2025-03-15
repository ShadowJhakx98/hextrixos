"""
immersive_xr_integration.py

Integration with Google's Immersive Stream for XR API
"""

import logging
import datetime
import json
import os
import requests
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

logger = logging.getLogger("ImmersiveXRIntegration")
logger.setLevel(logging.INFO)

class ImmersiveXRIntegration:
    def __init__(self, api_manager):
        """
        Initialize Immersive Stream for XR integration
        
        Args:
            api_manager: GoogleAPIManager instance
        """
        self.api_manager = api_manager
        
        # Get project ID from environment or fallback to a default for testing
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        
        # Add validation for project ID
        if not self.project_id:
            logger.warning("No Google Cloud project ID found in environment variables.")
            # You could set a default project ID here if needed
            # self.project_id = "your-default-project-id"
        
        self.location = "us-central1"  # Default location for ISXR
        self.api_endpoint = f"https://{self.location}-stream.googleapis.com/v1"
        self.session = None
        self.initialized = False  # Track initialization status
    
    def initialize(self):
        """Initialize the Immersive XR service"""
        try:
            # Get credentials
            creds = self.api_manager.get_credentials()
            
            # Create authorized session
            self.session = AuthorizedSession(creds)
            
            # Verify access
            test_response = self.session.get(f"{self.api_endpoint}/projects/{self.project_id}/locations/{self.location}/streams")
            if test_response.status_code != 200:
                logger.error(f"Failed to initialize Immersive XR service: {test_response.text}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Immersive XR service: {str(e)}")
            return False
    
    def list_streams(self):
        """List available XR streams in the project"""
        try:
            # Check if project ID is available
            if not self.project_id:
                logger.error("Cannot list streams: Project ID is missing")
                return []
                
            if not self.session:
                if not self.initialize():
                    return []
            
            response = self.session.get(f"{self.api_endpoint}/projects/{self.project_id}/locations/{self.location}/streams")
            
            if response.status_code == 200:
                return response.json().get('streams', [])
            else:
                logger.error(f"Error listing streams: {response.text}")
                return []
                    
        except Exception as e:
            logger.error(f"Error listing XR streams: {str(e)}")
            return []
    
    def get_stream(self, stream_id):
        """Get details of a specific XR stream"""
        try:
            if not self.session:
                if not self.initialize():
                    return None
            
            response = self.session.get(f"{self.api_endpoint}/projects/{self.project_id}/locations/{self.location}/streams/{stream_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting stream details: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting XR stream details: {str(e)}")
            return None
    
    def create_stream_session(self, stream_id, user_id=None):
        """Create a streaming session for a user"""
        try:
            if not self.session:
                if not self.initialize():
                    return None
            
            session_body = {
                "streamId": stream_id
            }
            
            # Add user ID if provided
            if user_id:
                session_body["userId"] = user_id
            
            response = self.session.post(
                f"{self.api_endpoint}/projects/{self.project_id}/locations/{self.location}/streamSessions",
                json=session_body
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error creating stream session: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating XR stream session: {str(e)}")
            return None
    
    def get_stream_session(self, session_id):
        """Get details of a specific stream session"""
        try:
            if not self.session:
                if not self.initialize():
                    return None
            
            response = self.session.get(f"{self.api_endpoint}/projects/{self.project_id}/locations/{self.location}/streamSessions/{session_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting session details: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting XR session details: {str(e)}")
            return None
    
    def end_stream_session(self, session_id):
        """End a streaming session"""
        try:
            if not self.session:
                if not self.initialize():
                    return False
            
            response = self.session.post(f"{self.api_endpoint}/projects/{self.project_id}/locations/{self.location}/streamSessions/{session_id}:end")
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Error ending stream session: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error ending XR session: {str(e)}")
            return False
    
    def generate_stream_url(self, stream_id, user_id=None, duration_seconds=3600):
        """Generate a URL for accessing a stream without creating a session"""
        try:
            # Create a session
            session = self.create_stream_session(stream_id, user_id)
            if not session:
                return None
            
            session_id = session.get('name', '').split('/')[-1]
            
            # Generate a streaming URL
            return f"https://{self.location}-stream.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/streamSessions/{session_id}/view"
            
        except Exception as e:
            logger.error(f"Error generating stream URL: {str(e)}")
            return None

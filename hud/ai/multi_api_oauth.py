"""
hextrix_oauth.py

Enhanced OAuth handler for multiple Google APIs that works in GitHub Codespaces
"""

import os
import json
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

class HextrixOAuth:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        
        # Define all required API scopes - UPDATED WITH COMPLETE PERMISSIONS
        self.scopes = [
            # Drive API for memory storage
            'https://www.googleapis.com/auth/drive',
            
            # Contacts API
            'https://www.googleapis.com/auth/contacts.readonly',
            
            # Fitness API - complete set
            'https://www.googleapis.com/auth/fitness.activity.read',
            'https://www.googleapis.com/auth/fitness.body.read',
            'https://www.googleapis.com/auth/fitness.heart_rate.read',
            'https://www.googleapis.com/auth/fitness.location.read',
            'https://www.googleapis.com/auth/fitness.nutrition.read',
            'https://www.googleapis.com/auth/fitness.blood_glucose.read',
            'https://www.googleapis.com/auth/fitness.blood_pressure.read',
            'https://www.googleapis.com/auth/fitness.body_temperature.read',
            'https://www.googleapis.com/auth/fitness.oxygen_saturation.read',
            'https://www.googleapis.com/auth/fitness.reproductive_health.read',
            'https://www.googleapis.com/auth/fitness.sleep.read',
            
            # Gmail API
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.metadata',
            
            # Google Photos API
            'https://www.googleapis.com/auth/photoslibrary.readonly',
            'https://www.googleapis.com/auth/photoslibrary.appendonly',
            
            # Immersive Stream for XR API (includes VR/AR capabilities)
            'https://www.googleapis.com/auth/cloud-platform'
        ]
        
        self.creds = None
        self.services = {}
    
    def get_credentials(self):
        """Get OAuth credentials, automatically refreshing if needed."""
        try:
            # Load existing token if present
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            
            # If credentials exist but are expired, try to refresh
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                # Save refreshed credentials
                with open(self.token_file, 'w') as token:
                    token.write(self.creds.to_json())
            
            # If no valid credentials, start new flow
            if not self.creds or not self.creds.valid:
                self._create_new_credentials()
            
            return self.creds
            
        except (RefreshError, Exception) as e:
            print(f"Error with credentials: {e}")
            # If refresh fails, try getting new credentials
            if os.path.exists(self.token_file):
                os.rename(self.token_file, f"{self.token_file}.bak")
            self._create_new_credentials()
            return self.creds
    
    def _create_new_credentials(self):
        """Create new credentials using device flow authentication."""
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
        
        print("\n" + "="*80)
        print("HEXTRIX OAUTH AUTHENTICATION".center(80))
        print("="*80)
        print("\nRequesting permissions for the following features:")
        print("- Google Drive (memory storage)")
        print("- Google Contacts (contacts panel)")
        print("- Google Fitness (biometrics panel)")
        print("- Gmail (messages panel)")
        print("- Google Photos (photo gallery panel)")
        print("- Immersive XR capabilities")
        print("\nStarting device authentication flow...\n")
        
        # Create a flow instance using client secrets file
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, 
            scopes=self.scopes
        )
        
        # Run the device flow authorization
        self.creds = flow.run_console()
        
        # Save the credentials for next run
        with open(self.token_file, 'w') as token:
            token.write(self.creds.to_json())
        
        print("\nAuthentication successful! Credentials saved to", self.token_file)
    
    def create_service(self, api_name, api_version):
        """Create an authorized Google API service."""
        creds = self.get_credentials()
        
        # Create and cache the service
        service_key = f"{api_name}_{api_version}"
        if service_key not in self.services:
            self.services[service_key] = build(api_name, api_version, credentials=creds)
        
        return self.services[service_key]
    
    def get_drive_service(self):
        """Create an authorized Google Drive service."""
        return self.create_service('drive', 'v3')
    
    def get_contacts_service(self):
        """Create an authorized Google Contacts service."""
        return self.create_service('people', 'v1')
    
    def get_fitness_service(self):
        """Create an authorized Google Fitness service."""
        return self.create_service('fitness', 'v1')
    
    def get_gmail_service(self):
        """Create an authorized Gmail service."""
        return self.create_service('gmail', 'v1')
    
def get_photos_service(self):
    """Create an authorized Google Photos service."""
    creds = self.get_credentials()
    
    try:
        # Direct build approach
        return build('photoslibrary', 'v1', credentials=creds, 
                    discoveryServiceUrl='https://photoslibrary.googleapis.com/$discovery/rest?version=v1')
    except Exception as e:
        print(f"Error building Photos API client: {str(e)}")
        
        # Fallback approach using static discovery
        try:
            # If direct service URL fails, try alternate approach
            from googleapiclient.discovery import build_from_document
            import requests
            
            # Fetch the discovery document
            r = requests.get('https://photoslibrary.googleapis.com/$discovery/rest?version=v1')
            if r.status_code == 200:
                service = build_from_document(r.text, credentials=creds)
                return service
            else:
                print(f"Failed to fetch Photos API discovery document: {r.status_code}")
                return None
        except Exception as inner_e:
            print(f"Error in fallback Photos API initialization: {str(inner_e)}")
            return None
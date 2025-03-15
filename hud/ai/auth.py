# Google API Authentication Setup for Hextrix

# 1. Create OAuth credentials
# - Go to Google Cloud Console: https://console.cloud.google.com/
# - Create a new project (or use an existing one)
# - Go to "APIs & Services" > "Credentials"
# - Click "Create Credentials" > "OAuth client ID"
# - Application type: "Desktop application"
# - Name: "Hextrix API Access"
# - Download the JSON file and rename it to "credentials.json"
# - Place credentials.json in your project root
# - Enable these APIs in the Google Cloud Console:
#   * Google Drive API
#   * Gmail API
#   * Google Photos Library API
#   * Fitness API
#   * People API (for Contacts)
#   * Immersive Stream for XR API

# 2. Install necessary packages if not already installed
# pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# 3. First-time authorization script (run this once)
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.discovery_cache.base import Cache
import os
import json

# Complete updated scopes list with all necessary permissions:
SCOPES = [
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
# Simple in-memory cache
class MemoryCache(Cache):
    _CACHE = {}
    def get(self, url):
        return MemoryCache._CACHE.get(url)
    def set(self, url, content):
        MemoryCache._CACHE[url] = content

def authorize_google_apis(credentials_path=None):
    """
    Authorize all Google APIs used by Hextrix and return service objects.
    
    Args:
        credentials_path (str, optional): Path to the credentials.json file. Defaults to None.
    
    Returns:
        dict: Dictionary of service objects for each API
    """
    creds = None
    # Use provided credentials path or default
    credentials_file = credentials_path if credentials_path else 'credentials.json'
    token_file = os.path.join(os.path.dirname(credentials_file), 'token.json')
    temp_credentials_file = None
    
    # Load the credentials file to check its structure
    try:
        with open(credentials_file, 'r') as f:
            credentials_data = json.load(f)
        
        # Check if this is the new format with nested structure
        if 'oauth' in credentials_data:
            # Create a temporary credentials file with just the OAuth part
            temp_credentials_file = os.path.join(os.path.dirname(credentials_file), 'temp_credentials.json')
            with open(temp_credentials_file, 'w') as f:
                json.dump(credentials_data['oauth'], f)
            credentials_file = temp_credentials_file
    except Exception as e:
        print(f"Error processing credentials file: {e}")
        return {}
    
    try:
        # The token.json file stores the user's access and refresh tokens
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        # If no valid credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Create service objects for each API
        services = {}
        
        # Drive API
        services['drive'] = build('drive', 'v3', credentials=creds)
        
        # Gmail API
        services['gmail'] = build('gmail', 'v1', credentials=creds)
        
        # Google Photos API
        # Get absolute path to the discovery document
        discovery_file_path = os.path.abspath('photoslibrary_v1.json')
        # Convert to a proper file URL (replace backslashes with forward slashes for Windows compatibility)
        discovery_url = f'file:///{discovery_file_path.replace("\\", "/")}'
    
        # Fitness API
        services['fitness'] = build('fitness', 'v1', credentials=creds)
        
        # People API (Contacts)
        services['people'] = build('people', 'v1', credentials=creds)
        
        print("Google APIs authorization successful!")
        return services
    finally:
        # Clean up the temporary credentials file if it was created
        if temp_credentials_file and os.path.exists(temp_credentials_file):
            try:
                os.remove(temp_credentials_file)
            except:
                pass

def test_drive_api(drive_service):
    """Test the Drive API connection"""
    try:
        results = drive_service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('Drive API: No files found.')
        else:
            print('Drive API: Successfully retrieved file list.')
            print(f'Drive API: Found {len(items)} files.')
    except Exception as e:
        print(f'Drive API: Error testing connection - {str(e)}')

def test_gmail_api(gmail_service):
    """Test the Gmail API connection"""
    try:
        results = gmail_service.users().messages().list(userId='me', maxResults=1).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print('Gmail API: No messages found.')
        else:
            print('Gmail API: Successfully retrieved messages list.')
            print(f'Gmail API: Found messages in inbox.')
    except Exception as e:
        print(f'Gmail API: Error testing connection - {str(e)}')

def test_photos_api(photos_service):
    """Test the Photos API connection"""
    try:
        results = photos_service.mediaItems().list(pageSize=1).execute()
        items = results.get('mediaItems', [])
        
        if not items:
            print('Photos API: No photos found.')
        else:
            print('Photos API: Successfully retrieved photos list.')
            print(f'Photos API: Found photos in library.')
    except Exception as e:
        print(f'Photos API: Error testing connection - {str(e)}')

def test_fitness_api(fitness_service):
    """Test the Fitness API connection"""
    try:
        import datetime
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(days=1)
        
        end_time_millis = int(end_time.timestamp() * 1000)
        start_time_millis = int(start_time.timestamp() * 1000)
        
        data_source = 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps'
        
        body = {
            "aggregateBy": [{
                "dataTypeName": data_source
            }],
            "bucketByTime": {"durationMillis": 86400000},  # Daily buckets
            "startTimeMillis": start_time_millis,
            "endTimeMillis": end_time_millis
        }
        
        fitness_service.users().dataset().aggregate(userId="me", body=body).execute()
        print('Fitness API: Successfully connected to fitness data.')
    except Exception as e:
        print(f'Fitness API: Error testing connection - {str(e)}')

def test_people_api(people_service):
    """Test the People API connection"""
    try:
        results = people_service.people().connections().list(
            resourceName='people/me',
            pageSize=1,
            personFields='names,emailAddresses').execute()
        connections = results.get('connections', [])
        
        if not connections:
            print('People API: No contacts found.')
        else:
            print('People API: Successfully retrieved contacts list.')
            print(f'People API: Found contacts.')
    except Exception as e:
        print(f'People API: Error testing connection - {str(e)}')

def test_all_apis(services):
    """Test all API connections"""
    print("\nTesting API Connections:")
    print("------------------------")
    
    # Test Drive API
    if 'drive' in services:
        test_drive_api(services['drive'])
    
    # Test Gmail API
    if 'gmail' in services:
        test_gmail_api(services['gmail'])
    
    # Test Photos API
    if 'photos' in services:
        test_photos_api(services['photos'])
    
    # Test Fitness API
    if 'fitness' in services:
        test_fitness_api(services['fitness'])
    
    # Test People API
    if 'people' in services:
        test_people_api(services['people'])
    
    print("------------------------")
# Add this debug code to your auth.py or app.py to verify credentials and scopes
def debug_auth():
    try:
        print("Checking for token.json...")
        if os.path.exists('token.json'):
            print("token.json exists")
            with open('token.json', 'r') as f:
                token_data = json.load(f)
                print(f"Token scopes: {token_data.get('scope', 'No scope found')}")
        else:
            print("token.json doesn't exist")
            
        print("Checking for credentials.json...")
        if os.path.exists('credentials.json'):
            print("credentials.json exists")
        else:
            print("credentials.json doesn't exist")
            
        # Test a basic API connection
        creds = Credentials.from_authorized_user_file('token.json', SCOPES) if os.path.exists('token.json') else None
        if creds and creds.valid:
            print("Credentials are valid")
        elif creds and creds.expired and creds.refresh_token:
            print("Credentials expired but can be refreshed")
        else:
            print("Need new credentials")
    except Exception as e:
        print(f"Auth debug error: {e}")

# Call this function early in your initialization

if __name__ == '__main__':
    debug_auth()
    print("Hextrix Google API Authorization Tool")
    print("====================================")
    print("This script will authenticate with Google and test connections to all required APIs.")
    print("You'll need to authorize access in your browser when prompted.")
    print("====================================\n")
    
    # Use the default credentials path
    services = authorize_google_apis()
    test_all_apis(services)
    
    print("\nAuthorization process complete.")
    print("You can now run the main Hextrix application with full API access.")
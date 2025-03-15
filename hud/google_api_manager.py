"""
google_api_manager.py

Manages all Google API connections for Hextrix with data caching
"""

import os
import time
import json
import logging
from datetime import datetime, timedelta
from multi_api_oauth import HextrixOAuth

# Set up logging
logger = logging.getLogger("GoogleAPIManager")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class GoogleAPIManager:
    def __init__(self, credentials_file='credentials.json'):
        self.oauth = HextrixOAuth(credentials_file=credentials_file)
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
        self.cache_duration = {
            'contacts': 3600,  # 1 hour
            'fitness': 1800,   # 30 minutes
            'gmail': 300,      # 5 minutes
            'photos': 7200     # 2 hours
        }
        
        # Initialize cache directory
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_credentials(self):
        """Get OAuth credentials, automatically refreshing if needed."""
        return self.oauth.get_credentials()

    def get_contacts(self, max_results=100, force_refresh=False):
        """
        Get user's contacts from Google Contacts API.
        
        Args:
            max_results: Maximum number of contacts to return
            force_refresh: Whether to force a refresh from the API
            
        Returns:
            List of contact objects
        """
        cache_path = os.path.join(self.cache_dir, 'contacts_cache.json')
        
        # Check if cache exists and is valid
        if not force_refresh and os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
                # Check if cache is still valid
                if time.time() - cache_data['timestamp'] < self.cache_duration['contacts']:
                    logger.info("Using cached contacts data")
                    return cache_data['contacts']
        
        try:
            # Create the People service
            service = self.get_contacts_service()
            
            # Request contacts data
            results = service.people().connections().list(
                resourceName='people/me',
                pageSize=max_results,
                personFields='names,emailAddresses,phoneNumbers,photos'
            ).execute()
            
            # Process the contacts data
            contacts = []
            for person in results.get('connections', []):
                contact = {
                    'resourceName': person.get('resourceName', ''),
                    'names': person.get('names', []),
                    'emailAddresses': person.get('emailAddresses', []),
                    'phoneNumbers': person.get('phoneNumbers', []),
                    'photos': person.get('photos', [])
                }
                
                # Add a processed name field for easy access
                if contact['names']:
                    contact['displayName'] = contact['names'][0].get('displayName', 'Unknown')
                else:
                    contact['displayName'] = 'Unknown'
                
                contacts.append(contact)
            
            # Cache the contacts data
            cache_data = {
                'timestamp': time.time(),
                'contacts': contacts
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            
            logger.info(f"Retrieved {len(contacts)} contacts from Google Contacts API")
            return contacts
            
        except Exception as e:
            logger.error(f"Error retrieving contacts: {str(e)}")
            
            # Return cached data if available, even if expired
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    logger.info("Using expired cached contacts data due to error")
                    return cache_data['contacts']
            
            return []

    def get_fitness_data(self, data_type='steps', days=7, force_refresh=False):
        """
        Get fitness data from Google Fitness API.
        
        Args:
            data_type: Type of fitness data ('steps', 'heart_rate', 'calories', 'weight')
            days: Number of days of data to retrieve
            force_refresh: Whether to force a refresh from the API
            
        Returns:
            Dictionary with fitness data
        """
        cache_path = os.path.join(self.cache_dir, f'fitness_{data_type}_cache.json')
        
        # Check if cache exists and is valid
        if not force_refresh and os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
                # Check if cache is still valid
                if time.time() - cache_data['timestamp'] < self.cache_duration['fitness']:
                    logger.info(f"Using cached {data_type} fitness data")
                    return cache_data['fitness_data']
        
        try:
            # Create the Fitness service
            service = self.get_fitness_service()
            
            # Set up time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Convert to timestamp format in nanoseconds
            end_time_ns = int(end_time.timestamp() * 1000000000)
            start_time_ns = int(start_time.timestamp() * 1000000000)
            
            # Map data types to Google Fitness data sources
            data_sources = {
                'steps': 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
                'heart_rate': 'derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm',
                'calories': 'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended',
                'weight': 'derived:com.google.weight:com.google.android.gms:merge_weight'
            }
            
            data_source = data_sources.get(data_type)
            if not data_source:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            # Request fitness data
            body = {
                "aggregateBy": [{
                    "dataTypeName": data_source
                }],
                "bucketByTime": { "durationMillis": 86400000 },  # Daily buckets
                "startTimeMillis": int(start_time.timestamp() * 1000),
                "endTimeMillis": int(end_time.timestamp() * 1000)
            }
            
            response = service.users().dataset().aggregate(userId="me", body=body).execute()
            
            # Process the fitness data
            fitness_data = {
                'data_type': data_type,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'points': []
            }
            
            for bucket in response.get('bucket', []):
                data_set = bucket.get('dataset', [])[0]
                data_points = data_set.get('point', [])
                
                if data_points:
                    point = data_points[0]
                    value = point.get('value', [{}])[0].get('intVal', 0)
                    
                    fitness_data['points'].append({
                        'start_time': bucket.get('startTimeMillis', 0),
                        'end_time': bucket.get('endTimeMillis', 0),
                        'value': value
                    })
            
            # Cache the fitness data
            cache_data = {
                'timestamp': time.time(),
                'fitness_data': fitness_data
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            
            logger.info(f"Retrieved {len(fitness_data['points'])} days of {data_type} data from Google Fitness API")
            return fitness_data
            
        except Exception as e:
            logger.error(f"Error retrieving fitness data: {str(e)}")
            
            # Return cached data if available, even if expired
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    logger.info(f"Using expired cached {data_type} fitness data due to error")
                    return cache_data['fitness_data']
            
            return {'data_type': data_type, 'points': []}

    def get_gmail_messages(self, max_results=10, force_refresh=False):
        """
        Get recent emails from Gmail API.
        
        Args:
            max_results: Maximum number of emails to return
            force_refresh: Whether to force a refresh from the API
            
        Returns:
            List of email objects
        """
        cache_path = os.path.join(self.cache_dir, 'gmail_cache.json')
        
        # Check if cache exists and is valid
        if not force_refresh and os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
                # Check if cache is still valid
                if time.time() - cache_data['timestamp'] < self.cache_duration['gmail']:
                    logger.info("Using cached Gmail data")
                    return cache_data['messages']
        
        try:
            # Create the Gmail service
            service = self.get_gmail_service()
            
            # Request list of messages
            results = service.users().messages().list(userId='me', maxResults=max_results).execute()
            message_ids = [msg['id'] for msg in results.get('messages', [])]
            
            # Get message details
            messages = []
            for msg_id in message_ids:
                message = service.users().messages().get(userId='me', id=msg_id).execute()
                
                # Extract headers
                headers = {}
                for header in message['payload']['headers']:
                    headers[header['name']] = header['value']
                
                # Process message data
                email = {
                    'id': message['id'],
                    'threadId': message['threadId'],
                    'from': headers.get('From', ''),
                    'to': headers.get('To', ''),
                    'subject': headers.get('Subject', '(No Subject)'),
                    'date': headers.get('Date', ''),
                    'snippet': message.get('snippet', '')
                }
                
                messages.append(email)
            
            # Cache the messages data
            cache_data = {
                'timestamp': time.time(),
                'messages': messages
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            
            logger.info(f"Retrieved {len(messages)} messages from Gmail API")
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving Gmail messages: {str(e)}")
            
            # Return cached data if available, even if expired
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    logger.info("Using expired cached Gmail data due to error")
                    return cache_data['messages']
            
            return []

    def get_photos_service(self):
        """Create an authorized Google Photos service."""
        creds = self.get_credentials()
        
        try:
            # Direct build approach
            return build('photoslibrary', 'v1', credentials=creds, 
                        discoveryServiceUrl='https://photoslibrary.googleapis.com/$discovery/rest?version=v1')
        except Exception as e:
            logger.error(f"Error building Photos API client: {str(e)}")
            
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
                    logger.error(f"Failed to fetch Photos API discovery document: {r.status_code}")
                    return None
            except Exception as inner_e:
                logger.error(f"Error in fallback Photos API initialization: {str(inner_e)}")
                return None

    def get_photo_albums(self, force_refresh=False):
        """
        Get list of photo albums from Google Photos API.
        
        Args:
            force_refresh: Whether to force a refresh from the API
            
        Returns:
            List of album objects
        """
        cache_path = os.path.join(self.cache_dir, 'photo_albums_cache.json')
        
        # Check if cache exists and is valid
        if not force_refresh and os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
                # Check if cache is still valid
                if time.time() - cache_data['timestamp'] < self.cache_duration['photos']:
                    logger.info("Using cached Photo Albums data")
                    return cache_data['albums']
        
        try:
            # Create the Photos service
            service = self.get_photos_service()
            
            # Request albums
            response = service.albums().list(pageSize=50).execute()
            album_items = response.get('albums', [])
            
            # Process the albums data
            albums = []
            for item in album_items:
                album = {
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'productUrl': item.get('productUrl', ''),
                    'mediaItemsCount': item.get('mediaItemsCount', 0),
                    'coverPhotoBaseUrl': item.get('coverPhotoBaseUrl', '')
                }
                
                # Add thumbnail URLs
                if 'coverPhotoBaseUrl' in item:
                    album['coverThumbnailUrl'] = f"{item['coverPhotoBaseUrl']}=w128-h128"
                
                albums.append(album)
            
            # Cache the albums data
            cache_data = {
                'timestamp': time.time(),
                'albums': albums
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            
            logger.info(f"Retrieved {len(albums)} albums from Google Photos API")
            return albums
            
        except Exception as e:
            logger.error(f"Error retrieving photo albums: {str(e)}")
            
            # Return cached data if available, even if expired
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    logger.info("Using expired cached photo albums data due to error")
                    return cache_data['albums']
            
            return []

    # Add missing service getter methods that are being requested by integrations
    def get_service(self, api_name, api_version):
        """Create an authorized Google API service."""
        return self.oauth.create_service(api_name, api_version)
    
    def get_drive_service(self):
        """Create an authorized Google Drive service."""
        return self.oauth.get_drive_service()
    
    def get_contacts_service(self):
        """Create an authorized Google Contacts service."""
        return self.oauth.get_contacts_service()
    
    def get_fitness_service(self):
        """Create an authorized Google Fitness service."""
        return self.oauth.get_fitness_service()
    
    def get_gmail_service(self):
        """Create an authorized Gmail service."""
        return self.oauth.get_gmail_service()
    
    def get_photos_service(self):
        """Create an authorized Google Photos service."""
        return self.oauth.get_photos_service()
    
    def authenticate(self):
        """Helper method to check if authentication is successful"""
        try:
            creds = self.get_credentials()
            return creds and creds.valid
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
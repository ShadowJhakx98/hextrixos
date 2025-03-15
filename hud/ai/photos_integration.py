"""
photos_integration.py

Display Google Photos in HUD panel
"""

import logging
import datetime

logger = logging.getLogger("PhotosIntegration")
logger.setLevel(logging.INFO)

class PhotosIntegration:
    def __init__(self, api_manager):
        """
        Initialize Google Photos integration
        
        Args:
            api_manager: GoogleAPIManager instance
        """
        self.api_manager = api_manager
        self.photos_service = None
        self.cached_photos = {}
        self.cached_albums = None
        self.cache_times = {}
    
    def initialize(self):
        """Initialize the Photos service"""
        try:
            self.photos_service = self.api_manager.get_photos_service()
            return self.photos_service is not None
        except Exception as e:
            logger.error(f"Error initializing Photos service: {str(e)}")
            return False
    
    def get_recent_photos(self, max_results=20, force_refresh=False):
        """Get list of recent photos"""
        # Define cache_key at the beginning to avoid UnboundLocalError
        cache_key = f"recent_{max_results}"
        
        try:
            if not self.photos_service:
                if not self.initialize():
                    return []
            
            # Return cached photos if available and not expired
            if (not force_refresh and cache_key in self.cached_photos and cache_key in self.cache_times and 
                (datetime.datetime.now() - self.cache_times[cache_key]).total_seconds() < 3600):  # 1 hour cache
                return self.cached_photos[cache_key]
            
            # Make the API call
            response = self.photos_service.mediaItems().list(pageSize=max_results).execute()
            
            # Process photos
            photos = self._process_media_items(response.get('mediaItems', []))
            
            # Cache results
            self.cached_photos[cache_key] = photos
            self.cache_times[cache_key] = datetime.datetime.now()
            
            return photos
            
        except Exception as e:
            logger.error(f"Error getting recent photos: {str(e)}")
            if cache_key in self.cached_photos:
                return self.cached_photos[cache_key]
            return []
    
    def get_album_photos(self, album_id, max_results=50, force_refresh=False):
        """Get photos from a specific album"""
        # Define cache_key at the beginning to avoid UnboundLocalError
        cache_key = f"album_{album_id}_{max_results}"
        
        try:
            if not self.photos_service:
                if not self.initialize():
                    return []
            
            # Return cached photos if available and not expired
            if (not force_refresh and cache_key in self.cached_photos and cache_key in self.cache_times and 
                (datetime.datetime.now() - self.cache_times[cache_key]).total_seconds() < 3600):  # 1 hour cache
                return self.cached_photos[cache_key]
            
            # Make the API call
            response = self.photos_service.mediaItems().search(body={
                'albumId': album_id,
                'pageSize': max_results
            }).execute()
            
            # Process photos
            photos = self._process_media_items(response.get('mediaItems', []))
            
            # Cache results
            self.cached_photos[cache_key] = photos
            self.cache_times[cache_key] = datetime.datetime.now()
            
            return photos
            
        except Exception as e:
            logger.error(f"Error getting album photos: {str(e)}")
            if cache_key in self.cached_photos:
                return self.cached_photos[cache_key]
            return []
    
    def get_albums(self, max_results=20, force_refresh=False):
        """Get list of albums"""
        try:
            if not self.photos_service:
                if not self.initialize():
                    return []
            
            # Return cached albums if available and not expired
            if (not force_refresh and self.cached_albums and 'cache_time' in self.cached_albums and 
                (datetime.datetime.now() - self.cached_albums['cache_time']).total_seconds() < 3600):  # 1 hour cache
                return self.cached_albums['albums']
            
            # Make the API call
            response = self.photos_service.albums().list(pageSize=max_results).execute()
            
            # Process albums
            albums = []
            for album in response.get('albums', []):
                processed_album = {
                    'id': album.get('id', ''),
                    'title': album.get('title', ''),
                    'item_count': album.get('mediaItemsCount', 0),
                    'cover_photo_url': album.get('coverPhotoBaseUrl', '')
                }
                
                # Add thumbnail URLs
                if 'coverPhotoBaseUrl' in album:
                    processed_album['thumbnail_url'] = f"{album['coverPhotoBaseUrl']}=w128-h128"
                
                albums.append(processed_album)
            
            # Cache results
            self.cached_albums = {
                'albums': albums,
                'cache_time': datetime.datetime.now()
            }
            
            return albums
            
        except Exception as e:
            logger.error(f"Error getting albums: {str(e)}")
            if self.cached_albums:
                return self.cached_albums['albums']
            return []
    
    def _process_media_items(self, items):
        """Process media items from the API into a simplified format"""
        photos = []
        
        for item in items:
            # Skip items without a baseUrl
            if 'baseUrl' not in item:
                continue
            
            # Process item
            photo = {
                'id': item.get('id', ''),
                'filename': item.get('filename', ''),
                'description': item.get('description', ''),
                'mime_type': item.get('mimeType', ''),
                'url': item.get('productUrl', ''),
                'base_url': item.get('baseUrl', '')
            }
            
            # Add media metadata
            if 'mediaMetadata' in item:
                metadata = item['mediaMetadata']
                photo['creation_time'] = metadata.get('creationTime', '')
                photo['width'] = metadata.get('width', '')
                photo['height'] = metadata.get('height', '')
                
                # Add photo-specific metadata
                if metadata.get('photo'):
                    photo['camera_make'] = metadata['photo'].get('cameraMake', '')
                    photo['camera_model'] = metadata['photo'].get('cameraModel', '')
                    photo['focal_length'] = metadata['photo'].get('focalLength', '')
                    photo['aperture_fnumber'] = metadata['photo'].get('apertureFNumber', '')
                    photo['iso'] = metadata['photo'].get('isoEquivalent', '')
                
                # Add video-specific metadata
                if metadata.get('video'):
                    photo['fps'] = metadata['video'].get('fps', '')
                    photo['status'] = metadata['video'].get('status', '')
            
            # Add URLs for different sizes
            if 'baseUrl' in item:
                photo['thumbnail_url'] = f"{item['baseUrl']}=w128-h128"
                photo['medium_url'] = f"{item['baseUrl']}=w512-h512"
                photo['large_url'] = f"{item['baseUrl']}=w1024-h1024"
            
            photos.append(photo)
        
        return photos
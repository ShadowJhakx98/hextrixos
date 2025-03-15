# drive_integration.py
import os
import io
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class DriveIntegration:
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.drive_service = None
        self.initialize()
        
    def initialize(self):
        """Initialize the Google Drive service"""
        try:
            # Use the API manager to get the drive service
            self.drive_service = self.api_manager.get_drive_service()
            return True if self.drive_service else False
        except Exception as e:
            logger.error(f"Error initializing Drive service: {str(e)}")
            return False
            
    def get_files(self, max_results=100, query=None, force_refresh=False):
        """Get list of files from Google Drive"""
        try:
            if not self.drive_service:
                if not self.initialize():
                    return []
            
            # Build the query
            query_string = "trashed=false"
            if query:
                query_string += f" and {query}"
                
            # Execute the query
            results = self.drive_service.files().list(
                q=query_string,
                pageSize=max_results,
                fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            logger.error(f"Error getting files: {str(e)}")
            return []
            
    def get_folder_contents(self, folder_id, max_results=100):
        """Get contents of a specific folder"""
        query = f"'{folder_id}' in parents"
        return self.get_files(max_results, query)
    
    def upload_file(self, file_path, folder_id=None):
        """Upload a file to Google Drive"""
        try:
            if not self.drive_service:
                if not self.initialize():
                    return None
            
            file_metadata = {
                'name': os.path.basename(file_path)
            }
            
            # Set parent folder if specified
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create media
            mime_type = self._get_mime_type(file_path)
            media = MediaFileUpload(file_path, mimetype=mime_type)
            
            # Upload file
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None

    def download_file(self, file_id, destination_path):
        """Download a file from Google Drive"""
        try:
            if not self.drive_service:
                if not self.initialize():
                    return False
            
            # Get file metadata to get the name
            file = self.drive_service.files().get(fileId=file_id).execute()
            
            # Create request
            request = self.drive_service.files().get_media(fileId=file_id)
            
            # Download file
            with io.FileIO(destination_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    logger.info(f"Download {int(status.progress() * 100)}%")
            
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return False

    def delete_file(self, file_id):
        """Delete a file from Google Drive"""
        try:
            if not self.drive_service:
                if not self.initialize():
                    return False
            
            self.drive_service.files().delete(fileId=file_id).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False

    def create_folder(self, folder_name, parent_id=None):
        """Create a new folder in Google Drive"""
        try:
            if not self.drive_service:
                if not self.initialize():
                    return None
            
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            # Set parent folder if specified
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            # Create folder
            folder = self.drive_service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return None

    def _get_mime_type(self, file_path):
        """Get the MIME type of a file based on its extension"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type
        else:
            # Default to binary
            return 'application/octet-stream'
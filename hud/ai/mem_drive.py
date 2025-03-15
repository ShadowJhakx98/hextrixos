"""
cloud_memory.py

Fixed memory management that uses Google Drive for storage with local caching
"""

import os
import io
import datetime
import numpy as np
import logging
import json
import time
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Configure logging
logger = logging.getLogger("CloudMemoryManager")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class CloudMemoryManager:
    def __init__(self, local_cache_size=1_000_000_000, memory_path=None, use_efficient_backups=False):
        self.local_cache_size = local_cache_size
        self.memory = None
        self.drive_service = None
        self.last_backup_date = None
        self.last_sync_date = None
        self.cloud_file_id = None
        self.local_file_path = memory_path or "brain_memory_cache.bin"  # Use provided path or default
        self.memory_shape = (int(local_cache_size / 8), )  # 8 bytes per float64
        self.use_efficient_backups = use_efficient_backups
        self.backup_drive_id = None  # Will be set later if needed
        
        # Google Drive related settings
        self.scopes = ['https://www.googleapis.com/auth/drive']
        self.token_path = 'token.json'
        self.credentials_path = 'credentials.json'
        self.backup_folder_id = None
        self.cloud_memory_name = "hextrix_brain_memory.bin"

    def initialize_memory(self):
        """Create or load a memory-mapped array for the local cache."""
        try:
            # Check if memory file exists
            if os.path.exists(self.local_file_path):
                logger.info(f"Loading existing memory cache: {self.local_file_path}")
                # Load existing memory file
                self.memory = np.memmap(
                    self.local_file_path,
                    dtype=np.float64,
                    mode='r+',
                    shape=self.memory_shape
                )
            else:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(os.path.abspath(self.local_file_path)), exist_ok=True)
                
                logger.info(f"Creating new memory cache: {self.local_file_path}")
                # Create new memory file
                self.memory = np.memmap(
                    self.local_file_path,
                    dtype=np.float64,
                    mode='w+',
                    shape=self.memory_shape
                )
                # Initialize with zeros
                self.memory[:] = 0
                self.memory.flush()
            
            logger.info(f"Memory cache initialized with shape: {self.memory.shape}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize memory cache: {str(e)}")
            # Create an in-memory fallback
            logger.info("Using in-memory array as fallback")
            self.memory = np.zeros(int(self.local_cache_size / 8), dtype=np.float64)
            return False

    def initialize_drive_service(self):
        """Initialize Google Drive service with proper authentication."""
        try:
            creds = None
            # Check if token file exists
            if os.path.exists(self.token_path):
                try:
                    creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
                except Exception as e:
                    logger.error(f"Error loading credentials from token.json: {e}")
                    os.rename(self.token_path, f"{self.token_path}.bak")
                    creds = None
            
            # If credentials don't exist or are invalid, refresh or get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # If credentials.json doesn't exist, warn and return
                    if not os.path.exists(self.credentials_path):
                        logger.warning(f"Credentials file not found: {self.credentials_path}")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for next run
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            
            # Build the Drive service
            self.drive_service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive service initialized successfully")
            
            # Find or create memory file in Google Drive
            self._setup_cloud_memory()
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize Drive service: {str(e)}")
            return False
    
    def _setup_cloud_memory(self):
        """Find or create the main memory file in Google Drive."""
        if not self.drive_service:
            logger.warning("Drive service not initialized")
            return
        
        # Check if memory file already exists
        query = f"name='{self.cloud_memory_name}' and trashed=false"
        results = self.drive_service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
        items = results.get('files', [])
        
        if items:
            # Use the first matching file
            self.cloud_file_id = items[0]['id']
            logger.info(f"Found existing cloud memory file: {self.cloud_file_id} (modified: {items[0]['modifiedTime']})")
        else:
            # Create initial empty file in Drive
            logger.info("Creating new cloud memory file")
            # Create a small initial file
            with open("initial_memory.bin", "wb") as f:
                np.zeros(1000, dtype=np.float64).tofile(f)
            
            file_metadata = {
                'name': self.cloud_memory_name
            }
            media = MediaFileUpload("initial_memory.bin", resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            self.cloud_file_id = file.get('id')
            logger.info(f"Created new cloud memory file with ID: {self.cloud_file_id}")
            
            # Clean up local temp file
            if os.path.exists("initial_memory.bin"):
                os.remove("initial_memory.bin")

    def upload_memory(self):
        """Upload the local memory cache to Google Drive."""
        if not self.drive_service or not self.cloud_file_id:
            logger.warning("Drive service or cloud file ID not available")
            return False
        
        try:
            # Ensure memory is flushed to disk
            if hasattr(self.memory, 'flush'):
                self.memory.flush()
            
            logger.info(f"Uploading memory cache to Google Drive ({self.cloud_file_id})")
            
            # Create a temporary copy of the memory file to avoid issues with memory-mapped files
            temp_file_path = f"{self.local_file_path}.tmp"
            with open(self.local_file_path, 'rb') as src_file:
                with open(temp_file_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())
            
            # Update the existing file using the temp file
            media = MediaFileUpload(temp_file_path, resumable=True)
            file = self.drive_service.files().update(
                fileId=self.cloud_file_id,
                media_body=media
            ).execute()
            
            # Remove temp file
            os.remove(temp_file_path)
            
            self.last_sync_date = datetime.datetime.now()
            logger.info(f"Memory cache uploaded successfully at {self.last_sync_date}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload memory cache: {str(e)}")
            return False

    def download_memory(self):
        """Download the cloud memory file to local cache."""
        if not self.drive_service or not self.cloud_file_id:
            logger.warning("Drive service or cloud file ID not available")
            return False
        
        try:
            logger.info(f"Downloading memory from Google Drive ({self.cloud_file_id})")
            
            # Get file metadata
            file_metadata = self.drive_service.files().get(fileId=self.cloud_file_id).execute()
            
            # Create download request
            request = self.drive_service.files().get_media(fileId=self.cloud_file_id)
            
            # Create a BytesIO stream to save the file content
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            # Download the file
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logger.info(f"Download progress: {int(status.progress() * 100)}%")
            
            # First close the current memory map if it exists
            if hasattr(self.memory, '_mmap'):
                del self.memory
            
            # Save to a temporary file first
            temp_file_path = f"{self.local_file_path}.downloading"
            with open(temp_file_path, 'wb') as f:
                f.write(file_content.getvalue())
            
            # Atomically replace the existing file
            if os.path.exists(self.local_file_path):
                # On Windows, can't replace directly, so use a backup approach
                backup_path = f"{self.local_file_path}.bak"
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(self.local_file_path, backup_path)
            
            os.rename(temp_file_path, self.local_file_path)
            
            # Reload the memory map
            self.memory = np.memmap(
                self.local_file_path,
                dtype=np.float64,
                mode='r+',
                shape=self.memory_shape
            )
            
            self.last_sync_date = datetime.datetime.now()
            logger.info(f"Memory downloaded successfully at {self.last_sync_date}")
            return True
        except Exception as e:
            logger.error(f"Failed to download memory: {str(e)}")
            return False

    def store_embeddings(self, embeddings, indices=None):
        """Store embeddings at the specified indices in the local memory cache."""
        if self.memory is None and not self.initialize_memory():
            logger.error("Cannot store embeddings - memory initialization failed")
            return False
        
        try:
            if indices is None:
                # Find empty space (zeros) in memory
                zero_indices = np.where(self.memory[:len(embeddings)] == 0)[0]
                if len(zero_indices) >= len(embeddings):
                    indices = zero_indices[:len(embeddings)]
                else:
                    # Not enough space at the beginning, try to find elsewhere
                    all_zeros = np.where(self.memory == 0)[0]
                    if len(all_zeros) >= len(embeddings):
                        indices = all_zeros[:len(embeddings)]
                    else:
                        # No empty space, overwrite oldest data (simple approach)
                        indices = np.arange(len(embeddings))
            
            # Store embeddings at the specified indices
            self.memory[indices] = embeddings
            if hasattr(self.memory, 'flush'):
                self.memory.flush()
            
            logger.info(f"Stored {len(embeddings)} embeddings at indices {indices[0]}-{indices[-1] if len(indices) > 1 else indices[0]}")
            
            # Auto-sync with cloud occasionally
            if hasattr(self, 'last_sync_date') and hasattr(self, 'upload_memory'):
                if self.last_sync_date is None or (datetime.datetime.now() - self.last_sync_date).total_seconds() > 3600:
                    self.upload_memory()
                    
            return indices
        except Exception as e:
            logger.error(f"Failed to store embeddings: {str(e)}")
            return False

    def add_memory(self, text, metadata=None, embedding=None):
        """
        Simplified interface to add a memory entry with text and optional metadata.
        
        Args:
            text (str): The text content to store in memory
            metadata (dict, optional): Additional metadata for the memory entry
            embedding (np.array, optional): Pre-computed embedding for the text
            
        Returns:
            int or None: The index where the memory was stored, or None if failed
        """
        try:
            if self.memory is None and not self.initialize_memory():
                logger.error("Cannot add memory - memory initialization failed")
                return None
                
            # Create a simple memory entry
            entry = {
                "text": text,
                "timestamp": datetime.datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # If no embedding provided, create a simple one (placeholder implementation)
            if embedding is None:
                # Create a basic embedding by hashing the text
                # This is just a placeholder - in a real system you'd use a proper embedding model
                import hashlib
                hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
                # Create a simple vector using the hash value
                embedding = np.array([hash_val % 100000 / 100000.0 for _ in range(10)], dtype=np.float64)
                
            # Store the embedding
            indices = self.store_embeddings(embedding.reshape(1, -1))
            if indices is not False and len(indices) > 0:
                logger.info(f"Added memory '{text[:30]}...' at index {indices[0]}")
                return indices[0]
            else:
                logger.error("Failed to store memory embedding")
                return None
                
        except Exception as e:
            logger.error(f"Failed to add memory: {str(e)}")
            return None

    def retrieve_embeddings(self, indices):
        """Retrieve embedding vectors from the memory map."""
        if self.memory is None:
            logger.error("Memory not initialized")
            return None
        
        try:
            embeddings = self.memory[indices]
            logger.info(f"Retrieved {len(indices)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to retrieve embeddings: {str(e)}")
            return None

    def is_memory_initialized(self):
        """Check if memory is properly initialized"""
        return hasattr(self, 'memory') and self.memory is not None

    def search_similar_embeddings(self, query_embedding, top_k=5):
        """Find similar embeddings using cosine similarity."""
        if self.memory is None:
            logger.error("Memory not initialized")
            return None
        
        try:
            # Normalize query embedding
            query_norm = np.linalg.norm(query_embedding)
            if query_norm > 0:
                query_embedding = query_embedding / query_norm
            
            # Calculate dot product with all non-zero embeddings
            non_zero_indices = np.where(self.memory != 0)[0]
            if len(non_zero_indices) == 0:
                return []
            
            # Get non-zero embeddings
            embeddings = self.memory[non_zero_indices]
            
            # Normalize embeddings
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            normalized = np.divide(embeddings, norms, out=np.zeros_like(embeddings), where=norms>0)
            
            # Calculate similarities
            similarities = np.dot(normalized, query_embedding)
            
            # Get top-k indices
            if len(similarities) < top_k:
                top_k = len(similarities)
            
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Map back to original indices
            result_indices = non_zero_indices[top_indices]
            
            return {
                'indices': result_indices,
                'similarities': similarities[top_indices]
            }
        except Exception as e:
            logger.error(f"Failed to search similar embeddings: {str(e)}")
            return None

    def create_backup(self, backup_name=None, frequency_days=7):
        """Create a backup of the memory file in Google Drive."""
        if not self.drive_service or not self.cloud_file_id:
            logger.warning("Drive service or cloud file ID not available")
            return False
        
        # If efficient backups are enabled, use that method instead
        if hasattr(self, 'use_efficient_backups') and self.use_efficient_backups:
            return self.create_efficient_backup(backup_name)
        
        try:
            # First make sure our cloud memory is up to date
            self.upload_memory()
            
            # Now create a backup copy
            if backup_name is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"hextrix_memory_backup_{timestamp}.bin"
            
            # Determine if we should use the backup drive
            file_metadata = {'name': backup_name}
            if hasattr(self, 'backup_drive_id') and self.backup_drive_id:
                file_metadata['parents'] = [self.backup_drive_id]
            
            # Copy the file
            copied_file = self.drive_service.files().copy(
                fileId=self.cloud_file_id,
                body=file_metadata
            ).execute()
            
            logger.info(f"Backup created: {backup_name}, ID: {copied_file['id']}")
            self.last_backup_date = datetime.datetime.now()
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return False

    def set_backup_drive_id(self, drive_id):
        """Set the Google Drive ID to use for backups."""
        self.backup_drive_id = drive_id
        logger.info(f"Backup Google Drive ID set to: {drive_id}")
        return True

    def enable_dynamic_fetching(self, enabled=True):
        """Enable or disable dynamic fetching of memories from cloud storage."""
        self.dynamic_fetching_enabled = enabled
        logger.info(f"Dynamic memory fetching {'enabled' if enabled else 'disabled'}")
        return True

    def set_backup_mode(self, mode):
        """Set the backup mode (full, incremental, differential)."""
        if mode not in ['full', 'incremental', 'differential']:
            logger.error(f"Invalid backup mode: {mode}")
            return False
        
        self.backup_mode = mode
        logger.info(f"Backup mode set to: {mode}")
        return True

    def set_compression_level(self, level):
        """Set the compression level for backups (0-9)."""
        if not 0 <= level <= 9:
            logger.error(f"Invalid compression level: {level} (must be 0-9)")
            return False
        
        self.compression_level = level
        logger.info(f"Backup compression level set to: {level}")
        return True

    def create_efficient_backup(self, backup_name=None):
        """Create an efficient backup with compression that only includes non-zero data."""
        if not self.drive_service:
            logger.warning("Drive service not available")
            return False
        
        try:
            # First ensure memory is flushed to disk
            if hasattr(self.memory, 'flush'):
                self.memory.flush()
            
            # Find non-zero data
            non_zero_indices = np.where(self.memory != 0)[0]
            if len(non_zero_indices) == 0:
                logger.info("No non-zero data to back up")
                self.last_backup_date = datetime.datetime.now()
                return True
            
            # Create temp file for compressed data
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_backup_file = f"temp_backup_{timestamp}.npz"
            
            # Save only non-zero data with compression
            np.savez_compressed(
                temp_backup_file,
                indices=non_zero_indices,
                values=self.memory[non_zero_indices],
                shape=self.memory_shape
            )
            
            # Set backup name
            if backup_name is None:
                backup_name = f"hextrix_memory_backup_{timestamp}.npz"
            
            # Create file metadata
            file_metadata = {'name': backup_name}
            if hasattr(self, 'backup_drive_id') and self.backup_drive_id:
                file_metadata['parents'] = [self.backup_drive_id]
            
            # Upload to Google Drive
            media = MediaFileUpload(temp_backup_file, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            # Clean up temp file
            os.remove(temp_backup_file)
            
            # Log success
            data_size = len(non_zero_indices) * 8
            logger.info(f"Efficient backup created: {backup_name}, ID: {file.get('id')}")
            logger.info(f"Backed up {len(non_zero_indices)} non-zero elements ({data_size/1024/1024:.2f} MB)")
            
            self.last_backup_date = datetime.datetime.now()
            return True
        except Exception as e:
            logger.error(f"Failed to create efficient backup: {str(e)}")
            return False
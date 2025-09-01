"""
Vercel Blob Storage Module for File Uploads
Handles document storage using Vercel's Blob Storage service
"""

import os
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any

class BlobStorage:
    """Handle file uploads to Vercel Blob Storage"""
    
    def __init__(self):
        # Vercel Blob requires a token - will be set in environment
        self.blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN', '')
        self.store_id = 'store_7ceE5O6mxIxmHWR2'
        self.public_url = 'https://7cee5o6mxixmhwr2.public.blob.vercel-storage.com'
        self.blob_api_url = 'https://blob.vercel-storage.com'
        self.connected = bool(self.blob_token)
        
        if self.connected:
            print("[BLOB] Vercel Blob Storage configured")
        else:
            print("[BLOB] Vercel Blob Storage not configured - set BLOB_READ_WRITE_TOKEN")
    
    def upload_file(self, file_data: bytes, filename: str, user_email: str, 
                   content_type: str = 'application/octet-stream') -> Optional[Dict[str, Any]]:
        """
        Upload a file to Vercel Blob Storage
        
        Args:
            file_data: Binary file data
            filename: Original filename
            user_email: Email of user uploading
            content_type: MIME type of file
            
        Returns:
            Dict with url and metadata if successful, None if failed
        """
        if not self.connected:
            print("[BLOB] Cannot upload - Blob Storage not configured")
            return None
        
        try:
            # Create a unique path for the file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_email = user_email.replace('@', '_at_').replace('.', '_')
            blob_path = f"uploads/{safe_email}/{timestamp}_{filename}"
            
            # Upload to Vercel Blob using the correct API endpoint
            response = requests.put(
                f"{self.blob_api_url}/{self.store_id}/{blob_path}",
                headers={
                    'authorization': f'Bearer {self.blob_token}',
                    'x-content-type': content_type,
                    'x-vercel-blob-addon-store': self.store_id
                },
                data=file_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"[BLOB] File uploaded successfully: {blob_path}")
                return {
                    'url': result.get('url'),
                    'pathname': blob_path,
                    'size': len(file_data),
                    'uploaded_at': datetime.now().isoformat(),
                    'content_type': content_type,
                    'original_name': filename
                }
            else:
                print(f"[BLOB] Upload failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[BLOB] Error uploading file: {e}")
            return None
    
    def delete_file(self, url: str) -> bool:
        """
        Delete a file from Vercel Blob Storage
        
        Args:
            url: The blob URL to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            print("[BLOB] Cannot delete - Blob Storage not configured")
            return False
        
        try:
            response = requests.delete(
                url,
                headers={
                    'authorization': f'Bearer {self.blob_token}'
                }
            )
            
            if response.status_code == 200:
                print(f"[BLOB] File deleted successfully: {url}")
                return True
            else:
                print(f"[BLOB] Delete failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[BLOB] Error deleting file: {e}")
            return False
    
    def list_user_files(self, user_email: str) -> list:
        """
        List all files for a specific user
        
        Args:
            user_email: Email of the user
            
        Returns:
            List of file metadata
        """
        if not self.connected:
            print("[BLOB] Cannot list files - Blob Storage not configured")
            return []
        
        try:
            safe_email = user_email.replace('@', '_at_').replace('.', '_')
            prefix = f"uploads/{safe_email}/"
            
            response = requests.get(
                f"{self.blob_api_url}/list",
                headers={
                    'authorization': f'Bearer {self.blob_token}'
                },
                params={
                    'prefix': prefix
                }
            )
            
            if response.status_code == 200:
                blobs = response.json().get('blobs', [])
                print(f"[BLOB] Found {len(blobs)} files for {user_email}")
                return blobs
            else:
                print(f"[BLOB] List failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[BLOB] Error listing files: {e}")
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dict with storage stats
        """
        if not self.connected:
            return {
                'connected': False,
                'total_files': 0,
                'total_size_mb': 0
            }
        
        try:
            # For now, return basic stats
            # Vercel Blob API doesn't provide global stats easily
            return {
                'connected': True,
                'service': 'Vercel Blob Storage',
                'status': 'Active'
            }
        except Exception as e:
            print(f"[BLOB] Error getting stats: {e}")
            return {
                'connected': False,
                'error': str(e)
            }

# Global instance
blob_storage = BlobStorage()

# Helper functions for backward compatibility
def upload_document(file_data, filename, user_email, content_type='application/pdf'):
    """Upload a document to Blob Storage"""
    return blob_storage.upload_file(file_data, filename, user_email, content_type)

def get_user_documents(user_email):
    """Get all documents for a user"""
    return blob_storage.list_user_files(user_email)

def delete_document(url):
    """Delete a document from Blob Storage"""
    return blob_storage.delete_file(url)
"""
Permutation Results Storage System
Always uses Vercel Blob Storage for all permutation results
Provides consistent, scalable storage with 500GB free tier capacity
Now uses improved compression and MongoDB metadata separation
"""
import os
import json
import gzip
import time
import requests
from datetime import datetime

# Vercel Blob credentials from environment
BLOB_READ_WRITE_TOKEN = os.environ.get('BLOB_READ_WRITE_TOKEN', '')

class PermutationResultsStorage:
    """Store and retrieve large permutation results"""

    def __init__(self):
        self.token = BLOB_READ_WRITE_TOKEN
        self.prefix = 'permutation-results/'
        self.blob_api_url = 'https://blob.vercel-storage.com'
        self.available = bool(self.token)

        if not self.available:
            print("[BLOB] Warning: BLOB_READ_WRITE_TOKEN environment variable not set")
            print("[BLOB] Permutation storage will not work until token is configured")
        else:
            print("[BLOB] Permutation Results Storage initialized successfully")
        
    def save_permutation_results(self, project_id, user_email, results_data):
        """
        Save permutation results to Vercel Blob

        Args:
            project_id: Project identifier
            user_email: User who ran the permutation
            results_data: Dict containing permutations, summary, metadata

        Returns:
            Dict with success status and blob URL
        """
        if not self.available:
            return {
                'success': False,
                'error': 'Vercel Blob storage not configured'
            }

        try:
            print(f"[BLOB] Compressing permutation results for project {project_id}...")

            # Compress results with gzip (maximum compression)
            json_data = json.dumps(results_data).encode('utf-8')
            compressed_data = gzip.compress(
                json_data,
                compresslevel=9  # Maximum compression
            )

            compression_ratio = len(json_data) / len(compressed_data)
            print(f"[BLOB] Compressed {len(json_data):,} bytes → {len(compressed_data):,} bytes")
            print(f"[BLOB] Compression ratio: {compression_ratio:.1f}:1")

            # Generate filename with timestamp
            timestamp = int(time.time())
            filename = f"{self.prefix}{project_id}_{timestamp}.json.gz"

            print(f"[BLOB] Uploading to Vercel Blob: {filename}")

            # Upload to Vercel Blob using REST API
            upload_response = requests.put(
                f"{self.blob_api_url}",
                params={'pathname': filename},
                headers={
                    'authorization': f'Bearer {self.token}',
                    'x-content-type': 'application/gzip',
                    'x-add-random-suffix': '0'
                },
                data=compressed_data
            )

            if upload_response.status_code != 200:
                print(f"[BLOB] Upload failed: {upload_response.status_code} - {upload_response.text}")
                return {
                    'success': False,
                    'error': f'Upload failed: {upload_response.status_code}'
                }

            blob_result = upload_response.json()
            blob_url = blob_result.get('url')

            print(f"[BLOB] Upload successful!")
            print(f"[BLOB] URL: {blob_url}")

            # Store metadata in MongoDB (small reference doc)
            metadata = {
                'project_id': project_id,
                'blob_url': blob_url,
                'blob_pathname': blob_result.get('pathname', filename),
                'executed_by': user_email,
                'permutation_count': len(results_data.get('permutations', [])),
                'compressed_size': len(compressed_data),
                'uncompressed_size': len(json_data),
                'compression_ratio': round(compression_ratio, 2),
                'timestamp': datetime.now().isoformat(),
                'summary': results_data.get('summary', {})
            }

            # Save metadata to MongoDB (only ~5KB)
            try:
                from cloud_database import cloud_db
                if cloud_db and cloud_db.connected:
                    cloud_db.db.permutation_metadata.update_one(
                        {'project_id': project_id},
                        {'$set': metadata},
                        upsert=True
                    )
                    print(f"[BLOB] Metadata saved to MongoDB")
                else:
                    print(f"[BLOB] Warning: MongoDB not connected, metadata not saved")
            except Exception as e:
                print(f"[BLOB] Warning: Failed to save metadata to MongoDB: {e}")

            return {
                'success': True,
                'storage_type': 'blob',
                'blob_url': blob_url,
                'result_id': project_id,
                'size_kb': round(len(compressed_data) / 1024, 2),
                'metadata': metadata
            }

        except Exception as e:
            print(f"[BLOB] Error saving permutation results: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def load_permutation_results(self, project_id):
        """
        Load permutation results from Vercel Blob

        Args:
            project_id: Project identifier

        Returns:
            Decompressed results dict or None if not found
        """
        if not self.available:
            print("[BLOB] Vercel Blob storage not configured")
            return None

        try:
            print(f"[BLOB] Loading permutation results for project {project_id}")

            # Get metadata from MongoDB
            from cloud_database import cloud_db
            if not cloud_db or not cloud_db.connected:
                print("[BLOB] MongoDB not connected, cannot retrieve blob URL")
                return None

            metadata = cloud_db.db.permutation_metadata.find_one(
                {'project_id': project_id}
            )

            if not metadata:
                print(f"[BLOB] No metadata found for project {project_id}")
                return None

            blob_url = metadata.get('blob_url')
            if not blob_url:
                print(f"[BLOB] No blob URL in metadata")
                return None

            print(f"[BLOB] Fetching from: {blob_url}")
            print(f"[BLOB] Size: {metadata.get('compressed_size', 0):,} bytes (compressed)")

            # Fetch from Vercel Blob
            response = requests.get(blob_url)

            if response.status_code != 200:
                print(f"[BLOB] Failed to fetch blob: {response.status_code}")
                return None

            # Decompress
            print(f"[BLOB] Decompressing...")
            compressed_data = response.content
            decompressed_data = gzip.decompress(compressed_data)
            results = json.loads(decompressed_data.decode('utf-8'))

            print(f"[BLOB] Successfully loaded {metadata.get('permutation_count', 0):,} permutations")

            # Add metadata to results for backward compatibility
            results['_metadata'] = metadata
            results['_storage_type'] = 'blob'

            return results

        except Exception as e:
            print(f"[BLOB] Error loading permutation results: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def list_permutation_results(self, user_email=None):
        """
        List all permutation result versions for projects

        Returns:
            List of metadata dicts
        """
        try:
            from cloud_database import cloud_db
            if not cloud_db or not cloud_db.connected:
                return []

            query = {}
            if user_email:
                query['executed_by'] = user_email

            cursor = cloud_db.db.permutation_metadata.find(query).sort('timestamp', -1)

            results = []
            for doc in cursor:
                doc.pop('_id', None)  # Remove MongoDB ID
                results.append(doc)

            return results

        except Exception as e:
            print(f"[BLOB] Error listing results: {e}")
            return []

    def delete_permutation_results(self, project_id):
        """Delete permutation results from blob storage"""
        if not self.available:
            return {'success': False, 'error': 'Vercel Blob storage not configured'}

        try:
            # Get metadata
            from cloud_database import cloud_db
            if not cloud_db or not cloud_db.connected:
                return {'success': False, 'error': 'MongoDB not connected'}

            metadata = cloud_db.db.permutation_metadata.find_one(
                {'project_id': project_id}
            )

            if not metadata:
                return {'success': False, 'error': 'Not found'}

            # Delete from Vercel Blob
            blob_url = metadata.get('blob_url')
            if blob_url:
                print(f"[BLOB] Deleting blob: {blob_url}")
                delete_response = requests.delete(
                    blob_url,
                    headers={'authorization': f'Bearer {self.token}'}
                )
                if delete_response.status_code == 200:
                    print(f"[BLOB] Blob deleted successfully")
                else:
                    print(f"[BLOB] Delete warning: {delete_response.status_code}")

            # Delete metadata from MongoDB
            cloud_db.db.permutation_metadata.delete_one(
                {'project_id': project_id}
            )
            print(f"[BLOB] Metadata deleted from MongoDB")

            return {'success': True}

        except Exception as e:
            print(f"[BLOB] Error deleting permutation results: {e}")
            return {'success': False, 'error': str(e)}

    def get_storage_stats(self):
        """Get storage statistics"""
        try:
            from cloud_database import cloud_db
            if not cloud_db or not cloud_db.connected:
                return None

            # Count total permutations stored
            total_count = cloud_db.db.permutation_metadata.count_documents({})

            # Calculate total storage used
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_compressed': {'$sum': '$compressed_size'},
                        'total_uncompressed': {'$sum': '$uncompressed_size'},
                        'total_permutations': {'$sum': '$permutation_count'}
                    }
                }
            ]
            result = list(cloud_db.db.permutation_metadata.aggregate(pipeline))

            if result:
                stats = result[0]
                return {
                    'project_count': total_count,
                    'total_compressed_bytes': stats.get('total_compressed', 0),
                    'total_uncompressed_bytes': stats.get('total_uncompressed', 0),
                    'total_permutations': stats.get('total_permutations', 0),
                    'total_compressed_gb': round(stats.get('total_compressed', 0) / 1024 / 1024 / 1024, 2),
                    'average_compression_ratio': round(
                        stats.get('total_uncompressed', 1) / max(stats.get('total_compressed', 1), 1),
                        2
                    )
                }
            return None

        except Exception as e:
            print(f"[BLOB] Error getting storage stats: {e}")
            return None

# Global instance
permutation_storage = PermutationResultsStorage()
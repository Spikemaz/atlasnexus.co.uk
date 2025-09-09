"""
Permutation Results Storage System
Always uses Vercel Blob Storage for all permutation results
Provides consistent, scalable storage with 100GB capacity
"""
import json
import gzip
import hashlib
from datetime import datetime
from blob_storage import blob_storage

class PermutationResultsStorage:
    """Store and retrieve large permutation results"""
    
    def __init__(self):
        self.blob = blob_storage
        
    def save_permutation_results(self, project_id, user_email, results_data):
        """
        Save permutation results to Vercel Blob Storage
        
        Args:
            project_id: The project identifier
            user_email: User who ran the permutation
            results_data: Dictionary containing:
                - parameters: Input parameters used
                - permutations: List of all permutation results
                - summary: Summary statistics
                - metadata: Additional metadata
        """
        try:
            # Create metadata
            metadata = {
                'project_id': project_id,
                'user_email': user_email,
                'created_at': datetime.now().isoformat(),
                'permutation_count': len(results_data.get('permutations', [])),
                'parameters_hash': self._hash_parameters(results_data.get('parameters', {}))
            }
            
            # Compress the results
            json_data = json.dumps(results_data)
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            
            # Calculate sizes
            original_size = len(json_data)
            compressed_size = len(compressed_data)
            compression_ratio = round((1 - compressed_size/original_size) * 100, 1)
            
            metadata['original_size_kb'] = round(original_size / 1024, 2)
            metadata['compressed_size_kb'] = round(compressed_size / 1024, 2)
            metadata['compression_ratio'] = compression_ratio
            
            print(f"[PERMUTATION] Original: {metadata['original_size_kb']}KB, "
                  f"Compressed: {metadata['compressed_size_kb']}KB "
                  f"({compression_ratio}% reduction)")
            
            # Always use Vercel Blob for consistency and simplicity
            return self._save_to_blob(project_id, compressed_data, metadata)
                
        except Exception as e:
            print(f"[ERROR] Failed to save permutation results: {e}")
            return None
    
    def _save_to_blob(self, project_id, compressed_data, metadata):
        """Save results to Vercel Blob Storage"""
        try:
            # Create blob filename
            filename = f"permutation_results/{project_id}/{metadata['parameters_hash']}.gz"
            
            # Upload to blob storage
            blob_url = self.blob.put(
                filename,
                compressed_data,
                {
                    'contentType': 'application/gzip',
                    'metadata': metadata
                }
            )
            
            # Save reference in MongoDB
            from cloud_database import CloudDatabase
            db = CloudDatabase()
            
            doc = {
                'project_id': project_id,
                'metadata': metadata,
                'blob_url': blob_url,
                'storage_type': 'blob',
                'filename': filename
            }
            
            result = db.db.permutation_results.replace_one(
                {'project_id': project_id},
                doc,
                upsert=True
            )
            
            return {
                'success': True,
                'storage_type': 'blob',
                'blob_url': blob_url,
                'result_id': str(result.upserted_id) if result.upserted_id else project_id,
                'size_kb': metadata['compressed_size_kb']
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to save to blob: {e}")
            return None
    
    def load_permutation_results(self, project_id):
        """Load permutation results from Vercel Blob"""
        try:
            from cloud_database import CloudDatabase
            db = CloudDatabase()
            
            # Find the result document
            doc = db.db.permutation_results.find_one({'project_id': project_id})
            
            if not doc:
                return None
            
            # Always fetch from blob storage
            blob_url = doc['blob_url']
            
            # Fetch from Vercel Blob
            import requests
            response = requests.get(blob_url)
            if response.status_code != 200:
                print(f"[ERROR] Failed to fetch from blob: {response.status_code}")
                return None
            
            compressed_data = response.content
            
            # Decompress
            json_data = gzip.decompress(compressed_data).decode('utf-8')
            results_data = json.loads(json_data)
            
            # Add metadata to results
            results_data['_metadata'] = doc['metadata']
            results_data['_storage_type'] = doc['storage_type']
            
            return results_data
            
        except Exception as e:
            print(f"[ERROR] Failed to load permutation results: {e}")
            return None
    
    def list_permutation_results(self, user_email=None):
        """List all available permutation results"""
        try:
            from cloud_database import CloudDatabase
            db = CloudDatabase()
            
            # Build query
            query = {}
            if user_email:
                query['metadata.user_email'] = user_email
            
            # Find all results
            results = list(db.db.permutation_results.find(
                query,
                {'project_id': 1, 'metadata': 1, 'storage_type': 1}
            ))
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Failed to list results: {e}")
            return []
    
    def _hash_parameters(self, parameters):
        """Create a hash of parameters for uniqueness"""
        param_str = json.dumps(parameters, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()[:12]

# Global instance
permutation_storage = PermutationResultsStorage()
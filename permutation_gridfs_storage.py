"""
Permutation Results Storage using MongoDB GridFS
Better solution for large datasets - no size limits
"""
import json
import gzip
import hashlib
from datetime import datetime
from bson import ObjectId
import gridfs
from cloud_database import CloudDatabase

class PermutationGridFSStorage:
    """Store large permutation results using MongoDB GridFS"""
    
    def __init__(self):
        self.db = CloudDatabase()
        if self.db.connected:
            self.fs = gridfs.GridFS(self.db.db)
            print("[STORAGE] GridFS initialized for large file storage")
        else:
            self.fs = None
            print("[STORAGE] GridFS not available - MongoDB not connected")
    
    def save_permutation_results(self, project_id, user_email, results_data):
        """
        Save permutation results using GridFS for unlimited size
        
        Args:
            project_id: Project identifier
            user_email: User who ran the permutation
            results_data: Results dictionary
        
        Returns:
            Storage result with file ID and metadata
        """
        if not self.fs:
            return {'success': False, 'message': 'GridFS not available'}
        
        try:
            # Prepare metadata
            metadata = {
                'project_id': project_id,
                'user_email': user_email,
                'created_at': datetime.now().isoformat(),
                'permutation_count': len(results_data.get('permutations', [])),
                'type': 'permutation_results'
            }
            
            # Convert to JSON and compress
            json_data = json.dumps(results_data)
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            
            # Calculate sizes
            original_size = len(json_data)
            compressed_size = len(compressed_data)
            compression_ratio = round((1 - compressed_size/original_size) * 100, 1)
            
            metadata['original_size_mb'] = round(original_size / (1024 * 1024), 2)
            metadata['compressed_size_mb'] = round(compressed_size / (1024 * 1024), 2)
            metadata['compression_ratio'] = compression_ratio
            
            print(f"[PERMUTATION] Storing results:")
            print(f"  Original: {metadata['original_size_mb']} MB")
            print(f"  Compressed: {metadata['compressed_size_mb']} MB")
            print(f"  Reduction: {compression_ratio}%")
            
            # Delete old results for this project if they exist
            self.delete_old_results(project_id)
            
            # Store in GridFS
            file_id = self.fs.put(
                compressed_data,
                filename=f"permutation_{project_id}.gz",
                metadata=metadata,
                content_type='application/gzip'
            )
            
            # Store reference in regular collection for fast lookups
            self.db.db.permutation_results.replace_one(
                {'project_id': project_id},
                {
                    'project_id': project_id,
                    'file_id': str(file_id),
                    'metadata': metadata,
                    'storage_type': 'gridfs'
                },
                upsert=True
            )
            
            return {
                'success': True,
                'file_id': str(file_id),
                'storage_type': 'gridfs',
                'size_mb': metadata['compressed_size_mb'],
                'compression_ratio': compression_ratio,
                'message': f'Stored {metadata["permutation_count"]} permutations ({metadata["compressed_size_mb"]} MB)'
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to save to GridFS: {e}")
            return {'success': False, 'message': str(e)}
    
    def load_permutation_results(self, project_id):
        """Load permutation results from GridFS"""
        if not self.fs:
            return None
        
        try:
            # Find the reference
            ref = self.db.db.permutation_results.find_one({'project_id': project_id})
            if not ref:
                return None
            
            # Get file from GridFS
            file_id = ObjectId(ref['file_id'])
            grid_file = self.fs.get(file_id)
            
            # Read and decompress
            compressed_data = grid_file.read()
            json_data = gzip.decompress(compressed_data).decode('utf-8')
            results = json.loads(json_data)
            
            # Add metadata
            results['_metadata'] = ref['metadata']
            results['_storage'] = {
                'type': 'gridfs',
                'file_id': ref['file_id'],
                'size_mb': ref['metadata']['compressed_size_mb']
            }
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Failed to load from GridFS: {e}")
            return None
    
    def delete_old_results(self, project_id):
        """Delete old results for a project"""
        try:
            # Find existing reference
            ref = self.db.db.permutation_results.find_one({'project_id': project_id})
            if ref and 'file_id' in ref:
                # Delete from GridFS
                file_id = ObjectId(ref['file_id'])
                self.fs.delete(file_id)
                print(f"[STORAGE] Deleted old results for project {project_id}")
        except Exception as e:
            print(f"[WARNING] Could not delete old results: {e}")
    
    def list_results(self, user_email=None):
        """List all stored permutation results"""
        try:
            query = {}
            if user_email:
                query['metadata.user_email'] = user_email
            
            results = list(self.db.db.permutation_results.find(
                query,
                {'project_id': 1, 'metadata': 1}
            ))
            
            # Format for display
            formatted = []
            for result in results:
                formatted.append({
                    'project_id': result['project_id'],
                    'created_at': result['metadata']['created_at'],
                    'size_mb': result['metadata']['compressed_size_mb'],
                    'permutation_count': result['metadata']['permutation_count'],
                    'user': result['metadata']['user_email']
                })
            
            return formatted
            
        except Exception as e:
            print(f"[ERROR] Failed to list results: {e}")
            return []
    
    def get_storage_stats(self):
        """Get storage statistics"""
        try:
            # Count GridFS files
            file_count = self.db.db.fs.files.count_documents({'metadata.type': 'permutation_results'})
            
            # Calculate total size
            pipeline = [
                {'$match': {'metadata.type': 'permutation_results'}},
                {'$group': {'_id': None, 'total_size': {'$sum': '$length'}}}
            ]
            result = list(self.db.db.fs.files.aggregate(pipeline))
            total_size = result[0]['total_size'] if result else 0
            
            return {
                'file_count': file_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'storage_type': 'MongoDB GridFS',
                'unlimited': True,
                'message': 'No size limits with GridFS'
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get stats: {e}")
            return {
                'file_count': 0,
                'total_size_mb': 0,
                'error': str(e)
            }

# Global instance
gridfs_storage = PermutationGridFSStorage()
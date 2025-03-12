import os
import shutil
import json
from functools import lru_cache
from typing import Dict, Any, List, Optional, BinaryIO

from utils.exceptions import StorageError
from config import settings

class StorageService:
    """
    Service for handling persistent storage operations
    """
    
    def __init__(self):
        """Initialize the storage service"""
        # Ensure base directories exist
        self.graph_output_dir = settings.GRAPH_OUTPUT_DIR
        os.makedirs(self.graph_output_dir, exist_ok=True)
        
        # Additional data directory for metadata
        self.data_dir = os.path.join(settings.TEMP_DIR, "data")
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_file(self, file_data: BinaryIO, destination: str) -> str:
        """
        Save a binary file to storage
        
        Args:
            file_data: Binary file data
            destination: Relative path where the file will be stored
            
        Returns:
            Full path to the saved file
        """
        try:
            # Ensure the destination directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            # Write the file
            with open(destination, 'wb') as f:
                shutil.copyfileobj(file_data, f)
            
            return destination
        except Exception as e:
            raise StorageError(f"Error saving file: {str(e)}")
    
    def get_file(self, file_path: str) -> BinaryIO:
        """
        Retrieve a file from storage
        
        Args:
            file_path: Path to the file
            
        Returns:
            File data as binary
        """
        try:
            if not os.path.exists(file_path):
                raise StorageError(f"File not found: {file_path}")
            
            return open(file_path, 'rb')
        except Exception as e:
            raise StorageError(f"Error retrieving file: {str(e)}")
    
    def delete_file(self, file_path: str) -> None:
        """
        Delete a file from storage
        
        Args:
            file_path: Path to the file to delete
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise StorageError(f"Error deleting file: {str(e)}")
    
    def list_files(self, directory: str) -> List[str]:
        """
        List all files in a directory
        
        Args:
            directory: Directory to list
            
        Returns:
            List of file paths
        """
        try:
            if not os.path.exists(directory):
                return []
            
            return [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f))
            ]
        except Exception as e:
            raise StorageError(f"Error listing files: {str(e)}")
    
    def save_metadata(self, project_id: str, metadata: Dict[str, Any]) -> None:
        """
        Save project metadata to storage
        
        Args:
            project_id: Unique project identifier
            metadata: Dictionary of metadata to save
        """
        try:
            metadata_file = os.path.join(self.data_dir, f"{project_id}.json")
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            raise StorageError(f"Error saving metadata: {str(e)}")
    
    def get_metadata(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve project metadata from storage
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            Dictionary of metadata or None if not found
        """
        try:
            metadata_file = os.path.join(self.data_dir, f"{project_id}.json")
            
            if not os.path.exists(metadata_file):
                return None
            
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Error retrieving metadata: {str(e)}")
    
    def delete_metadata(self, project_id: str) -> None:
        """
        Delete project metadata from storage
        
        Args:
            project_id: Unique project identifier
        """
        try:
            metadata_file = os.path.join(self.data_dir, f"{project_id}.json")
            
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
        except Exception as e:
            raise StorageError(f"Error deleting metadata: {str(e)}")

@lru_cache(maxsize=1)
def get_storage_service() -> StorageService:
    """
    Get the storage service singleton instance
    """
    return StorageService()
import os
import shutil
import tempfile
import zipfile
from typing import List, Optional
from utils.exceptions import FileServiceError
from config import settings

class FileService:
    """Service for handling file operations"""
    
    def get_code_files(self, directory: str) -> List[str]:
        """
        Get all code files in a directory
        
        Args:
            directory: Path to the directory
            
        Returns:
            List of paths to code files
        """
        code_files = []
        extensions = ('.py', '.js', '.ts', '.java', '.cs', '.go', '.rb', '.php', '.rs')
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(extensions):
                        code_files.append(os.path.join(root, file))
        except Exception as e:
            raise FileServiceError(f"Error scanning directory: {str(e)}")
        
        return code_files
    
    def read_file(self, file_path: str) -> str:
        """
        Read a file's content
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                raise FileServiceError(f"Error reading file {file_path}: {str(e)}")
        except Exception as e:
            raise FileServiceError(f"Error reading file {file_path}: {str(e)}")
    
    def extract_zip(self, zip_path: str, extract_to: Optional[str] = None) -> str:
        """
        Extract a zip file
        
        Args:
            zip_path: Path to the zip file
            extract_to: Path to extract to (creates temp dir if None)
            
        Returns:
            Path to the extracted directory
        """
        try:
            if extract_to is None:
                extract_to = tempfile.mkdtemp(dir=settings.TEMP_DIR)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            return extract_to
        except Exception as e:
            raise FileServiceError(f"Error extracting zip file: {str(e)}")
    
    def create_temp_dir(self) -> str:
        """
        Create a temporary directory
        
        Returns:
            Path to the temporary directory
        """
        try:
            return tempfile.mkdtemp(dir=settings.TEMP_DIR)
        except Exception as e:
            raise FileServiceError(f"Error creating temporary directory: {str(e)}")
    
    def cleanup_dir(self, directory: str) -> None:
        """
        Clean up a directory
        
        Args:
            directory: Path to the directory to clean up
        """
        try:
            shutil.rmtree(directory, ignore_errors=True)
        except Exception as e:
            # Log but don't raise - cleanup failures shouldn't break the app
            print(f"Warning: Failed to clean up directory {directory}: {str(e)}")
    
    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to the file
            
        Returns:
            File size in bytes
        """
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            raise FileServiceError(f"Error getting file size: {str(e)}")
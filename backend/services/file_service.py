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
        Get all code and configuration files in a directory
        
        Args:
            directory: Path to the directory
            
        Returns:
            List of paths to code files
        """
        all_files = []
        
        # Code file extensions
        code_extensions = (
            # Programming languages
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cs', 
            '.go', '.rb', '.php', '.rs', '.swift', '.kt', '.scala', '.h', '.hpp',
            
            # Web
            '.html', '.htm', '.css', '.scss', '.less', '.svg', '.json', '.xml',
            
            # Database
            '.sql', '.sqlite', '.db',
            
            # Config
            '.yml', '.yaml', '.toml', '.ini', '.conf', '.cnf', '.config', '.env',
            
            # Documentation
            '.md', '.txt', '.rst',
            
            # Scripts
            '.sh', '.bash', '.bat', '.cmd', '.ps1'
        )
        
        # Special filenames to include (without extensions)
        special_files = (
            'dockerfile', 'docker-compose', '.gitignore', 'makefile', 'readme',
            'requirements', 'setup', 'config', 'package.json', 'mydb', 'database'
        )
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Include file if it has a recognized extension
                    if file.lower().endswith(code_extensions):
                        all_files.append(file_path)
                        continue
                    
                    # Include file if it's a special file (without extension check)
                    if any(special_name in file.lower() for special_name in special_files):
                        all_files.append(file_path)
                        continue
                        
                    # Include hidden config files (like .gitignore, .env)
                    if file.startswith('.') and os.path.getsize(file_path) < 1024 * 1024:  # Limit to 1MB
                        all_files.append(file_path)
        except Exception as e:
            raise FileServiceError(f"Error scanning directory: {str(e)}")
        
        return all_files
    
    def read_file(self, file_path: str) -> str:
        """
        Read a file's content
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string
        """
        try:
            # First try UTF-8 encoding
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                # Try with latin-1 encoding if UTF-8 fails
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        return f.read()
                except Exception as e:
                    # If still fails, try to read as binary and return a placeholder for binary files
                    file_size = os.path.getsize(file_path)
                    if file_size > 1024 * 1024:  # If file is larger than 1MB
                        return f"[Binary file: {file_path}, size: {file_size/1024:.1f} KB]"
                    
                    # For smaller binary files, try to read them anyway
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        # Check if it's a text file despite encoding issues
                        if self._is_probably_text(content):
                            return content.decode('latin-1', errors='replace')
                        else:
                            return f"[Binary file: {file_path}, size: {file_size/1024:.1f} KB]"
        except Exception as e:
            raise FileServiceError(f"Error reading file {file_path}: {str(e)}")
    
    def _is_probably_text(self, content: bytes) -> bool:
        """
        Check if content is probably text by looking at byte values
        
        Args:
            content: Binary content to check
            
        Returns:
            True if content is likely text, False otherwise
        """
        # Simple heuristic: text files mostly have ASCII characters
        text_chars = len([b for b in content[:1000] if 32 <= b <= 126 or b in (9, 10, 13)])
        return text_chars / min(len(content), 1000) > 0.7
    
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
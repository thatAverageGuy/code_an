import os
import re
import json
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime

from utils.constants import SUPPORTED_CODE_EXTENSIONS

def normalize_path(path: str) -> str:
    """
    Normalize a file path for consistent handling
    
    Args:
        path: File path to normalize
        
    Returns:
        Normalized path
    """
    return os.path.normpath(path).replace('\\', '/')

def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension with leading dot
    """
    _, ext = os.path.splitext(file_path)
    return ext.lower()

def is_code_file(file_path: str) -> bool:
    """
    Check if a file is a supported code file
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is a supported code file, False otherwise
    """
    ext = get_file_extension(file_path)
    return ext in SUPPORTED_CODE_EXTENSIONS

def get_language_from_extension(file_path: str) -> Optional[str]:
    """
    Get the programming language from a file extension
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name or None if not recognized
    """
    ext = get_file_extension(file_path)
    return SUPPORTED_CODE_EXTENSIONS.get(ext)

def generate_project_id(seed: str = None) -> str:
    """
    Generate a unique project ID
    
    Args:
        seed: Optional seed for reproducible IDs
        
    Returns:
        Unique project ID
    """
    if seed:
        # Create deterministic ID from seed
        return f"project-{hashlib.md5(seed.encode()).hexdigest()[:8]}"
    else:
        # Create random ID
        return f"project-{uuid.uuid4().hex[:8]}"

def format_timestamp(dt: datetime = None) -> str:
    """
    Format a timestamp for consistent display
    
    Args:
        dt: Datetime object (uses current time if None)
        
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to ensure it's safe for file system operations
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscore
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    # Ensure the filename doesn't start with a dot
    if sanitized.startswith('.'):
        sanitized = '_' + sanitized[1:]
    
    return sanitized

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + '...'

def find_common_imports(analysis_results: Dict[str, Dict]) -> Set[str]:
    """
    Find common imports across multiple files
    
    Args:
        analysis_results: Dictionary of file analysis results
        
    Returns:
        Set of common import names
    """
    if not analysis_results:
        return set()
    
    # Get all imports for each file
    file_imports = []
    for file_path, analysis in analysis_results.items():
        if 'imports' in analysis:
            file_imports.append(set(analysis['imports'].keys()))
    
    if not file_imports:
        return set()
    
    # Find intersection of all import sets
    common_imports = set.intersection(*file_imports)
    return common_imports

def extract_function_dependencies(
    analysis_results: Dict[str, Dict]
) -> List[Tuple[str, str]]:
    """
    Extract function dependencies from analysis results
    
    Args:
        analysis_results: Dictionary of file analysis results
        
    Returns:
        List of tuples representing function call dependencies
    """
    dependencies = []
    
    for file_path, analysis in analysis_results.items():
        file_name = os.path.basename(file_path)
        
        if 'functions' in analysis:
            for func_name, details in analysis['functions'].items():
                caller = f"{file_name}:{func_name}"
                
                for called_func in details.get('calls', []):
                    dependencies.append((caller, called_func))
    
    return dependencies

def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    """
    Safely load JSON from text, handling various formats
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Parsed JSON as dictionary or None if parsing fails
    """
    try:
        # Try direct parsing
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON if embedded in text
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
    
    return None
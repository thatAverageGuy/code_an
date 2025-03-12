class BaseServiceError(Exception):
    """Base exception for service errors"""
    pass

class FileServiceError(BaseServiceError):
    """Exception raised for errors in the file service"""
    pass

class GithubServiceError(BaseServiceError):
    """Exception raised for errors in the GitHub service"""
    pass

class AnalysisError(BaseServiceError):
    """Exception raised for errors in code analysis"""
    pass

class LLMServiceError(BaseServiceError):
    """Exception raised for errors in LLM service"""
    pass

class StorageError(BaseServiceError):
    """Exception raised for errors in storage operations"""
    pass
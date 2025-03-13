from fastapi import Depends, Query
from typing import Optional

from services.file_service import FileService
from services.github_service import GithubService
from services.analysis_service import AnalysisService
from domain.entities import AnalysisOptions
from infrastructure.storage import get_storage_service
from infrastructure.logging import get_logger

# Common dependencies for FastAPI endpoints

async def get_analysis_options(
    visualization_type: Optional[str] = Query("networkx", description="Type of visualization to generate")
) -> AnalysisOptions:
    """
    Get analysis options from query parameters
    """
    return AnalysisOptions(
        visualization_type=visualization_type
    )

def get_file_service() -> FileService:
    """
    Get FileService instance
    """
    return FileService()

def get_github_service() -> GithubService:
    """
    Get GithubService instance
    """
    return GithubService()

def get_analysis_service(
    file_service: FileService = Depends(get_file_service)
) -> AnalysisService:
    """
    Get AnalysisService instance with its dependencies
    """
    return AnalysisService(file_service)

def get_storage():
    """
    Get storage service instance
    """
    return get_storage_service()

def get_application_logger():
    """
    Get application logger
    """
    return get_logger("application")
from fastapi import Depends, Query
from typing import Optional

from services.file_service import FileService
from services.github_service import GithubService
from services.analysis_service import AnalysisService
from services.llm_service import LLMService
from domain.entities import AnalysisOptions
from infrastructure.anthropic_client import get_anthropic_client
from infrastructure.storage import get_storage_service
from infrastructure.logging import get_logger

# Common dependencies for FastAPI endpoints

async def get_analysis_options(
    use_llm: bool = Query(False, description="Whether to use LLM for enhanced analysis"),
    visualization_type: str = Query("networkx", description="Type of visualization to generate")
) -> AnalysisOptions:
    """
    Get analysis options from query parameters
    """
    return AnalysisOptions(
        use_llm=use_llm,
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

def get_llm_service() -> LLMService:
    """
    Get LLMService instance
    """
    return LLMService()

def get_analysis_service(
    file_service: FileService = Depends(get_file_service),
    llm_service: LLMService = Depends(get_llm_service)
) -> AnalysisService:
    """
    Get AnalysisService instance with its dependencies
    """
    return AnalysisService(file_service, llm_service)

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
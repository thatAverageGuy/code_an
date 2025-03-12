from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Optional

from services.file_service import FileService
from services.github_service import GithubService
from services.analysis_service import AnalysisService
from services.llm_service import LLMService
from domain.entities import GithubAnalysisRequest, AnalysisResults, ErrorResponse
from utils.exceptions import GithubServiceError, AnalysisError
from config import settings

router = APIRouter()

def get_services():
    file_service = FileService()
    github_service = GithubService()
    llm_service = LLMService()
    analysis_service = AnalysisService(file_service, llm_service)
    return file_service, github_service, analysis_service

@router.post("/", response_model=AnalysisResults, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze_github_repo(
    request: GithubAnalysisRequest,
    background_tasks: BackgroundTasks,
    services: tuple = Depends(get_services)
):
    """
    Analyze a GitHub repository
    """
    file_service, github_service, analysis_service = services
    
    # Path to cloned repo
    repo_dir = None
    
    try:
        # Clone the repository
        repo_dir = github_service.clone_repository(
            github_url=str(request.github_url),
            branch=request.branch
        )
        
        # Get repo info for project identification
        repo_info = github_service.get_repository_info(str(request.github_url))
        
        # Analyze the project
        results = await analysis_service.analyze_project(
            repo_dir,
            use_llm=request.use_llm
        )
        
        # Add repository info to results
        results.project_id = repo_info["full_name"]
        
        # Schedule cleanup
        background_tasks.add_task(file_service.cleanup_dir, repo_dir)
        
        return results
    
    except GithubServiceError as e:
        # Clean up on error
        if repo_dir:
            background_tasks.add_task(file_service.cleanup_dir, repo_dir)
        
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    except AnalysisError as e:
        # Clean up on error
        if repo_dir:
            background_tasks.add_task(file_service.cleanup_dir, repo_dir)
        
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
    except Exception as e:
        # Clean up on error
        if repo_dir:
            background_tasks.add_task(file_service.cleanup_dir, repo_dir)
        
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
import os
import base64
import tempfile
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional

from services.file_service import FileService
from services.analysis_service import AnalysisService
from domain.entities import AnalysisResults, ErrorResponse
from utils.exceptions import FileServiceError, AnalysisError
from config import settings

router = APIRouter()

# Define request model for base64 encoded file upload
class Base64FileUploadRequest(BaseModel):
    file_content: str  # Base64 encoded file content
    file_name: str  # Original filename
    visualization_type: Optional[str] = "networkx"

def get_services():
    file_service = FileService()
    analysis_service = AnalysisService(file_service)
    return file_service, analysis_service

@router.post("/", response_model=AnalysisResults, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def upload_project(
    request: Base64FileUploadRequest,
    background_tasks: BackgroundTasks,
    services: tuple = Depends(get_services)
):
    """
    Upload a project file (zip) for analysis using base64 encoded content
    """
    file_service, analysis_service = services
    
    # Check file extension
    if not request.file_name.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are supported"
        )
    
    # Create a temporary directory
    temp_dir = None
    extract_dir = None
    
    try:
        # Create temp dir for the uploaded file
        temp_dir = file_service.create_temp_dir()
        file_path = os.path.join(temp_dir, request.file_name)
        
        # Decode and save the base64 encoded file
        try:
            file_content = base64.b64decode(request.file_content)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 encoding: {str(e)}"
            )
        
        # Write decoded content to file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Extract the zip file
        extract_dir = file_service.extract_zip(file_path)
        
        # Analyze the project
        results = await analysis_service.analyze_project(extract_dir)
        
        # Schedule cleanup
        background_tasks.add_task(file_service.cleanup_dir, temp_dir)
        background_tasks.add_task(file_service.cleanup_dir, extract_dir)
        
        return results
    
    except FileServiceError as e:
        # Clean up on error
        if temp_dir:
            background_tasks.add_task(file_service.cleanup_dir, temp_dir)
        if extract_dir:
            background_tasks.add_task(file_service.cleanup_dir, extract_dir)
        
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    except AnalysisError as e:
        # Clean up on error
        if temp_dir:
            background_tasks.add_task(file_service.cleanup_dir, temp_dir)
        if extract_dir:
            background_tasks.add_task(file_service.cleanup_dir, extract_dir)
        
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
    except Exception as e:
        # Clean up on error
        if temp_dir:
            background_tasks.add_task(file_service.cleanup_dir, temp_dir)
        if extract_dir:
            background_tasks.add_task(file_service.cleanup_dir, extract_dir)
        
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
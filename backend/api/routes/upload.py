import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from typing import Optional

from services.file_service import FileService
from services.analysis_service import AnalysisService
from domain.entities import AnalysisOptions, AnalysisResults, ErrorResponse
from utils.exceptions import FileServiceError, AnalysisError
from config import settings

router = APIRouter()

def get_services():
    file_service = FileService()
    analysis_service = AnalysisService(file_service)
    return file_service, analysis_service

@router.post("/", response_model=AnalysisResults, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def upload_project(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: Optional[AnalysisOptions] = Depends(),
    services: tuple = Depends(get_services)
):
    """
    Upload a project file (zip) for analysis
    """
    file_service, analysis_service = services
    
    # Check file extension
    if not file.filename.endswith(".zip"):
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
        file_path = os.path.join(temp_dir, file.filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract the zip file
        extract_dir = file_service.extract_zip(file_path)
        
        # Analyze the project
        results = await analysis_service.analyze_project(
            extract_dir,
            visualization_type=options.visualization_type
        )
        
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
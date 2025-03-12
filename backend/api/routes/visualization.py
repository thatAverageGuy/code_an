from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
import os
from typing import Optional

from config import settings
from utils.exceptions import StorageError

router = APIRouter()

@router.get("/{file_name}", responses={404: {"description": "Visualization not found"}})
async def get_visualization(file_name: str):
    """
    Retrieve a visualization file
    """
    try:
        # Ensure the filename doesn't contain path traversal
        if '..' in file_name or '/' in file_name:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )
        
        # Build the path to the visualization file
        file_path = os.path.join(settings.GRAPH_OUTPUT_DIR, file_name)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Visualization not found"
            )
        
        # Determine the content type based on the file extension
        content_type = "image/png"
        if file_name.endswith(".json"):
            content_type = "application/json"
        
        # Return the file with appropriate content type
        return FileResponse(
            path=file_path,
            media_type=content_type,
            filename=file_name
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving visualization: {str(e)}"
        )

@router.delete("/{file_name}", responses={404: {"description": "Visualization not found"}})
async def delete_visualization(file_name: str):
    """
    Delete a visualization file
    """
    try:
        # Ensure the filename doesn't contain path traversal
        if '..' in file_name or '/' in file_name:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )
        
        # Build the path to the visualization file
        file_path = os.path.join(settings.GRAPH_OUTPUT_DIR, file_name)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Visualization not found"
            )
        
        # Delete the file
        os.remove(file_path)
        
        return {"status": "success", "message": f"Visualization {file_name} deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting visualization: {str(e)}"
        )
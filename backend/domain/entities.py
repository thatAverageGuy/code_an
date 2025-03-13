from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Request models
class GithubAnalysisRequest(BaseModel):
    github_url: HttpUrl
    branch: Optional[str] = "main"
    visualization_type: str = "networkx"  
    
    class Config:
        schema_extra = {
            "example": {
                "github_url": "https://github.com/username/repo",
                "branch": "main",
                "visualization_type": "networkx"
            }
        }

class AnalysisOptions(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "visualization_type": "networkx"
            }
        }

# Response models
class ImportInfo(BaseModel):
    name: str
    source: str

class FunctionInfo(BaseModel):
    name: str
    args: List[str]
    calls: List[str]
    complexity: Optional[int] = None

class ClassInfo(BaseModel):
    name: str
    bases: List[str] = []
    methods: List[str] = []

class FileAnalysis(BaseModel):
    file_path: str
    imports: Dict[str, str] = {}
    functions: Dict[str, Dict[str, Any]] = {}
    classes: Dict[str, Dict[str, Any]] = {}
    errors: Optional[List[str]] = None

class AnalysisResults(BaseModel):
    project_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    files_analyzed: int
    structure: Dict[str, FileAnalysis]
    raw_data: Dict[str, Any] = {}
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "github-user-repo",
                "timestamp": "2025-03-12T14:30:00Z",
                "files_analyzed": 5,
                "structure": {},
                "raw_data": {
                    "nodes": [],
                    "links": []
                }
            }
        }

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: Optional[Any] = None
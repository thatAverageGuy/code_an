from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Request models
class GithubAnalysisRequest(BaseModel):
    github_url: HttpUrl
    use_llm: bool = False
    branch: Optional[str] = "main"
    
    class Config:
        schema_extra = {
            "example": {
                "github_url": "https://github.com/username/repo",
                "use_llm": True,
                "branch": "main"
            }
        }

class AnalysisOptions(BaseModel):
    use_llm: bool = False
    visualization_type: str = "networkx"  # Options: networkx, d3
    
    class Config:
        schema_extra = {
            "example": {
                "use_llm": True,
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

class VisualizationInfo(BaseModel):
    format: str
    url: str

class LLMCodeAnalysis(BaseModel):
    quality_score: int
    bugs: List[str] = []
    suggestions: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "quality_score": 7,
                "bugs": ["Potential null reference in function X"],
                "suggestions": ["Add error handling to function Y"]
            }
        }

class AnalysisResults(BaseModel):
    project_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    files_analyzed: int
    structure: Dict[str, FileAnalysis]
    visualizations: List[VisualizationInfo]
    llm_analysis: Optional[Dict[str, LLMCodeAnalysis]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "github-user-repo",
                "timestamp": "2025-03-12T14:30:00Z",
                "files_analyzed": 5,
                "structure": {},
                "visualizations": [
                    {
                        "format": "networkx",
                        "url": "/api/visualization/abc123"
                    }
                ],
                "llm_analysis": {}
            }
        }

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: Optional[Any] = None
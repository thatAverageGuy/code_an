import os
import json
import uuid
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

from domain.analyzer import CodeAnalyzerStrategy, PythonAnalyzer
from domain.visualizer import GraphVisualizerStrategy, NetworkXVisualizer, D3Visualizer
from services.file_service import FileService
from services.llm_service import LLMService
from domain.entities import AnalysisResults, VisualizationInfo, FileAnalysis
from utils.exceptions import AnalysisError
from config import settings

class AnalysisService:
    """
    Mediator that coordinates the code analysis process
    """
    
    def __init__(self, file_service: FileService, llm_service: LLMService):
        self.file_service = file_service
        self.llm_service = llm_service
        self.analyzers = {}
        self.visualizers = {}
        
        # Register default analyzers
        self.register_analyzer("py", PythonAnalyzer())
        
        # Register default visualizers
        self.register_visualizer("networkx", NetworkXVisualizer())
        self.register_visualizer("d3", D3Visualizer())
    
    def register_analyzer(self, extension: str, analyzer: CodeAnalyzerStrategy):
        """Register a code analyzer for a specific file extension"""
        self.analyzers[extension] = analyzer
    
    def register_visualizer(self, name: str, visualizer: GraphVisualizerStrategy):
        """Register a visualizer strategy"""
        self.visualizers[name] = visualizer
    
    async def analyze_project(self, 
                             project_path: str, 
                             use_llm: bool = False, 
                             visualization_type: str = "networkx") -> AnalysisResults:
        """
        Analyze a project and generate visualizations
        
        Args:
            project_path: Path to the project directory
            use_llm: Whether to use LLM for additional analysis
            visualization_type: Type of visualization to generate
            
        Returns:
            Analysis results with visualization paths
        """
        # Generate a unique project ID
        project_id = f"project-{uuid.uuid4().hex[:8]}"
        
        try:
            # Get all code files
            files = self.file_service.get_code_files(project_path)
            
            if not files:
                raise AnalysisError("No code files found in the project")
            
            # Analyze each file
            analysis_results = {}
            for file_path in files:
                extension = file_path.split('.')[-1].lower()
                if extension in self.analyzers:
                    analyzer = self.analyzers[extension]
                    content = self.file_service.read_file(file_path)
                    analysis_results[file_path] = analyzer.analyze(file_path, content)
            
            # Generate visualizations
            visualizations = []
            for viz_type, visualizer in self.visualizers.items():
                if viz_type == visualization_type or visualization_type == "all":
                    output_path = os.path.join(
                        settings.GRAPH_OUTPUT_DIR, 
                        f"{project_id}_{viz_type}.{'png' if viz_type == 'networkx' else 'json'}"
                    )
                    viz_path = visualizer.visualize(analysis_results, output_path)
                    visualizations.append(
                        VisualizationInfo(
                            format=viz_type,
                            url=f"/api/visualization/{os.path.basename(viz_path)}"
                        )
                    )
            
            # LLM analysis
            llm_analysis = None
            if use_llm and settings.ANTHROPIC_API_KEY:
                llm_analysis = {}
                # Only analyze files under a certain size limit
                for file_path in files:
                    extension = file_path.split('.')[-1].lower()
                    if extension in self.analyzers:
                        content = self.file_service.read_file(file_path)
                        if len(content) < 8000:  # Restrict to smaller files
                            result = await self.llm_service.analyze_code(content, file_path)
                            try:
                                # Try to parse the response as JSON
                                if isinstance(result, str):
                                    # Extract JSON if embedded in text
                                    import re
                                    json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
                                    if json_match:
                                        result = json_match.group(1)
                                    # Try direct parsing
                                    parsed_result = json.loads(result)
                                    llm_analysis[file_path] = parsed_result
                                else:
                                    llm_analysis[file_path] = result
                            except json.JSONDecodeError:
                                # If not valid JSON, store as raw text
                                llm_analysis[file_path] = {"raw_output": result}
            
            # Structure file analysis for response
            structured_analysis = {}
            for file_path, analysis in analysis_results.items():
                structured_analysis[file_path] = FileAnalysis(
                    file_path=file_path,
                    imports=analysis.get('imports', {}),
                    functions=analysis.get('functions', {}),
                    classes=analysis.get('classes', {}),
                    errors=[analysis.get('error')] if 'error' in analysis else None
                )
            
            # Create final results
            results = AnalysisResults(
                project_id=project_id,
                timestamp=datetime.now(),
                files_analyzed=len(files),
                structure=structured_analysis,
                visualizations=visualizations,
                llm_analysis=llm_analysis
            )
            
            return results
        
        except Exception as e:
            raise AnalysisError(f"Error during project analysis: {str(e)}")
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect the programming language based on file extension"""
        extension = file_path.split('.')[-1].lower()
        mapping = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'java': 'java',
            'cs': 'csharp',
            'go': 'go',
            'rb': 'ruby',
            'php': 'php',
            'rs': 'rust'
        }
        return mapping.get(extension)
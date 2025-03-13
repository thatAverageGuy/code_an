import os
import json
import uuid
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

from domain.analyzer import CodeAnalyzerStrategy, PythonAnalyzer
from domain.visualizer import GraphVisualizerStrategy, NetworkXVisualizer, D3Visualizer
from services.file_service import FileService
from domain.entities import AnalysisResults, VisualizationInfo, FileAnalysis
from utils.exceptions import AnalysisError
from config import settings

class AnalysisService:
    """
    Mediator that coordinates the code analysis process
    """
    
    def __init__(self, file_service: FileService):
        self.file_service = file_service
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

    async def analyze_project(self, project_path: str) -> AnalysisResults:
        """
        Analyze a project and generate data for visualization
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Analysis results with data for visualization
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
            
            # Generate visualization data for the frontend
            visualization_data = self._prepare_visualization_data(analysis_results)
            
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
            
            # Create final results with raw data
            results = AnalysisResults(
                project_id=project_id,
                timestamp=datetime.now(),
                files_analyzed=len(files),
                structure=structured_analysis,
                raw_data=visualization_data
            )
            
            return results
        
        except Exception as e:
            raise AnalysisError(f"Error during project analysis: {str(e)}")

    def _prepare_visualization_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare visualization data for the frontend
        
        Args:
            analysis_results: Analysis results by file
            
        Returns:
            Data structure for visualization
        """
        nodes = []
        links = []
        node_map = {}
        node_id = 0
        
        # Process each file's analysis
        for file_path, analysis in analysis_results.items():
            file_name = os.path.basename(file_path)
            
            # Add file as node
            nodes.append({
                "id": node_id,
                "name": file_name,
                "path": file_path,
                "type": "file"
            })
            file_node_id = node_id
            node_map[file_path] = node_id
            node_id += 1
            
            # Process functions
            if 'functions' in analysis:
                for func_name, details in analysis['functions'].items():
                    # Add function node
                    nodes.append({
                        "id": node_id,
                        "name": func_name,
                        "path": file_path,
                        "type": "function",
                        "args": details.get('args', [])
                    })
                    func_node_id = node_id
                    node_map[f"{file_path}:{func_name}"] = node_id
                    node_id += 1
                    
                    # Add link from file to function
                    links.append({
                        "source": file_node_id,
                        "target": func_node_id,
                        "type": "contains"
                    })
                    
                    # Add function call links
                    for called_func in details.get('calls', []):
                        # We'll add these links in a second pass
                        # after all nodes are created
                        links.append({
                            "source": func_node_id,
                            "target": called_func,  # This is just the name, we'll process it later
                            "type": "calls",
                            "temp": True  # Mark as temporary
                        })
            
            # Process classes
            if 'classes' in analysis:
                for class_name, details in analysis['classes'].items():
                    # Add class node
                    nodes.append({
                        "id": node_id, 
                        "name": class_name,
                        "path": file_path,
                        "type": "class",
                        "methods": details.get('methods', []),
                        "bases": details.get('bases', [])
                    })
                    class_node_id = node_id
                    node_map[f"{file_path}:{class_name}"] = node_id
                    node_id += 1
                    
                    # Add link from file to class
                    links.append({
                        "source": file_node_id,
                        "target": class_node_id,
                        "type": "contains"
                    })
        
        # Process function calls and class inheritance
        # We need a second pass because now all nodes are created
        actual_links = []
        for link in links:
            if link.get('temp', False):
                # This is a function call link, find the actual target
                source_node = nodes[link['source']]
                target_name = link['target']
                found = False
                
                # Try to find the target node
                for node in nodes:
                    if node['type'] == 'function' and node['name'] == target_name:
                        actual_links.append({
                            "source": link['source'],
                            "target": node['id'],
                            "type": "calls"
                        })
                        found = True
                        break
                
                # If not found, keep the name for frontend processing
                if not found:
                    actual_links.append({
                        "source": link['source'],
                        "target": f"unknown:{target_name}",
                        "targetName": target_name,
                        "type": "calls"
                    })
            else:
                # Regular link, keep it
                actual_links.append(link)
        
        # Add module hierarchy
        module_map = {}
        for file_path in analysis_results.keys():
            parts = file_path.split('/')
            # Build module hierarchy
            current_path = ""
            for i, part in enumerate(parts[:-1]):  # Skip the filename
                parent_path = current_path
                current_path = (current_path + "/" + part).lstrip("/")
                
                if current_path not in module_map:
                    # Create module node
                    nodes.append({
                        "id": node_id,
                        "name": part,
                        "path": current_path,
                        "type": "module"
                    })
                    module_map[current_path] = node_id
                    node_id += 1
                    
                    # Link to parent module if exists
                    if parent_path and parent_path in module_map:
                        actual_links.append({
                            "source": module_map[parent_path],
                            "target": module_map[current_path],
                            "type": "contains"
                        })
                
                # Link module to file
                if node_map.get(file_path) is not None:
                    actual_links.append({
                        "source": module_map[current_path],
                        "target": node_map[file_path],
                        "type": "contains"
                    })
        
        return {
            "nodes": nodes,
            "links": actual_links,
            "modules": list(module_map.keys())
        }

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
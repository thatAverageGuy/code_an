import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from domain.analyzer import CodeAnalyzerStrategy, PythonAnalyzer
from services.file_service import FileService
from domain.entities import AnalysisResults, FileAnalysis
from utils.exceptions import AnalysisError

class AnalysisService:
    """
    Mediator that coordinates the code analysis process
    """
    
    def __init__(self, file_service: FileService):
        self.file_service = file_service
        self.analyzers = {}
        
        # Register default analyzers
        self.register_analyzer("py", PythonAnalyzer())
    
    def register_analyzer(self, extension: str, analyzer: CodeAnalyzerStrategy):
        """Register a code analyzer for a specific file extension"""
        self.analyzers[extension] = analyzer
    
    def normalize_path(self, file_path: str) -> str:
        """
        Normalize file paths by removing temporary directory prefixes
        and standardizing path separators
        
        Args:
            file_path: The original file path
            
        Returns:
            Normalized path without temp directories
        """
        # Convert Windows path separators to forward slashes
        if '\\' in file_path:
            file_path = file_path.replace('\\', '/')
        
        # Extract the relevant part of the path
        # Remove temporary directory prefixes like /tmp/code_analyzer/github_clone_xxx/
        parts = file_path.split('/')
        if len(parts) > 3 and ('tmp' in parts or 'temp' in parts or 'code_analyzer' in parts):
            # Find the first actual project directory
            # Skip tmp, code_analyzer, and unique IDs like github_clone_xxx
            start_idx = 0
            for i, part in enumerate(parts):
                if 'github_clone_' in part or 'clone_' in part:
                    start_idx = i + 1
                    break
            
            # If we found a marker, remove everything before it
            if start_idx > 0:
                parts = parts[start_idx:]
                return '/'.join(parts)
        
        return file_path
    
    def generate_file_summary(self, file_path: str, content: str) -> str:
        """
        Generate a summary of the file content based on file type
        
        Args:
            file_path: Path to the file
            content: File content as string
            
        Returns:
            Summary of the file content
        """
        filename = os.path.basename(file_path)
        extension = filename.split('.')[-1].lower() if '.' in filename else ''
        
        # Handle empty content
        if not content or len(content.strip()) == 0:
            return "Empty file"
            
        # Handle binary content
        if content.startswith('[Binary file:'):
            return content
        
        # Different summary strategies based on file type
        if extension == 'md' or filename.lower() == 'readme':
            # For markdown, extract title and first paragraph
            lines = content.split('\n')
            title_line = next((line for line in lines if line.strip() and line.strip().startswith('#')), '')
            
            # Find first paragraph
            paragraph = ""
            in_paragraph = False
            for line in lines:
                if line.strip() and not line.strip().startswith('#') and not in_paragraph:
                    in_paragraph = True
                    paragraph += line.strip() + " "
                elif in_paragraph and line.strip():
                    paragraph += line.strip() + " "
                elif in_paragraph and not line.strip():
                    break
            
            if title_line:
                title = title_line.strip('#').strip()
                return f"Documentation: {title}\n{paragraph[:150]}..."
            else:
                return f"Documentation: {paragraph[:200]}..."
        
        elif extension in ['cnf', 'conf', 'config', 'ini', 'env'] or filename.startswith('.'):
            # For config files, show sections
            sections = []
            current_section = None
            
            for line in content.split('\n')[:20]:  # Look at first 20 lines
                line = line.strip()
                if not line or line.startswith('#') or line.startswith(';'):
                    continue
                    
                if line.startswith('[') and line.endswith(']'):
                    current_section = line
                    sections.append(current_section)
                elif '=' in line and len(sections) < 5:
                    key = line.split('=', 1)[0].strip()
                    sections.append(f"- {key}")
            
            if sections:
                return f"Configuration file with sections: {', '.join(sections[:5])}" + ("..." if len(sections) > 5 else "")
            else:
                # Just show first few lines for simple configs
                content_preview = '\n'.join(line for line in content.split('\n')[:5] if line.strip())
                return f"Configuration settings:\n{content_preview[:200]}..."
        
        elif 'db' in filename.lower() or extension == 'sql':
            # For database files
            if extension == 'sql':
                # Extract table definitions or first few statements
                tables = []
                for line in content.split('\n'):
                    if 'CREATE TABLE' in line.upper():
                        table_name = line.split('CREATE TABLE', 1)[1].strip().split('(')[0].strip('` \t\n')
                        tables.append(table_name)
                
                if tables:
                    return f"SQL database schema with tables: {', '.join(tables[:5])}" + ("..." if len(tables) > 5 else "")
                else:
                    # Just show first few lines
                    return f"SQL file:\n{content[:200]}..."
            else:
                # Binary database file
                return f"Database file: {filename}"
        
        elif extension in ['txt', 'rst']:
            # For text files, show first few lines
            lines = [line for line in content.split('\n')[:10] if line.strip()]
            if lines:
                preview = '\n'.join(lines[:3])
                return f"Text file:\n{preview[:200]}..."
            else:
                return "Empty text file"
                
        elif filename == '.gitignore':
            # For gitignore, show patterns
            patterns = [line for line in content.split('\n') if line.strip() and not line.startswith('#')]
            if patterns:
                return f"Git ignore file with {len(patterns)} patterns: {', '.join(patterns[:5])}" + ("..." if len(patterns) > 5 else "")
            else:
                return "Empty .gitignore file"
                
        elif filename == 'requirements.txt':
            # For requirements, show packages
            packages = [line.split('==')[0].strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            if packages:
                return f"Python requirements with {len(packages)} packages: {', '.join(packages[:5])}" + ("..." if len(packages) > 5 else "")
            else:
                return "Empty requirements file"
                
        else:
            # Default summary for other files
            lines = content.split('\n')
            content_preview = '\n'.join(line for line in lines[:5] if line.strip())
            return f"File preview:\n{content_preview[:200]}..."

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
            # Get all code and config files
            files = self.file_service.get_code_files(project_path)
            
            if not files:
                raise AnalysisError("No code files found in the project")
            
            # Analyze each file
            analysis_results = {}
            for file_path in files:
                extension = file_path.split('.')[-1].lower() if '.' in file_path else ''
                content = self.file_service.read_file(file_path)
                
                # Use the registered analyzer if available, or create a basic analysis for other file types
                if extension in self.analyzers:
                    analyzer = self.analyzers[extension]
                    analysis = analyzer.analyze(file_path, content)
                else:
                    # For files without registered analyzers, provide basic info
                    analysis = {
                        'imports': {},
                        'functions': {},
                        'classes': {},
                    }
                
                # Add file summary
                analysis['summary'] = self.generate_file_summary(file_path, content)
                analysis_results[file_path] = analysis
            
            # Generate visualization data for the frontend
            visualization_data = self._prepare_visualization_data(analysis_results)
            
            # Structure file analysis for response with normalized paths
            structured_analysis = {}
            for file_path, analysis in analysis_results.items():
                normalized_path = self.normalize_path(file_path)
                
                # Create FileAnalysis with the normalized path
                structured_analysis[normalized_path] = FileAnalysis(
                    file_path=normalized_path,
                    imports=analysis.get('imports', {}),
                    functions=analysis.get('functions', {}),
                    classes=analysis.get('classes', {}),
                    errors=[analysis.get('error')] if 'error' in analysis else None,
                    summary=analysis.get('summary', '')
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
            normalized_path = self.normalize_path(file_path)
            file_name = os.path.basename(normalized_path)
            
            # Determine file type for visualization
            extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
            file_type = self._get_file_type(file_name, extension)
            
            # Add file as node
            nodes.append({
                "id": node_id,
                "name": file_name,
                "path": normalized_path,
                "type": "file",
                "file_type": file_type,
                "summary": analysis.get('summary', '')
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
                        "path": normalized_path,
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
                        "path": normalized_path,
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
        
        # Add module hierarchy with normalized paths
        module_map = {}
        for file_path in analysis_results.keys():
            normalized_path = self.normalize_path(file_path)
            parts = normalized_path.split('/')
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

    def _get_file_type(self, filename: str, extension: str) -> str:
        """
        Determine the type of file based on filename and extension
        
        Args:
            filename: The name of the file
            extension: The file extension
            
        Returns:
            String indicating the file type
        """
        # Database files
        if any(db_file in filename.lower() for db_file in ['db.', 'database', '.sql', 'mydb', '.sqlite']):
            return 'database'
            
        # Config files
        if extension in ['cnf', 'conf', 'config', 'ini', 'yml', 'yaml', 'toml', 'env']:
            return 'config'
            
        # Code files by extension
        code_extensions = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'jsx': 'react',
            'tsx': 'react',
            'java': 'java',
            'c': 'c',
            'cpp': 'cpp',
            'h': 'header',
            'hpp': 'header',
            'cs': 'csharp',
            'go': 'go',
            'rb': 'ruby',
            'php': 'php',
            'rs': 'rust',
            'swift': 'swift',
            'kt': 'kotlin',
            'scala': 'scala',
        }
        
        if extension in code_extensions:
            return code_extensions[extension]
            
        # Web files
        if extension in ['html', 'htm', 'css', 'scss', 'less', 'svg', 'json', 'xml']:
            return 'web'
            
        # Documentation
        if extension in ['md', 'txt', 'rst', 'pdf', 'doc', 'docx']:
            return 'document'
            
        # Scripts
        if extension in ['sh', 'bash', 'bat', 'cmd', 'ps1']:
            return 'script'
            
        # Docker
        if 'dockerfile' in filename.lower() or filename.lower() == 'docker-compose.yml':
            return 'docker'
            
        # Git
        if filename.startswith('.git') or filename == '.gitignore':
            return 'git'
            
        # Default
        return 'other'

    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect the programming language based on file extension"""
        extension = file_path.split('.')[-1].lower() if '.' in file_path else ''
        mapping = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'jsx': 'react',
            'tsx': 'react',
            'java': 'java',
            'c': 'c',
            'cpp': 'cpp',
            'h': 'header',
            'hpp': 'header',
            'cs': 'csharp',
            'go': 'go',
            'rb': 'ruby',
            'php': 'php',
            'rs': 'rust',
            'swift': 'swift',
            'kt': 'kotlin',
            'scala': 'scala',
            'sql': 'sql',
            'yaml': 'yaml',
            'yml': 'yaml',
            'json': 'json',
            'xml': 'xml',
            'html': 'html',
            'css': 'css',
            'md': 'markdown',
            'sh': 'shell',
            'bash': 'shell',
            'env': 'config',
            'cnf': 'config',
            'conf': 'config',
            'ini': 'config',
            'toml': 'config'
        }
        return mapping.get(extension, 'other')
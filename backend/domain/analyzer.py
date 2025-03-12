import ast
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple

class CodeAnalyzerStrategy(ABC):
    """Base strategy class for analyzing code files"""
    
    @abstractmethod
    def analyze(self, file_path: str, content: str = None) -> Dict[str, Any]:
        """
        Analyze code content and return structured information
        
        Args:
            file_path: Path to the file
            content: Optional file content (if already loaded)
            
        Returns:
            Dictionary with analysis results
        """
        pass

class PythonAnalyzer(CodeAnalyzerStrategy):
    """Strategy for analyzing Python code using AST"""
    
    def analyze(self, file_path: str, content: str = None) -> Dict[str, Any]:
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as source:
                    content = source.read()
            except Exception as e:
                return {"error": str(e)}
        
        try:
            tree = ast.parse(content)
            visitor = PythonASTVisitor()
            visitor.visit(tree)
            
            return {
                "imports": visitor.imports,
                "functions": visitor.functions,
                "classes": visitor.classes,
                "calls": visitor.calls
            }
        except SyntaxError as e:
            return {"error": f"Syntax error: {str(e)}"}
        except Exception as e:
            return {"error": f"Analysis error: {str(e)}"}

class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor to extract Python code structure"""
    
    def __init__(self):
        self.imports = {}
        self.functions = {}
        self.classes = {}
        self.calls = []
    
    def visit_Import(self, node):
        for name in node.names:
            self.imports[name.asname or name.name] = name.name
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        module = node.module
        for alias in node.names:
            imported_name = alias.asname or alias.name
            self.imports[imported_name] = f"{module}.{alias.name}" if module else alias.name
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.functions[node.name] = {
            'args': [arg.arg for arg in node.args.args],
            'body': [ast.unparse(stmt) for stmt in node.body if not isinstance(stmt, ast.Pass)],
            'calls': []
        }
        
        # Find all calls within this function
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call):
                if isinstance(stmt.func, ast.Name):
                    self.functions[node.name]['calls'].append(stmt.func.id)
                    self.calls.append(stmt.func.id)
                elif isinstance(stmt.func, ast.Attribute):
                    self.functions[node.name]['calls'].append(stmt.func.attr)
                    self.calls.append(stmt.func.attr)
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
        
        self.classes[node.name] = {
            'bases': bases,
            'methods': methods
        }
        
        self.generic_visit(node)

class JavaScriptAnalyzer(CodeAnalyzerStrategy):
    """Strategy for analyzing JavaScript code"""
    
    def analyze(self, file_path: str, content: str = None) -> Dict[str, Any]:
        # Placeholder for JavaScript analysis
        # Would require a JavaScript parser like esprima
        return {"error": "JavaScript analysis not implemented yet"}
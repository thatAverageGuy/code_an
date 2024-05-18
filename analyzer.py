import ast
import os

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.imports = {}
        self.functions = {}

    def visit_ImportFrom(self, node):
        module = node.module
        for alias in node.names:
            self.imports[alias.name] = f"{module}.{alias.name}"
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.functions[node.name] = {
            'args': [arg.arg for arg in node.args.args],
            'body': [ast.dump(stmt) for stmt in node.body],  # Updated line
            'calls': []
        }
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if isinstance(call.func, ast.Attribute):
                    self.functions[node.name]['calls'].append(call.func.attr)
                elif isinstance(call.func, ast.Name):
                    self.functions[node.name]['calls'].append(call.func.id)
        self.generic_visit(node)

    def analyze(self, content=None):  # Modify the analyze method to accept an optional content argument
        if content is None:
            with open(self.filepath, "r") as source:
                tree = ast.parse(source.read())
        else:
            tree = ast.parse(content)
        self.visit(tree)
        return self.imports, self.functions

def analyze_files(files):
    all_imports = {}
    all_functions = {}
    
    if isinstance(files, dict):
        # If 'files' is a dictionary of file contents
        for file_name, file_content in files.items():
            analyzer = CodeAnalyzer(file_name)
            imports, functions = analyzer.analyze(file_content)
            all_imports[file_name] = imports
            all_functions[file_name] = functions
    elif isinstance(files, list):
        # If 'files' is a list of file paths
        for file_path in files:
            with open(file_path, "r", encoding="utf-8") as source:
                analyzer = CodeAnalyzer(file_path)
                imports, functions = analyzer.analyze(source.read())
                all_imports[file_path] = imports
                all_functions[file_path] = functions
    else:
        raise ValueError("Invalid input format. 'files' must be a dictionary or a list.")

    return all_imports, all_functions


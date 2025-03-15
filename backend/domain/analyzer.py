import ast
from abc import ABC, abstractmethod
import re
from typing import Dict, List, Any, Optional, Set

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

class JavaAnalyzer(CodeAnalyzerStrategy):
    """Strategy for analyzing Java code using regex patterns"""
    
    def analyze(self, file_path: str, content: str = None) -> Dict[str, Any]:
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as source:
                    content = source.read()
            except UnicodeDecodeError:
                try:
                    # Try with latin-1 encoding if UTF-8 fails
                    with open(file_path, "r", encoding="latin-1") as source:
                        content = source.read()
                except Exception as e:
                    return {"error": f"Error reading file with latin-1 encoding: {str(e)}"}
            except Exception as e:
                return {"error": str(e)}
        
        if not content:
            return {
                "imports": {},
                "functions": {},
                "classes": {},
                "calls": []
            }
            
        try:
            # Extract imports
            imports = {}
            import_pattern = r'import\s+(static\s+)?([\w.]+)(?:\.\*)?(?:\s+as\s+(\w+))?;'
            for match in re.finditer(import_pattern, content):
                static, package, alias = match.groups()
                if package:  # Ensure package is not None
                    if alias:
                        imports[alias] = package
                    else:
                        # Get the last part of the import as the name
                        parts = package.split('.')
                        if parts:  # Make sure parts is not empty
                            name = parts[-1]
                            imports[name] = package
            
            # Extract classes
            classes = {}
            class_pattern = r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?'
            for match in re.finditer(class_pattern, content):
                groups = match.groups()
                if not groups:
                    continue
                    
                class_name = groups[0]
                if not class_name:
                    continue
                    
                parent_class = groups[1] if len(groups) > 1 else None
                interfaces = groups[2] if len(groups) > 2 else None
                
                bases = []
                if parent_class:
                    bases.append(parent_class)
                if interfaces:
                    for interface in interfaces.split(','):
                        bases.append(interface.strip())
                
                # Find methods within class blocks
                class_content = self._extract_block_content(content, match.end())
                methods = []
                if class_content:
                    method_pattern = r'(?:public|private|protected)?\s*(?:static|final|abstract)?\s*(?:<.*>)?\s*(?:[\w<>[\],\s]+)\s+(\w+)\s*\([^)]*\)'
                    for method_match in re.finditer(method_pattern, class_content):
                        method_groups = method_match.groups()
                        if method_groups and method_groups[0]:
                            methods.append(method_groups[0])
                
                classes[class_name] = {
                    'bases': bases,
                    'methods': methods
                }
            
            # Extract functions (methods outside classes)
            functions = {}
            function_pattern = r'(?:public|private|protected)?\s*(?:static|final)?\s*(?:<.*>)?\s*(?:[\w<>[\],\s]+)\s+(\w+)\s*\(([^)]*)\)'
            for match in re.finditer(function_pattern, content):
                # Skip matches that are within classes
                if self._is_within_class(content, match.start()):
                    continue
                
                groups = match.groups()
                if not groups or len(groups) < 2:
                    continue
                    
                function_name, params_str = groups[0], groups[1]
                if not function_name:
                    continue
                
                args = []
                if params_str:
                    # Parse parameters safely
                    for param in params_str.split(','):
                        param = param.strip()
                        if param:
                            # Extract parameter name (last word)
                            param_parts = param.split()
                            if param_parts:
                                args.append(param_parts[-1])
                
                # Extract function body to find calls
                func_content = self._extract_block_content(content, match.end())
                calls = set()
                if func_content:
                    call_pattern = r'(\w+)\s*\('
                    for call_match in re.finditer(call_pattern, func_content):
                        if call_match.groups() and call_match.groups()[0]:
                            calls.add(call_match.groups()[0])
                
                functions[function_name] = {
                    'args': args,
                    'calls': list(calls)
                }
            
            all_calls = set()
            for func_data in functions.values():
                if 'calls' in func_data and func_data['calls']:
                    all_calls.update(func_data['calls'])
            
            return {
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "calls": list(all_calls)
            }
        except Exception as e:
            return {"error": f"Java analysis error: {str(e)}"}
    
    def _extract_block_content(self, content: str, start_pos: int) -> Optional[str]:
        """Extract content between { and } blocks, handling nested blocks"""
        if not content or start_pos >= len(content):
            return None
            
        depth = 0
        start_idx = None
        
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                if depth == 0:
                    start_idx = i + 1
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0 and start_idx is not None:
                    return content[start_idx:i]
        
        return None
    
    def _is_within_class(self, content: str, pos: int) -> bool:
        """Check if position is within a class declaration"""
        if not content or pos >= len(content):
            return False
            
        class_pattern = r'class\s+\w+'
        class_matches = list(re.finditer(class_pattern, content))
        
        for match in class_matches:
            class_start = match.start()
            if class_start > pos:
                continue
            
            # Find the closing brace of the class
            class_content = content[class_start:]
            depth = 0
            for i, char in enumerate(class_content):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        class_end = class_start + i
                        if pos < class_end:
                            return True
                        break
        
        return False
    
class GoAnalyzer(CodeAnalyzerStrategy):
    """Strategy for analyzing Go code using regex patterns"""
    
    def analyze(self, file_path: str, content: str = None) -> Dict[str, Any]:
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as source:
                    content = source.read()
            except Exception as e:
                return {"error": str(e)}
        
        try:
            # Extract package
            package_pattern = r'package\s+(\w+)'
            package_match = re.search(package_pattern, content)
            package_name = package_match.group(1) if package_match else ""
            
            # Extract imports
            imports = {}
            import_block_pattern = r'import\s+\(([\s\S]*?)\)'
            import_single_pattern = r'import\s+(?:"([^"]+)"|\w+\s+"([^"]+)")'
            
            # Process multi-line import blocks
            for block_match in re.finditer(import_block_pattern, content):
                import_block = block_match.group(1)
                for line in import_block.strip().split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Handle aliased imports: alias "package/path"
                    if ' ' in line:
                        alias, path = line.split(' ', 1)
                        path = path.strip('"')
                        imports[alias] = path
                    else:
                        # Regular import: "package/path"
                        path = line.strip('"')
                        # Extract the last component as the package name
                        name = path.split('/')[-1]
                        imports[name] = path
            
            # Process single-line imports
            for match in re.finditer(import_single_pattern, content):
                path = match.group(1) or match.group(2)
                name = path.split('/')[-1]
                imports[name] = path
            
            # Extract struct definitions (similar to classes)
            classes = {}
            struct_pattern = r'type\s+(\w+)\s+struct\s*\{([^}]*)\}'
            for match in re.finditer(struct_pattern, content):
                struct_name = match.group(1)
                # Go doesn't have traditional inheritance, but we'll track embedded types
                embedded_types = []
                struct_body = match.group(2)
                
                # Look for embedded types (fields without names)
                field_pattern = r'(\b\w+\b)\s*($|\n|;)'
                for field_match in re.finditer(field_pattern, struct_body):
                    embedded_types.append(field_match.group(1))
                
                classes[struct_name] = {
                    'bases': embedded_types,
                    'methods': []  # Will be populated later
                }
            
            # Extract interface definitions
            interface_pattern = r'type\s+(\w+)\s+interface\s*\{([^}]*)\}'
            for match in re.finditer(interface_pattern, content):
                interface_name = match.group(1)
                methods = []
                interface_body = match.group(2)
                
                # Extract method signatures from interface
                method_pattern = r'(\w+)\s*\([^)]*\)(?:\s*\([^)]*\))?\s*($|\n|;)'
                for method_match in re.finditer(method_pattern, interface_body):
                    methods.append(method_match.group(1))
                
                classes[interface_name] = {
                    'bases': [],
                    'methods': methods,
                    'type': 'interface'
                }
            
            # Extract functions and methods
            functions = {}
            
            # Method pattern: func (receiver Type) Name(args) (returns)
            method_pattern = r'func\s+\((\w+)\s+\*?(\w+)\)\s+(\w+)\s*\(([^)]*)\)'
            for match in re.finditer(method_pattern, content):
                receiver_name, receiver_type, method_name, args_str = match.groups()
                
                # Add this method to the struct's methods list
                if receiver_type in classes:
                    if 'methods' in classes[receiver_type]:
                        classes[receiver_type]['methods'].append(method_name)
                
                # Parse arguments
                args = []
                if args_str:
                    arg_chunks = re.findall(r'(?:^|,)\s*(?:\w+(?:\s*,\s*\w+)*)\s+[*\[\]]*\w+', args_str)
                    for chunk in arg_chunks:
                        # Extract parameter names (before the type)
                        param_names = re.findall(r'\b(\w+)\b', chunk.split()[0])
                        args.extend(param_names)
                
                # Extract function body to find calls
                func_content = self._extract_block_content(content, match.end())
                calls = set()
                if func_content:
                    # Simplified call detection
                    call_pattern = r'(\w+)\s*\('
                    for call_match in re.finditer(call_pattern, func_content):
                        calls.add(call_match.group(1))
                
                functions[f"{receiver_type}.{method_name}"] = {
                    'args': args,
                    'calls': list(calls)
                }
            
            # Function pattern: func Name(args) (returns)
            func_pattern = r'func\s+(\w+)\s*\(([^)]*)\)'
            for match in re.finditer(func_pattern, content):
                # Skip if this is already processed as a method
                if self._is_method_declaration(content, match.start()):
                    continue
                
                func_name, args_str = match.groups()
                
                # Parse arguments
                args = []
                if args_str:
                    arg_chunks = re.findall(r'(?:^|,)\s*(?:\w+(?:\s*,\s*\w+)*)\s+[*\[\]]*\w+', args_str)
                    for chunk in arg_chunks:
                        # Extract parameter names (before the type)
                        param_names = re.findall(r'\b(\w+)\b', chunk.split()[0])
                        args.extend(param_names)
                
                # Extract function body to find calls
                func_content = self._extract_block_content(content, match.end())
                calls = set()
                if func_content:
                    # Simple call detection
                    call_pattern = r'(\w+)\s*\('
                    for call_match in re.finditer(call_pattern, func_content):
                        calls.add(call_match.group(1))
                
                functions[func_name] = {
                    'args': args,
                    'calls': list(calls)
                }
            
            return {
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "calls": list(set().union(*[f.get('calls', []) for f in functions.values()], set()))
            }
        except Exception as e:
            return {"error": f"Go analysis error: {str(e)}"}
    
    def _extract_block_content(self, content: str, start_pos: int) -> Optional[str]:
        """Extract content between { and } blocks, handling nested blocks"""
        depth = 0
        start_idx = None
        
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                if depth == 0:
                    start_idx = i + 1
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0 and start_idx is not None:
                    return content[start_idx:i]
        
        return None
    
    def _is_method_declaration(self, content: str, pos: int) -> bool:
        """Check if the function declaration at pos is a method (has a receiver)"""
        # Look backward for the 'func' keyword
        line_start = content.rfind('\n', 0, pos)
        if line_start == -1:
            line_start = 0
        func_decl = content[line_start:pos].strip()
        
        # Check if it has a receiver: func (r ReceiverType)
        return '(' in func_decl and ')' in func_decl and func_decl.index('(') < func_decl.index(')')

class CppAnalyzer(CodeAnalyzerStrategy):
    """Strategy for analyzing C++ code using regex patterns"""
    
    def analyze(self, file_path: str, content: str = None) -> Dict[str, Any]:
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as source:
                    content = source.read()
            except Exception as e:
                return {"error": str(e)}
        
        try:
            # Remove C and C++ style comments
            content = self._remove_comments(content)
            
            # Extract includes (imports)
            imports = {}
            include_pattern = r'#include\s+[<"]([^">]+)[">]'
            for match in re.finditer(include_pattern, content):
                path = match.group(1)
                name = path.split('/')[-1].split('.')[0]
                imports[name] = path
            
            # Extract namespaces
            namespaces = {}
            namespace_pattern = r'namespace\s+(\w+)\s*\{'
            for match in re.finditer(namespace_pattern, content):
                namespace = match.group(1)
                namespaces[namespace] = self._extract_block_content(content, match.end() - 1)
            
            # Extract using declarations
            using_pattern = r'using\s+(?:namespace\s+)?(\w+)(?:::(\w+))?;'
            for match in re.finditer(using_pattern, content):
                namespace, element = match.groups()
                if element:
                    imports[element] = f"{namespace}::{element}"
                else:
                    imports[namespace] = namespace
            
            # Extract classes and structs
            classes = {}
            class_pattern = r'(?:class|struct)\s+(\w+)(?:\s*:\s*(?:public|protected|private)\s+(\w+))?'
            
            for match in re.finditer(class_pattern, content):
                class_name, parent_class = match.groups()
                
                bases = []
                if parent_class:
                    bases.append(parent_class)
                
                # Look for multiple inheritance
                inheritance_list_pattern = r'(?:class|struct)\s+' + re.escape(class_name) + r'\s*:([^{]+)'
                inheritance_match = re.search(inheritance_list_pattern, content)
                if inheritance_match:
                    inheritance_list = inheritance_match.group(1)
                    # Parse inheritance list
                    for inheritance in re.finditer(r'(?:public|protected|private)\s+(\w+)', inheritance_list):
                        base = inheritance.group(1)
                        if base and base != parent_class:  # Avoid duplicates
                            bases.append(base)
                
                # Extract class content
                class_pos = match.start()
                class_content = self._extract_class_content(content, class_pos)
                
                methods = []
                if class_content:
                    # Method pattern - simplified to match common cases
                    method_pattern = r'(?:virtual|static|inline)?\s*(?:[\w:~<>]+\s+)?(\w+)\s*\([^)]*\)\s*(?:const|override|final|noexcept)?\s*(?:=\s*0)?[^;]*?(?:\{|;)'
                    for method_match in re.finditer(method_pattern, class_content):
                        method_name = method_match.group(1)
                        if method_name not in ['if', 'for', 'while', 'switch'] and method_name != class_name:
                            methods.append(method_name)
                
                    # Add constructors
                    constructor_pattern = r'(?:explicit\s+)?(' + re.escape(class_name) + r')\s*\([^)]*\)[^;]*?(?:\{|:)'
                    for ctor_match in re.finditer(constructor_pattern, class_content):
                        methods.append(ctor_match.group(1))
                    
                    # Add destructors
                    destructor_pattern = r'(?:virtual\s+)?~(' + re.escape(class_name) + r')\s*\(\s*\)[^;]*?(?:\{|;)'
                    for dtor_match in re.finditer(destructor_pattern, class_content):
                        methods.append(f"~{dtor_match.group(1)}")
                
                classes[class_name] = {
                    'bases': bases,
                    'methods': methods
                }
            
            # Extract standalone functions
            functions = {}
            function_pattern = r'(?:static|inline)?\s*(?:[\w:~<>]+\s+)+(\w+)\s*\(([^)]*)\)\s*(?:const|noexcept)?\s*(?:->[\s\w:<>]+)?\s*\{'
            
            for match in re.finditer(function_pattern, content):
                function_name, args_str = match.groups()
                
                # Skip if this is likely a method inside a class
                if self._is_within_class(content, match.start()):
                    continue
                
                # Skip common control structures
                if function_name in ['if', 'for', 'while', 'switch']:
                    continue
                
                # Parse arguments
                args = []
                if args_str:
                    # Simple parameter name extraction
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        if arg:
                            # Try to extract parameter name (last word)
                            parts = arg.split()
                            if parts:
                                # Handle pointer/reference parameters
                                last_part = parts[-1]
                                if last_part.startswith('*') or last_part.startswith('&'):
                                    last_part = last_part[1:]
                                args.append(last_part)
                
                # Extract function body to find calls
                func_content = self._extract_block_content(content, match.end() - 1)
                calls = set()
                if func_content:
                    # Function call pattern
                    call_pattern = r'(\w+)\s*\('
                    for call_match in re.finditer(call_pattern, func_content):
                        calls.add(call_match.group(1))
                
                functions[function_name] = {
                    'args': args,
                    'calls': list(calls)
                }
            
            return {
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "calls": list(set().union(*[f.get('calls', []) for f in functions.values()], set()))
            }
        except Exception as e:
            return {"error": f"C++ analysis error: {str(e)}"}
    
    def _remove_comments(self, content: str) -> str:
        """Remove C and C++ style comments from the code"""
        # Remove block comments (/* ... */)
        content = re.sub(r'/\*[\s\S]*?\*/', '', content)
        
        # Remove line comments (// ...)
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        return content
    
    def _extract_block_content(self, content: str, start_pos: int) -> Optional[str]:
        """Extract content between { and } blocks, handling nested blocks"""
        depth = 0
        start_idx = None
        
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                if depth == 0:
                    start_idx = i + 1
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0 and start_idx is not None:
                    return content[start_idx:i]
        
        return None
    
    def _extract_class_content(self, content: str, class_pos: int) -> Optional[str]:
        """Extract content of a class declaration"""
        # Find the opening brace
        open_brace_pos = content.find('{', class_pos)
        if open_brace_pos == -1:
            return None
        
        return self._extract_block_content(content, open_brace_pos)
    
    def _is_within_class(self, content: str, pos: int) -> bool:
        """Check if position is within a class declaration"""
        # Find all class declarations
        class_pattern = r'(?:class|struct)\s+\w+'
        class_matches = list(re.finditer(class_pattern, content))
        
        for match in class_matches:
            class_start = match.start()
            if class_start > pos:
                continue
            
            # Find the class block boundaries
            open_brace_pos = content.find('{', class_start)
            if open_brace_pos == -1:
                continue
            
            class_content = content[open_brace_pos:]
            depth = 0
            for i, char in enumerate(class_content):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        class_end = open_brace_pos + i
                        if pos < class_end:
                            return True
                        break
        
        return False

class CAnalyzer(CppAnalyzer):
    """Strategy for analyzing C code using regex patterns"""
    
    def analyze(self, file_path: str, content: str = None) -> Dict[str, Any]:
        # C code analysis is similar to C++ with some differences
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as source:
                    content = source.read()
            except Exception as e:
                return {"error": str(e)}
        
        try:
            # Remove C style comments
            content = self._remove_comments(content)
            
            # Extract includes
            imports = {}
            include_pattern = r'#include\s+[<"]([^">]+)[">]'
            for match in re.finditer(include_pattern, content):
                path = match.group(1)
                name = path.split('/')[-1].split('.')[0]
                imports[name] = path
            
            # Extract structs (C's version of classes)
            classes = {}
            struct_pattern = r'(?:typedef\s+)?struct\s+(?:(\w+)\s*)?\{([^}]*)\}(?:\s*(\w+))?'
            for match in re.finditer(struct_pattern, content):
                pre_name, struct_body, post_name = match.groups()
                
                # Get the struct name (typedef name or declared name)
                struct_name = post_name or pre_name
                if not struct_name:
                    continue
                
                classes[struct_name] = {
                    'bases': [],  # C doesn't have inheritance
                    'methods': []  # C doesn't have methods
                }
            
            # Extract function prototypes and definitions
            functions = {}
            
            # C function pattern
            func_pattern = r'(?:static|extern)?\s*[\w\s\*]+\s+(\w+)\s*\(([^)]*)\)\s*(?:;|\{)'
            for match in re.finditer(func_pattern, content):
                func_name, args_str = match.groups()
                
                # Skip if this is a control structure
                if func_name in ['if', 'for', 'while', 'switch', 'return']:
                    continue
                
                # Parse arguments
                args = []
                if args_str and args_str.strip() != 'void':
                    # Simple parameter extraction
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        if arg:
                            # Find the parameter name (typically the last word)
                            arg_parts = re.findall(r'\b(\w+)\b', arg)
                            if arg_parts:
                                args.append(arg_parts[-1])
                
                # Check if this is a function definition (has a body)
                is_definition = match.group(0).strip().endswith('{')
                
                if is_definition:
                    # Extract function body to find calls
                    func_content = self._extract_block_content(content, match.end() - 1)
                    calls = set()
                    if func_content:
                        # Function call pattern
                        call_pattern = r'(\w+)\s*\('
                        for call_match in re.finditer(call_pattern, func_content):
                            call_name = call_match.group(1)
                            # Skip control structures
                            if call_name not in ['if', 'for', 'while', 'switch', 'sizeof']:
                                calls.add(call_name)
                else:
                    calls = []
                
                functions[func_name] = {
                    'args': args,
                    'calls': list(calls)
                }
            
            return {
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "calls": list(set().union(*[f.get('calls', []) for f in functions.values() if 'calls' in f], set()))
            }
        except Exception as e:
            return {"error": f"C analysis error: {str(e)}"}

class JavaScriptAnalyzer(CodeAnalyzerStrategy):
    """Strategy for analyzing JavaScript code using regex patterns"""
    
    def analyze(self, file_path: str, content: str = None) -> Dict[str, Any]:
        if content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as source:
                    content = source.read()
            except Exception as e:
                return {"error": str(e)}
        
        try:
            # Remove comments
            content = self._remove_comments(content)
            
            # Extract imports
            imports = {}
            
            # ES6 imports
            import_pattern = r'import\s+(?:{([^}]+)}|(\w+))\s+from\s+[\'"]([^\'"]+)[\'"]'
            for match in re.finditer(import_pattern, content):
                named_imports, default_import, module_path = match.groups()
                
                if default_import:
                    imports[default_import] = module_path
                
                if named_imports:
                    for named_import in named_imports.split(','):
                        named_import = named_import.strip()
                        
                        # Handle aliased imports: { OriginalName as AliasName }
                        if ' as ' in named_import:
                            original, alias = named_import.split(' as ')
                            imports[alias.strip()] = f"{module_path}:{original.strip()}"
                        else:
                            imports[named_import] = f"{module_path}:{named_import}"
            
            # CommonJS requires
            require_pattern = r'(?:const|let|var)?\s*(?:{\s*([^}]+)\s*}|(\w+))\s*=\s*require\s*\([\'"]([^\'"]+)[\'"]\)'
            for match in re.finditer(require_pattern, content):
                destructured_imports, variable_name, module_path = match.groups()
                
                if variable_name:
                    imports[variable_name] = module_path
                
                if destructured_imports:
                    for part in destructured_imports.split(','):
                        part = part.strip()
                        if ' as ' in part or ':' in part:
                            # Handle aliased imports: { original: alias } or { original as alias }
                            parts = part.replace(' as ', ':').split(':')
                            if len(parts) >= 2:
                                original, alias = parts[0].strip(), parts[1].strip()
                                imports[alias] = f"{module_path}:{original}"
                        else:
                            imports[part] = f"{module_path}:{part}"
            
            # Extract classes (ES6 class syntax)
            classes = {}
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{'
            for match in re.finditer(class_pattern, content):
                class_name, parent_class = match.groups()
                
                bases = []
                if parent_class:
                    bases.append(parent_class)
                
                # Extract class body to find methods
                class_content = self._extract_block_content(content, match.end() - 1)
                methods = []
                
                if class_content:
                    # Method pattern in class
                    method_pattern = r'(?:async\s+)?(?:static\s+)?(?:get|set)?\s*(\w+)\s*\([^)]*\)\s*{'
                    for method_match in re.finditer(method_pattern, class_content):
                        method_name = method_match.group(1)
                        # Skip constructor and common names that might be part of utility functions
                        if method_name != 'constructor' and method_name not in ['if', 'for', 'while']:
                            methods.append(method_name)
                
                # Add constructor if exists
                constructor_pattern = r'constructor\s*\([^)]*\)\s*{'
                if re.search(constructor_pattern, class_content):
                    methods.append('constructor')
                
                classes[class_name] = {
                    'bases': bases,
                    'methods': methods
                }
            
            # Extract React functional components
            react_component_pattern = r'(?:export\s+(?:default\s+)?)?(?:const|function)\s+(\w+)\s*=?\s*(?:\([^)]*\)|[^=]*=>\s*)'
            for match in re.finditer(react_component_pattern, content):
                component_name = match.group(1)
                
                # Simple heuristic: if it starts with an uppercase letter, it's likely a component
                if component_name and component_name[0].isupper():
                    if component_name not in classes:
                        classes[component_name] = {
                            'bases': [],
                            'methods': [],
                            'type': 'component'
                        }
            
            # Extract functions
            functions = {}
            
            # Regular and arrow functions
            function_patterns = [
                r'function\s+(\w+)\s*\(([^)]*)\)',  # Regular function declaration
                r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(?([^)]*)\)?\s*=>'  # Arrow function with declaration
            ]
            
            for pattern in function_patterns:
                for match in re.finditer(pattern, content):
                    func_name, args_str = match.groups()
                    
                    # Skip if this is a component we've already processed
                    if func_name in classes and classes[func_name].get('type') == 'component':
                        continue
                    
                    # Parse arguments
                    args = []
                    if args_str:
                        # Handle destructuring in args
                        if '{' in args_str:
                            # Extract variable names from destructuring pattern
                            destructure_pattern = r'\{\s*([^}]+)\s*\}'
                            for d_match in re.finditer(destructure_pattern, args_str):
                                destructured_args = d_match.group(1)
                                for arg in destructured_args.split(','):
                                    arg = arg.strip()
                                    if arg:
                                        # Handle aliasing in destructuring
                                        if ':' in arg:
                                            key, value = arg.split(':', 1)
                                            args.append(value.strip())
                                        else:
                                            args.append(arg)
                        else:
                            # Simple comma-separated args
                            for arg in args_str.split(','):
                                arg = arg.strip()
                                if arg:
                                    # Handle default values
                                    if '=' in arg:
                                        arg = arg.split('=')[0].strip()
                                    args.append(arg)
                    
                    # Find the function body
                    if pattern.startswith('function'):
                        # Regular function
                        func_pos = match.end()
                        open_brace_pos = content.find('{', func_pos)
                        if open_brace_pos != -1:
                            func_content = self._extract_block_content(content, open_brace_pos)
                        else:
                            func_content = None
                    else:
                        # Arrow function - more complex to find the body
                        arrow_pos = content.find('=>', match.end())
                        if arrow_pos != -1:
                            # Check if body is a block or expression
                            body_start = arrow_pos + 2
                            while body_start < len(content) and content[body_start].isspace():
                                body_start += 1
                            
                            if body_start < len(content):
                                if content[body_start] == '{':
                                    func_content = self._extract_block_content(content, body_start)
                                else:
                                    # Expression body - get to the end of the statement
                                    statement_end = content.find(';', body_start)
                                    if statement_end == -1:
                                        statement_end = content.find('\n', body_start)
                                    
                                    if statement_end != -1:
                                        func_content = content[body_start:statement_end]
                                    else:
                                        func_content = None
                        else:
                            func_content = None
                    
                    # Extract function calls
                    calls = set()
                    if func_content:
                        # Function call pattern
                        call_pattern = r'(\w+)\s*\('
                        for call_match in re.finditer(call_pattern, func_content):
                            call_name = call_match.group(1)
                            if call_name not in ['if', 'for', 'while', 'switch', 'console']:
                                calls.add(call_name)
                    
                    functions[func_name] = {
                        'args': args,
                        'calls': list(calls)
                    }
            
            # Object method definitions
            object_method_pattern = r'(\w+)\s*:\s*function\s*\(([^)]*)\)'
            for match in re.finditer(object_method_pattern, content):
                method_name, args_str = match.groups()
                
                # Parse arguments
                args = []
                if args_str:
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        if arg:
                            args.append(arg)
                
                # Extract method body
                func_pos = match.end()
                open_brace_pos = content.find('{', func_pos)
                if open_brace_pos != -1:
                    func_content = self._extract_block_content(content, open_brace_pos)
                    
                    # Extract function calls
                    calls = set()
                    if func_content:
                        call_pattern = r'(\w+)\s*\('
                        for call_match in re.finditer(call_pattern, func_content):
                            call_name = call_match.group(1)
                            if call_name not in ['if', 'for', 'while', 'switch', 'console']:
                                calls.add(call_name)
                    
                    functions[method_name] = {
                        'args': args,
                        'calls': list(calls)
                    }
            
            # Shorthand object methods in ES6
            shorthand_method_pattern = r'(\w+)\s*\(([^)]*)\)\s*{'
            for match in re.finditer(shorthand_method_pattern, content):
                method_name, args_str = match.groups()
                
                # Skip if this is already processed as a function or is within a class
                if method_name in functions or self._is_within_class(content, match.start()):
                    continue
                
                # Parse arguments
                args = []
                if args_str:
                    for arg in args_str.split(','):
                        arg = arg.strip()
                        if arg:
                            args.append(arg)
                
                # Extract function body
                func_content = self._extract_block_content(content, match.end() - 1)
                
                # Extract function calls
                calls = set()
                if func_content:
                    call_pattern = r'(\w+)\s*\('
                    for call_match in re.finditer(call_pattern, func_content):
                        call_name = call_match.group(1)
                        if call_name not in ['if', 'for', 'while', 'switch', 'console']:
                            calls.add(call_name)
                
                functions[method_name] = {
                    'args': args,
                    'calls': list(calls)
                }
            
            return {
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "calls": list(set().union(*[f.get('calls', []) for f in functions.values()], set()))
            }
        except Exception as e:
            return {"error": f"JavaScript analysis error: {str(e)}"}
    
    def _remove_comments(self, content: str) -> str:
        """Remove JavaScript comments from the code"""
        # Remove block comments (/* ... */)
        content = re.sub(r'/\*[\s\S]*?\*/', '', content)
        
        # Remove line comments (// ...)
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        return content
    
    def _extract_block_content(self, content: str, start_pos: int) -> Optional[str]:
        """Extract content between { and } blocks, handling nested blocks"""
        depth = 0
        start_idx = None
        
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                if depth == 0:
                    start_idx = i + 1
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0 and start_idx is not None:
                    return content[start_idx:i]
        
        return None
    
    def _is_within_class(self, content: str, pos: int) -> bool:
        """Check if position is within a class declaration"""
        class_pattern = r'class\s+\w+'
        class_matches = list(re.finditer(class_pattern, content))
        
        for match in class_matches:
            class_start = match.start()
            if class_start > pos:
                continue
            
            # Find the class block boundaries
            class_content = content[class_start:]
            depth = 0
            open_brace_pos = class_content.find('{')
            if open_brace_pos == -1:
                continue
            
            for i, char in enumerate(class_content[open_brace_pos:]):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        class_end = class_start + open_brace_pos + i
                        if pos < class_end:
                            return True
                        break
        
        return False
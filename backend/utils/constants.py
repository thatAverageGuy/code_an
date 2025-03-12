# File types and extensions
SUPPORTED_CODE_EXTENSIONS = {
    # Python
    ".py": "python",
    
    # JavaScript/TypeScript
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    
    # Java
    ".java": "java",
    
    # C#
    ".cs": "csharp",
    
    # Go
    ".go": "go",
    
    # Ruby
    ".rb": "ruby",
    
    # PHP
    ".php": "php",
    
    # Rust
    ".rs": "rust",
    
    # C/C++
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp"
}

# Visualization types
VISUALIZATION_TYPES = {
    "networkx": "NetworkX graph visualization",
    "d3": "D3.js interactive visualization"
}

# LLM analysis parameters
LLM_ANALYSIS_MAX_FILE_SIZE = 8000  # Maximum file size for LLM analysis in bytes
LLM_PROMPT_TEMPLATE = """
Please analyze this {language} code file and provide insights:
- Code quality assessment (1-10 score)
- Potential bugs or issues
- Suggestions for improvement

File: {file_path}

```{language}
{code}
```

Format your response as JSON with exactly these keys only: quality_score (integer), bugs (array of strings), suggestions (array of strings)
"""

# API rate limiting
API_RATE_LIMIT = 100  # requests per minute
API_RATE_LIMIT_BURST = 20  # burst limit

# Analysis constants
MAX_ANALYSIS_DEPTH = 5  # Maximum depth for recursive analysis
MAX_FILES_PER_ANALYSIS = 100  # Maximum number of files to analyze in one request
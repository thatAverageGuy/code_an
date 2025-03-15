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
    ".cc": "cpp",
    ".cxx": "cpp"
}

# Visualization types
VISUALIZATION_TYPES = {
    "networkx": "NetworkX graph visualization",
    "d3": "D3.js interactive visualization"
}

# API rate limiting
API_RATE_LIMIT = 100  # requests per minute
API_RATE_LIMIT_BURST = 20  # burst limit

# Analysis constants
MAX_ANALYSIS_DEPTH = 5  # Maximum depth for recursive analysis
MAX_FILES_PER_ANALYSIS = 100  # Maximum number of files to analyze in one request

# Visualization types
VISUALIZATION_TYPES = {
    "networkx": "NetworkX graph visualization",
    "d3": "D3.js interactive visualization"
}


# Language specific style classes for syntax highlighting
LANGUAGE_CSS_CLASSES = {
    "python": "language-python",
    "javascript": "language-javascript",
    "typescript": "language-typescript",
    "java": "language-java",
    "c": "language-c",
    "cpp": "language-cpp",
    "go": "language-go",
    "ruby": "language-ruby",
    "php": "language-php",
    "rust": "language-rust",
    "csharp": "language-csharp"
}

# File icon mappings by extension
FILE_ICONS = {
    # Python
    ".py": "🐍",
    
    # JavaScript/TypeScript
    ".js": "📜",
    ".jsx": "⚛️",
    ".ts": "📜",
    ".tsx": "⚛️",
    
    # Java
    ".java": "☕",
    
    # C#
    ".cs": "🔷",
    
    # Go
    ".go": "🐹",
    
    # Ruby
    ".rb": "💎",
    
    # PHP
    ".php": "🐘",
    
    # Rust
    ".rs": "⚙️",
    
    # C/C++
    ".c": "🔨",
    ".h": "📐",
    ".cpp": "🔧",
    ".hpp": "📐",
    ".cc": "🔧",
    ".cxx": "🔧",
    
    # Web
    ".html": "🌐",
    ".css": "🎨",
    ".scss": "🎨",
    ".sass": "🎨",
    ".less": "🎨",
    
    # Data
    ".json": "📊",
    ".xml": "📊",
    ".yaml": "📊",
    ".yml": "📊",
    
    # Documentation
    ".md": "📝",
    ".txt": "📄",
    ".pdf": "📄",
    ".doc": "📄",
    ".docx": "📄",
    
    # Config
    ".config": "⚙️",
    ".conf": "⚙️",
    ".ini": "⚙️",
    ".env": "⚙️",
    
    # Other
    ".sql": "🗄️",
    ".db": "🗄️",
    ".sqlite": "🗄️",
    ".gitignore": "📎",
    ".dockerignore": "🐳",
    "dockerfile": "🐳",
    "makefile": "🔨",
    "readme": "📖"
}
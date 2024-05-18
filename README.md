# Code Analyzer

Code Analyzer is a tool for analyzing Python projects to visualize their dependencies and generate a summary of their structure.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Code Analyzer is a Python-based tool that helps developers understand the structure of their Python projects. It analyzes Python files to identify dependencies between functions and modules, and then generates a visualization of the project's structure as a directed graph. Additionally, it provides a summary of the project's imports and function calls.

## Features

- Analyze Python projects to generate dependency graphs
- Visualize project structure using NetworkX and Matplotlib
- Generate summaries of project imports and function calls
- Support for analyzing both local projects and GitHub repositories


## Installation

1. Clone the repository:

```
git clone https://github.com/your-username/code-analyzer.git
```

2. Navigate to the project directory:

```
cd code-analyzer
```

3. Install dependencies:

```
pip install -r requirements.txt
```

## Usage

To use the Code Analyzer tool, you can either upload a Python project zip file or provide a GitHub repository URL.

To analyze a local project:

1. Start the Flask server:

```
python webapp.py
```

2. Use the `/upload` endpoint to upload a zip file containing your Python project.

To analyze a GitHub repository:

1. Start the Flask server:

```
python webapp.py
```

2. Use the `/github` endpoint to provide the GitHub repository URL.

## API Endpoints

- `/upload` (POST): Upload a zip file containing a Python project for analysis.
- `/github` (POST): Provide a GitHub repository URL for analysis.

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvement, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

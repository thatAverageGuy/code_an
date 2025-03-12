import json
from typing import Dict, Any, List
from infrastructure.anthropic_client import get_anthropic_client
from utils.exceptions import LLMServiceError

class LLMService:
    """
    Facade for LLM-based code analysis
    """
    
    def __init__(self):
        self.anthropic_client = get_anthropic_client()
    
    async def analyze_code(self, code: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze code using Claude
        
        Args:
            code: Source code to analyze
            file_path: Path to the file
            
        Returns:
            Structured analysis from Claude
        """
        try:
            result = await self.anthropic_client.analyze_code(code, file_path)
            return self._process_llm_response(result)
        except Exception as e:
            raise LLMServiceError(f"Error analyzing code with LLM: {str(e)}")
    
    async def analyze_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple files
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            Dictionary mapping file paths to analysis results
        """
        results = {}
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip files that are too large
                if len(content) < 8000:
                    results[file_path] = await self.analyze_code(content, file_path)
                else:
                    results[file_path] = {"error": "File too large for LLM analysis"}
            except Exception as e:
                results[file_path] = {"error": str(e)}
        
        return results
    
    def _process_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Process and normalize the LLM response
        
        Args:
            response: Raw response from the LLM
            
        Returns:
            Structured data from the response
        """
        if isinstance(response, dict):
            # Already a dict (from error handling)
            return response
        
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            # Try to parse the response as JSON
            parsed_response = json.loads(response)
            
            # Ensure the response has the expected structure
            normalized_response = {
                "quality_score": parsed_response.get("quality_score", 0),
                "bugs": parsed_response.get("bugs", []),
                "suggestions": parsed_response.get("suggestions", [])
            }
            
            return normalized_response
        except json.JSONDecodeError:
            # If not valid JSON, return the raw text
            return {"raw_output": response}
import os
import anthropic
from functools import lru_cache
from config import settings

class AnthropicClient:
    """
    Singleton class for Anthropic API client
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnthropicClient, cls).__new__(cls)
            cls._instance.client = anthropic.Anthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
        return cls._instance
    
    async def analyze_code(self, code: str, file_path: str):
        """
        Analyze code using Claude
        
        Args:
            code: Source code to analyze
            file_path: Path to the file
            
        Returns:
            Structured analysis from Claude
        """
        # Get file extension
        extension = file_path.split('.')[-1].lower()
        language = self._get_language(extension)
        
        prompt = f"""
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
        
        try:
            response = await self.client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            # Return the text content
            return response.content[0].text
        except anthropic.APIError as e:
            return {"error": f"Anthropic API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def _get_language(self, extension: str) -> str:
        """Map file extension to language name"""
        mapping = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'java': 'java',
            'cs': 'csharp',
            'go': 'go',
            'rb': 'ruby',
            'php': 'php',
            'rs': 'rust',
            'cpp': 'cpp',
            'c': 'c',
            'h': 'c',
            'hpp': 'cpp'
        }
        return mapping.get(extension, 'text')

@lru_cache(maxsize=1)
def get_anthropic_client():
    """
    Get the Anthropic client singleton instance
    """
    return AnthropicClient()
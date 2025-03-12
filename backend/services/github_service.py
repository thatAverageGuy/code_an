import os
import tempfile
from git import Repo, GitCommandError
from github import Github, GithubException
from typing import Optional
from utils.exceptions import GithubServiceError
from config import settings

class GithubService:
    """
    Adapter for GitHub API operations
    """
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.github = Github(self.token) if self.token else Github()
    
    def clone_repository(self, github_url: str, branch: str = "main") -> str:
        """
        Clone a GitHub repository
        
        Args:
            github_url: URL of the GitHub repository
            branch: Branch to clone
            
        Returns:
            Path to the cloned repository
        """
        try:
            # Normalize GitHub URL
            if not github_url.endswith(".git"):
                if self.token:
                    # Extract owner/repo from URL
                    repo_parts = github_url.replace("https://github.com/", "").split("/")
                    if len(repo_parts) >= 2:
                        owner_repo = "/".join(repo_parts[:2])
                        repo = self.github.get_repo(owner_repo)
                        # Add token to URL for private repos
                        clone_url = repo.clone_url.replace(
                            'https://', f'https://{self.token}@'
                        )
                    else:
                        raise GithubServiceError("Invalid GitHub URL format")
                else:
                    repo_name = github_url.split("https://github.com/")[-1]
                    repo = self.github.get_repo(repo_name)
                    clone_url = repo.clone_url
            else:
                clone_url = github_url
            
            # Create temp directory for clone
            temp_dir = tempfile.mkdtemp(prefix="github_clone_", dir=settings.TEMP_DIR)
            
            # Clone the repository
            repo = Repo.clone_from(clone_url, temp_dir)
            
            # Checkout specified branch if not the default
            if branch != "main" and branch != "master":
                repo.git.checkout(branch)
            
            return temp_dir
        
        except GithubException as e:
            raise GithubServiceError(f"GitHub API error: {str(e)}")
        except GitCommandError as e:
            raise GithubServiceError(f"Git command error: {str(e)}")
        except Exception as e:
            raise GithubServiceError(f"Error cloning repository: {str(e)}")
    
    def get_repository_info(self, github_url: str) -> dict:
        """
        Get information about a GitHub repository
        
        Args:
            github_url: URL of the GitHub repository
            
        Returns:
            Dictionary with repository information
        """
        try:
            # Extract owner/repo from URL
            repo_parts = github_url.replace("https://github.com/", "").split("/")
            if len(repo_parts) >= 2:
                owner_repo = "/".join(repo_parts[:2])
                repo = self.github.get_repo(owner_repo)
                
                return {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "default_branch": repo.default_branch
                }
            else:
                raise GithubServiceError("Invalid GitHub URL format")
        
        except GithubException as e:
            raise GithubServiceError(f"GitHub API error: {str(e)}")
        except Exception as e:
            raise GithubServiceError(f"Error getting repository info: {str(e)}")
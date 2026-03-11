import os
import re
import logging
import subprocess
from pathlib import Path

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def is_valid_github_url(repo_url: str) -> bool:
    """
    Validates if the provided URL is a structurally valid GitHub repository URL.
    Handles deep links by normalizing them to the root.
    """
    normalized_url = normalize_github_url(repo_url)
    github_url_pattern = re.compile(
        r"^(https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?|"
        r"git@github\.com:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git)$"
    )
    return bool(github_url_pattern.match(normalized_url))

def normalize_github_url(url: str) -> str:
    """
    Normalizes a GitHub URL to its root repository form.
    e.g., https://github.com/user/repo/tree/master/folder -> https://github.com/user/repo
    """
    if "github.com" not in url:
        return url
        
    # Extract just the owner and repo part
    parts = url.split("github.com/")
    if len(parts) > 1:
        path_parts = parts[1].split("/")
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1].replace(".git", "") # stip trailing .git if present just in case
            return f"https://github.com/{owner}/{repo}"
            
    return url

def clone_repository(repo_url: str, project_id: str) -> str:
    """
    Clones a GitHub repository into a temporary local directory.
    Uses a shallow clone (--depth 1) for performance.
    
    Args:
        repo_url (str): The GitHub repository URL.
        project_id (str): A unique identifier for this cloning operation.
        
    Returns:
        str: The absolute path to the local cloned repository.
        
    Raises:
        ValueError: If the repository URL is invalid.
        RuntimeError: If the cloning process fails.
    """
    if not is_valid_github_url(repo_url):
        logger.error(f"Invalid GitHub URL provided: {repo_url}")
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
        
    original_url = repo_url
    repo_url = normalize_github_url(repo_url)
    
    if original_url != repo_url:
        logger.info(f"Normalized deep link '{original_url}' to root repo '{repo_url}'")
        
    # Construct the base temp directory path from the current working directory
    base_temp_dir = Path("temp")
    
    # Path where the specific project will be cloned
    clone_target_path = base_temp_dir / project_id
    
    # Ensure the parent temp directory exists
    base_temp_dir.mkdir(parents=True, exist_ok=True)
    
    # If the target directory already exists and isn't empty, handle it 
    # (for simplicity here, we assume a fresh clone is needed or we might clear it)
    if clone_target_path.exists() and any(clone_target_path.iterdir()):
        logger.warning(f"Target directory {clone_target_path} already exists and is not empty. "
                       f"Assuming it was previously cloned.")
        return str(clone_target_path.resolve())

    logger.info(f"Initiating shallow clone of {repo_url} into {clone_target_path}")
    
    try:
        # Construct the git clone command
        clone_command = [
            "git", "clone", 
            "--depth", "1", 
            repo_url, 
            str(clone_target_path)
        ]
        
        # Execute the git command
        result = subprocess.run(
            clone_command,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Successfully cloned repository for project: {project_id}")
        logger.debug(f"Git execution output: {result.stdout}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository {repo_url}.")
        logger.error(f"Git error output: {e.stderr}")
        raise RuntimeError(f"Failed to clone repository: {e.stderr}") from e
    except FileNotFoundError as e:
        logger.error("Git executable not found. Ensure Git is installed and in the system PATH.")
        raise RuntimeError("Git is not installed on the system.") from e
        
    return str(clone_target_path.resolve())

if __name__ == "__main__":
    # Small manual test case for verifying functionality
    test_url = "https://github.com/octocat/Hello-World"
    test_id = "test_project_123"
    
    try:
        local_path = clone_repository(test_url, test_id)
        print(f"Test Successful! Cloned to: {local_path}")
    except Exception as e:
        print(f"Test Failed: {e}")

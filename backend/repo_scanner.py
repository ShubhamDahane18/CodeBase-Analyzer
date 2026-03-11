import os
import logging
from pathlib import Path
from typing import List

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants for scanning filters
IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "env",
    "dist",
    "build",
    "__pycache__" # Added Python cache for completeness
}

ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp"
}

# 200KB in bytes
MAX_FILE_SIZE_BYTES = 200 * 1024  

def scan_repository(repo_path: str) -> List[str]:
    """
    Scans a cloned repository directory to find code files suitable for analysis.
    
    Filters out ignored directories, invalid file extensions, and files 
    exceeding the maximum allowed file size.
    
    Args:
        repo_path (str): The absolute or relative path to the cloned repository.
        
    Returns:
        List[str]: A list of absolute file paths to the valid code files.
        
    Raises:
        FileNotFoundError: If the provided repo_path does not exist or is not a directory.
    """
    base_path = Path(repo_path)
    
    if not base_path.exists():
        logger.error(f"Repository path does not exist: {base_path}")
        raise FileNotFoundError(f"Repository path not found: {base_path}")
        
    if not base_path.is_dir():
        logger.error(f"Provided path is not a directory: {base_path}")
        raise FileNotFoundError(f"Path is not a directory: {base_path}")

    logger.info(f"Starting repository scan at: {base_path.resolve()}")
    valid_files: List[str] = []
    
    # os.walk provides a clean way to traverse directories and skip ignored ones
    for root, dirs, files in os.walk(base_path):
        current_dir = Path(root)
        
        # 1. Filter out ignored directories
        # Modifying the 'dirs' list in-place tells os.walk to skip traversing them
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
        
        for file in files:
            file_path = current_dir / file
            
            # 2. Check for allowed extensions
            if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
                
            # 3. Check for file size
            try:
                # getsize() returns bytes
                file_size = os.path.getsize(file_path)
                
                if file_size > MAX_FILE_SIZE_BYTES:
                    logger.debug(f"Skipping {file_path.name}: Exceeds size limit ({file_size / 1024:.2f} KB)")
                    continue
                    
                # If all checks pass, add the absolute path mapping
                valid_files.append(str(file_path.resolve()))
                
            except OSError as e:
                # Catch cases where a file might have been deleted mid-scan, or permission errors
                logger.warning(f"Could not access file {file_path}: {e}")

    logger.info(f"Scan complete. Found {len(valid_files)} valid code files.")
    return valid_files

if __name__ == "__main__":
    # Small manual test case for verifying functionality
    # First, let's create a mock directory structure using pathlib
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_repo = Path(temp_dir) / "test_repo"
        test_repo.mkdir()
        
        # Create valid files
        (test_repo / "main.py").write_text("print('hello')")
        (test_repo / "app.js").write_text("console.log('hello')")
        
        # Create ignored folder with a valid extension file inside
        node_modules = test_repo / "node_modules"
        node_modules.mkdir()
        (node_modules / "library.js").write_text("console.log('ignored')")
        
        # Create an invalid extension file
        (test_repo / "notes.txt").write_text("Some text")
        
        # Create a giant file
        giant_file = test_repo / "giant.py"
        with open(giant_file, "wb") as f:
            f.write(b"0" * (MAX_FILE_SIZE_BYTES + 10)) # Just over 200KB
            
        print("Testing Scanner Module:")
        results = scan_repository(str(test_repo))
        
        print("\nResults found:")
        for res in results:
            print(f" - {res}")
            
        assert len(results) == 2, f"Expected 2 files, found {len(results)}"
        print("\nTest Pasased!")

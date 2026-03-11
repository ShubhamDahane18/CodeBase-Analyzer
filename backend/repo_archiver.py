import os
import shutil
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_docs_archive(project_path: str) -> str:
    """
    Compresses the generated MkDocs documentation ('site' folder) 
    into a downloadable ZIP archive ('docs.zip').
    
    Args:
        project_path (str): The root directory where the documentation site was built 
                            (must contain the generated 'site' nested folder).
                            
    Returns:
        str: The absolute path to the generated ZIP file.
        
    Raises:
        FileNotFoundError: If the 'site' folder does not exist within the project_path.
        RuntimeError: If the zipping process fails.
    """
    base_path = Path(project_path)
    site_dir = base_path / "site"
    
    # Path where the output zip will be placed (we omit the .zip extension here, 
    # shutil.make_archive adds it automatically based on the format specified)
    zip_target_path = base_path / "docs"
    
    # Final expected output file path for validation
    final_zip_file = base_path / "docs.zip"

    if not site_dir.exists() or not site_dir.is_dir():
        logger.error(f"Cannot create archive. The 'site' directory does not exist at: {site_dir}")
        raise FileNotFoundError(f"Generated site directory not found at: {site_dir}")

    logger.info(f"Initiating ZIP archive creation for {site_dir}...")

    try:
        # Create a ZIP file named "docs.zip" inside the project_path,
        # containing the contents of the 'site' directory.
        shutil.make_archive(
            base_name=str(zip_target_path), 
            format="zip", 
            root_dir=str(site_dir)
        )
        
        # Verify the file was actually created
        if not final_zip_file.exists():
            raise RuntimeError("Make archive returned successfully, but docs.zip was not found.")
            
        logger.info(f"Successfully created documentation archive at {final_zip_file}")
        
    except Exception as e:
        logger.error(f"Failed to create ZIP archive: {e}")
        raise RuntimeError(f"Failed to generate docs.zip: {e}") from e

    return str(final_zip_file.resolve())

if __name__ == "__main__":
    # Small test case simulating the Archiving module
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_path = Path(temp_dir) / "test_project_123"
        test_project_path.mkdir()
        
        # Mocking the `site` folder generated in the previous step
        mock_site_dir = test_project_path / "site"
        mock_site_dir.mkdir()
        
        # Write some fake HTML content to zip up
        (mock_site_dir / "index.html").write_text("<html><body><h1>Hello World</h1></body></html>")
        
        mock_assets_dir = mock_site_dir / "assets"
        mock_assets_dir.mkdir()
        (mock_assets_dir / "style.css").write_text("body { color: red; }")
        
        print(f"Testing Archiver in: {test_project_path}...\n")
        
        try:
            zip_path = create_docs_archive(str(test_project_path))
            print(f"Test Successful! ZIP archive generated at: {zip_path}")
            
            # Simple validation to check file size > 0
            file_size_bytes = os.path.getsize(zip_path)
            print(f"Generated ZIP size: {file_size_bytes} bytes")
            assert file_size_bytes > 0, "ZIP file is empty"
            
        except Exception as e:
            print(f"Test Failed: {e}")

import os
import uuid
import logging
import argparse
from repo_cloner import clone_repository
from repo_scanner import scan_repository
from repo_parser import parse_code_file
from repo_doc_gen import generate_documentation
from repo_mkdocs import build_docs
from repo_archiver import create_docs_archive

# Configure logging for the main orchestrator
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_doc_generation(repo_url: str, project_id: str = None) -> str:
    """
    Main orchestration pipeline that:
    1. Clones a GitHub repo
    2. Scans for valid code
    3. Parses the abstract syntax
    4. Generates Markdown via LLM
    5. Builds static MkDocs HTML
    6. Archives it as docs.zip
    
    Returns the absolute path to the generated zip file.
    """
    if not project_id:
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        
    logger.info(f"Starting AI Documentation Pipeline for {repo_url}")
    logger.info(f"Assigned Project ID: {project_id}")

    try:
        # Step 1: Clone Repository
        logger.info("\n--- STEP 1: Cloning Repository ---")
        cloned_path = clone_repository(repo_url, project_id)
        logger.info(f"Repository cloned to: {cloned_path}")

        # Step 2: Scan Repository
        logger.info("\n--- STEP 2: Scanning Repository ---")
        valid_files = scan_repository(cloned_path)
        logger.info(f"Scan complete. Found {len(valid_files)} valid code files.")

        if not valid_files:
            logger.warning("No valid code files found. Pipeline terminating early.")
            return

        # Step 3 & 4: Parse Code & Generate Documentation
        logger.info("\n--- STEP 3 & 4: Parsing AST & Generating Markdown ---")
        docs_content = {}
        # We limit the number of files generated in this orchestrator to avoid giant token loops
        # Or you can remove `[:10]` to process the entire repo instead.
        max_files_to_process = 10 
        files_to_process = valid_files[:max_files_to_process]
        
        logger.info(f"Processing top {len(files_to_process)} files to build documentation...")
        
        for file_path in files_to_process:
            # Parse the tree
            parsed_data = parse_code_file(file_path)
            
            # Skip empty parses
            if not parsed_data.get("functions") and not parsed_data.get("classes"):
                logger.debug(f"Skipping {parsed_data['file']}: No functions or classes found.")
                continue
                
            # Generate the Mocked output
            markdown_output = generate_documentation(parsed_data)
            
            # Store it associating with the original file name
            docs_content[parsed_data["file"]] = markdown_output

        if not docs_content:
             logger.warning("No significant code structures found to document. Terminating.")
             return

        # Step 5: Build MkDocs Site 
        logger.info("\n--- STEP 5: Building MkDocs Site ---")
        # We output to the cloned path root for this project
        # e.g.: temp/project_abc123/site
        output_dir = cloned_path
        
        site_path = build_docs(output_dir, docs_content)
        logger.info(f"MkDocs site built successfully at: {site_path}")

        # Step 6: Create Downloadable Archive
        logger.info("\n--- STEP 6: Creating ZIP Archive ---")
        zip_path = create_docs_archive(output_dir)
        logger.info(f"Documentation archive ready at: {zip_path}")

        logger.info("\n🎉 Pipeline Execution Complete! 🎉")
        logger.info(f"-> You can view the site locally by opening: {os.path.join(site_path, 'index.html')}")
        logger.info(f"-> You can download the zipped archive here: {zip_path}")
        
        return zip_path
        
    except Exception as e:
        logger.error(f"Pipeline failed with an error: {e}", exc_info=True)
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Documentation Pipeline Runner")
    parser.add_argument("repo_url", nargs="?", default="https://github.com/haghish/Chase", help="The GitHub repository URL to process")
    
    args = parser.parse_args()
    
    run_doc_generation(args.repo_url)

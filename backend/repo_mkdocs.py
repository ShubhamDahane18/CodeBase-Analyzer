import os
import yaml
import logging
import subprocess
from pathlib import Path
from typing import List, Dict

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def build_docs(project_path: str, docs_content: Dict[str, str]) -> str:
    """
    Takes generated Markdown content, creates a MkDocs folder structure,
    generates a mkdocs.yml file, and builds the static site.
    
    Args:
        project_path (str): The root directory where the documentation site should be built.
                            For isolation, this is typically under `temp/{project_id}/output`.
        docs_content (Dict[str, str]): A dictionary mapping the original file name 
                                       (e.g., "auth.py") to its generated Markdown string.
                                       
    Returns:
        str: The absolute path to the generated static `site/` folder.
        
    Raises:
        RuntimeError: If MkDocs fails to build the site.
    """
    base_path = Path(project_path)
    docs_dir = base_path / "docs"
    site_dir = base_path / "site"
    mkdocs_file = base_path / "mkdocs.yml"
    
    # 1. Create docs/ directory
    logger.info(f"Creating MkDocs structure in {base_path}")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Save Markdown files inside docs/
    nav_items = []
    
    # Always create a root index.md
    index_path = docs_dir / "index.md"
    nav_items.append({"Project Overview": "index.md"})
    
    # Write the dynamically generated documents
    for file_name, markdown_content in docs_content.items():
        # Clean the file name to have a .md extension (e.g., auth.py -> auth.md)
        safe_name = Path(file_name).with_suffix('.md').name
        output_path = docs_dir / safe_name
        
        output_path.write_text(markdown_content, encoding="utf-8")
        logger.debug(f"Saved {safe_name} to {docs_dir}")
        
        # Add to the navigation list
        # E.g., auth.py -> Auth
        nav_title = Path(file_name).stem.replace("_", " ").title()
        nav_items.append({nav_title: safe_name})
        
    # 3. Generate mkdocs.yml file automatically
    mkdocs_config = {
        "site_name": f"AI Documentation - {base_path.name}",
        "theme": {
            "name": "material" # A very popular and clean MkDocs theme
        },
        "nav": nav_items
    }
    
    with open(mkdocs_file, "w", encoding="utf-8") as f:
        yaml.dump(mkdocs_config, f, sort_keys=False)
        f.write("\nmarkdown_extensions:\n  - pymdownx.superfences:\n      custom_fences:\n        - name: mermaid\n          class: mermaid\n          format: !!python/name:pymdownx.superfences.fence_code_format\n")

        
    logger.info("Generated mkdocs.yml configuration")

    # 4. Run `mkdocs build` to generate the static site
    logger.info("Running `mkdocs build`...")
    try:
        # Run mkdocs build with the specific config file, outputting to site_dir
        result = subprocess.run(
            ["mkdocs", "build", "--config-file", str(mkdocs_file), "--site-dir", str(site_dir)],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Successfully built static site at {site_dir}")
        logger.debug(f"MkDocs Output: {result.stdout}")
        
    except FileNotFoundError as e:
        logger.error("MkDocs is not installed or not in PATH. Please run `pip install mkdocs mkdocs-material`.")
        raise RuntimeError("MkDocs is not installed.") from e
    except subprocess.CalledProcessError as e:
        logger.error(f"MkDocs build failed. Error output:\n{e.stderr}")
        raise RuntimeError(f"Failed to build MkDocs site: {e.stderr}") from e
        
    return str(site_dir.resolve())


if __name__ == "__main__":
    # Small test case simulating the MkDocs compilation after generation
    import tempfile
    
    mock_docs_content = {
        "auth.py": "# Module Overview\n\nHandles user authentication.\n\n## Classes\n`AuthManager`\n",
        "database.py": "# Module Overview\n\nHandles database connections and pooling.",
        "utils.js": "# Module Overview\n\nHelper functions for the frontend."
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_path = Path(temp_dir) / "test_project_docs"
        
        print(f"Testing MkDocs Builder in: {test_project_path}...\n")
        
        try:
            site_path = build_docs(str(test_project_path), mock_docs_content)
            print(f"Test Successful! Static HTML site created directly in: {site_path}")
            
            # Verify the output
            print("\nListing generated files in site directory:")
            for root, dirs, files in os.walk(site_path):
                level = root.replace(site_path, '').count(os.sep)
                indent = ' ' * 4 * (level)
                print(f"{indent}{os.path.basename(root)}/")
                sub_indent = ' ' * 4 * (level + 1)
                for f in files:
                    # Just print top level HTML files to keep output clean
                    if f.endswith('.html') and level == 0:
                        print(f"{sub_indent}{f}")
        except Exception as e:
            print(f"Test Failed: {e}")

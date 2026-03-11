import os
import sys
import uuid
import yaml
import logging
import argparse
import subprocess
from pathlib import Path

# Import existing modules
from repo_cloner import clone_repository
from repo_scanner import scan_repository, ALLOWED_EXTENSIONS
from repo_parser import parse_code_file
from repo_doc_gen import (
    generate_documentation,
    generate_file_fallback,
    generate_directory_summary,
    generate_project_overview,
    generate_architecture_overview,
    generate_modules_overview,
    generate_api_overview
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def serve_pipeline(repo_url: str, build_only: bool = False):
    project_id = f"serve_{uuid.uuid4().hex[:8]}"
    logger.info(f"Starting pipeline for {repo_url} (Project ID: {project_id})")

    # Step 2: Clone repository
    print(f"[STEP] Cloning repository")
    logger.info("Cloning repository...")
    cloned_path = clone_repository(repo_url, project_id)
    print(f"[INFO] Repository cloned successfully to: {cloned_path}")

    # Step 3: Scan repository
    print(f"[STEP] Scanning files")
    logger.info("Scanning for code files...")
    
    # Using the scanner which by itself filters, so we'll just count what it found
    # For advanced logging like skipped and extensions, we count them manually here
    # Since scan_repository doesn't return that granular data, we do a quick count
    all_files_count = 0
    skipped_count = 0
    extensions_found = set()
    
    base_path = Path(cloned_path)
    for root, dirs, files in os.walk(base_path):
        if ".git" in root or "node_modules" in root: continue
        for file in files:
            all_files_count += 1
            extensions_found.add(Path(file).suffix.lower())
            
    valid_files = scan_repository(cloned_path)
    skipped_count = all_files_count - len(valid_files)
    
    print(f"[INFO] Total files found: {all_files_count}")
    print(f"[INFO] Files selected for analysis: {len(valid_files)}")
    print(f"[INFO] Skipped files: {skipped_count}")
    print(f"[INFO] File extensions detected: {', '.join(extensions_found)}")
    
    if not valid_files:
        logger.warning("No valid code files found.")
        return

    # Step 4: Generate Markdown documentation
    print(f"[STEP] Generating documentation")
    logger.info("Parsing code and generating Markdown documentation...")
    docs_content = {}
    
    # Process up to 10 files for this example to keep it fast
    max_files_to_process = 10 
    for file_path in valid_files[:max_files_to_process]:
        parsed_data = parse_code_file(file_path)
        
        file_name = parsed_data.get("file", "unknown")
        classes = parsed_data.get("classes", [])
        functions = parsed_data.get("functions", [])
        
        print(f"[INFO] Analyzed: {file_name}")
        print(f"       Extracted classes: {len(classes)} ({', '.join(classes) if classes else 'None'})")
        print(f"       Extracted functions: {len(functions)} ({', '.join(functions) if functions else 'None'})")
        
        if not functions and not classes:
            # Fallback for scripts, config files, or files without standard structure
            markdown_output = generate_file_fallback(parsed_data)
        else:
            markdown_output = generate_documentation(parsed_data)
            
        docs_content[parsed_data["file"]] = markdown_output

    print(f"[INFO] Markdown files created: {len(docs_content)}")
    for md_file in docs_content.keys():
        print(f"[INFO]   -> Created docs for: {md_file}")

    if not docs_content:
        logger.warning("No generated documentation content.")
        return

    # Step 5: Organize into MkDocs structure
    print(f"[STEP] Preparing MkDocs structure")
    logger.info("Organizing MkDocs structure...")
    project_path = Path(cloned_path)
    docs_dir = project_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    modules_dir = docs_dir / "modules"
    modules_dir.mkdir(parents=True, exist_ok=True)
    
    files_dir = docs_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    dirs_to_files = {}
    modules_nav = []
    files_nav = []

    for file_name, md_content in docs_content.items():
        # Get the relative path starting inside the repo
        # Example: 'src/main.py' or 'main.py'
        rel_path = os.path.relpath(file_name, cloned_path)
        parent_dir = os.path.dirname(rel_path)
        
        # Determine logical directory bucket
        if not parent_dir or parent_dir == "." or parent_dir.startswith(".."): 
            dir_name = "root"
        else:
            dir_name = parent_dir.replace(os.path.sep, "_")
            
        if dir_name not in dirs_to_files:
            dirs_to_files[dir_name] = []
            
        safe_name = Path(file_name).with_suffix('.md').name
        dirs_to_files[dir_name].append(safe_name)
        
        # Determine if it's a module
        file_suffix = Path(file_name).suffix.lower()
        if file_suffix in ALLOWED_EXTENSIONS:
            output_path = modules_dir / safe_name
            nav_ref = f"modules/{safe_name}"
            nav_list = modules_nav
        else:
            output_path = files_dir / safe_name
            nav_ref = f"files/{safe_name}"
            nav_list = files_nav
            
        output_path.write_text(md_content, encoding="utf-8")
        nav_title = Path(file_name).stem.replace("_", " ").title()
        nav_list.append({nav_title: nav_ref})
        
    # Generate Directory Summaries
    print(f"[STEP] Generating Directory Summaries")
    for d_name, d_files in dirs_to_files.items():
        summary_md = generate_directory_summary(d_name, d_files)
        dir_summary_path = modules_dir / f"{d_name}.md"
        dir_summary_path.write_text(summary_md, encoding="utf-8")
        modules_nav.insert(0, {f"Directory: {d_name}": f"modules/{d_name}.md"})
        print(f"[INFO] Created directory summary for {d_name}")
        
    # Generate Summary / Index
    print(f"[STEP] Generating Project Overview")
    project_overview_md = generate_project_overview(
        repo_url=repo_url, 
        total_files=all_files_count, 
        detected_extensions=extensions_found, 
        directories=set(dirs_to_files.keys())
    )
    index_path = docs_dir / "index.md"
    index_path.write_text(project_overview_md, encoding="utf-8")

    def fix_mermaid_blocks(text: str) -> str:
        """Ensure every ```mermaid block is closed with a matching ```."""
        lines = text.splitlines()
        in_block = False
        result = []
        for line in lines:
            stripped = line.strip()
            if not in_block and stripped.startswith("```mermaid"):
                in_block = True
            elif in_block and stripped == "```":
                in_block = False
            result.append(line)
        if in_block:
            result.append("```")  # Close unclosed block
        return "\n".join(result)

    # 6. Generate Global Context Pages (Architecture, Modules, API)
    print(f"\n[INFO] Generating global context pages for MkDocs...")
    directories_found = set(dirs_to_files.keys())
    structure_mapping = dirs_to_files
    architecture_md = fix_mermaid_blocks(generate_architecture_overview(directories_found, structure_mapping))
    modules_md = fix_mermaid_blocks(generate_modules_overview(directories_found, structure_mapping))
    api_reference_md = generate_api_overview(len(docs_content), directories_found)
    
    # Write to files
    arc_path = docs_dir / "architecture.md"
    arc_path.write_text(architecture_md, encoding="utf-8")
    
    mod_path = docs_dir / "modules_overview.md"
    mod_path.write_text(modules_md, encoding="utf-8")
    
    api_path = docs_dir / "api_reference.md"
    api_path.write_text(api_reference_md, encoding="utf-8")
    
    print(f"[INFO] Wrote Architecture, Modules, and API Reference overviews")
    
    # 7. Generate mkdocs.yml Configuration...")
    mkdocs_file = project_path / "mkdocs.yml"
    
    nav_config = [
        {"Project Overview": "index.md"},
        {"Architecture": "architecture.md"},
        {"Modules": "modules_overview.md"},
        {"API Reference": "api_reference.md"}
    ]
    
    if modules_nav:
        nav_config.append({"Modules": modules_nav})
    
    if files_nav:
        nav_config.append({"Files": files_nav})
        
    mkdocs_config = {
        "site_name": f"Documentation - {project_path.name}",
        "theme": {
            "name": "material",
            "features": [
                "navigation.sections",
                "navigation.expand",
                "navigation.top",
                "search.highlight",
                "search.share",
                "content.code.copy",
                "toc.integrate"
            ],
            "palette": [
                {
                    "scheme": "default",
                    "toggle": {
                        "icon": "material/brightness-7",
                        "name": "Switch to dark mode"
                    }
                },
                {
                    "scheme": "slate",
                    "toggle": {
                        "icon": "material/brightness-4",
                        "name": "Switch to light mode"
                    }
                }
            ]
        },
        "plugins": [
            "search"
        ],
        "nav": nav_config
    }
    
    with open(mkdocs_file, "w", encoding="utf-8") as f:
        yaml.dump(mkdocs_config, f, sort_keys=False)
        f.write("\nmarkdown_extensions:\n  - pymdownx.superfences:\n      custom_fences:\n        - name: mermaid\n          class: mermaid\n          format: !!python/name:pymdownx.superfences.fence_code_format\n")


    print(f"[INFO] Verified docs/ directory created: {docs_dir.exists()}")
    print(f"[INFO] Verified docs/index.md created: {index_path.exists()}")
    print(f"[INFO] Verified mkdocs.yml created: {mkdocs_file.exists()}")
    print(f"[INFO] Modules generated: {len(modules_nav)}")
    print(f"[INFO] Files generated: {len(files_nav)}")

    # Step 7: Run `mkdocs build`
    print(f"[STEP] Running mkdocs build")
    logger.info("Building MkDocs static site...")
    try:
        subprocess.run(
            ["mkdocs", "build"], 
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("MkDocs build successful.")
    except subprocess.CalledProcessError as e:
        logger.error(f"MkDocs build failed: {e.stderr}")
        return
        
    # Get the site dir path
    site_dir = project_path / "site"

    if build_only:
        # API mode: return site_dir and None (no zip in serve_pipeline)
        logger.info(f"Build-only mode: returning site_dir={site_dir}")
        return str(site_dir), None

    # Step 8 & 9: Serve the documentation and print the URL
    logger.info("Serving MkDocs documentation...")
    print("\n" + "="*50)
    print("Documentation is live! View it in your browser at:")
    print("http://127.0.0.1:8000")
    print("="*50 + "\n")
    
    # Run serve 
    try:
        subprocess.run(
            ["mkdocs", "serve", "-a", "127.0.0.1:8000"], 
            cwd=project_path
        )
    except KeyboardInterrupt:
        logger.info("MkDocs server stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and serve documentation for a GitHub repository")
    parser.add_argument("repo_url", help="The GitHub repository URL to process")
    args = parser.parse_args()
    
    serve_pipeline(args.repo_url)

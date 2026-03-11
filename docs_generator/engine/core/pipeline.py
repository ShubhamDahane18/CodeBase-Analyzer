from docs_generator.engine.input_handler.validator import validate_path
from docs_generator.engine.input_handler.scanner import scan_directory
from docs_generator.parsers.file_reader import read_python_file
from docs_generator.parsers.ast_parser import parse_python_file
from docs_generator.engine.context_builder.builder import build_context
from docs_generator.engine.prompt_engine.prompt_builder import build_prompt, build_project_overview_prompt, build_architecture_prompt, build_api_reference_prompt
from docs_generator.engine.output_manager.saver import save_single_doc, save_markdown_file
from docs_generator.engine.llm_engine.gemini_client import generate_documentation
from docs_generator.engine.core.cache import CacheManager
import os
import json
import shutil
import concurrent.futures


def process_file(file: dict, cache_manager: CacheManager, force: bool = False) -> bool:
    """
    Processes a single file through the LLM pipeline.
    Returns True if successful, False if failed or skipped.
    """
    if file.get("extension") != ".py":
        return False

    file_path = file["file_path"]

    # --- Cache Check ---
    if not force and cache_manager.is_cached(file_path):
        print(f"Skipping (cached): {file['file_name']}")
        return False

    try:
        print(f"Processing started: {file['file_name']}")
        content = read_python_file(file_path)
        parsed = parse_python_file(content)

        context = build_context(file, parsed)
        prompt = build_prompt(context)
        documentation_text = generate_documentation(prompt)

        real_llm_response = {
            "file_name": file["file_name"],
            "documentation": documentation_text
        }

        # Save immediately explicitly instead of collecting in a massive array
        save_single_doc(real_llm_response)
        
        # --- Update Cache on Success ---
        cache_manager.update_cache(file_path)
        
        print(f"Processing completed: {file['file_name']}")
        return True
    except Exception as e:
        print(f"Pipeline error on {file['file_name']}: {e}")
        return False


def run_pipeline(project_path: str, max_workers: int = 4, force: bool = False):
    """
    Orchestrates the entire documentation generation workflow using streaming and concurrency.
    """
    valid_path = validate_path(project_path)
    files_to_scan = list(scan_directory(valid_path))
    cache_manager = CacheManager()

    print("Layer 1 Complete... starting concurrent stream processing")

    # Clear old master JSON before streaming new run
    os.makedirs(os.path.join("docs_generator", "output", "raw"), exist_ok=True)
    os.makedirs(os.path.join("docs_generator", "output", "modules"), exist_ok=True)
    
    master_json_path = os.path.join("docs_generator", "output", "raw", "all_documentation.json")
    
    if force:
        # Cleanup old files
        if os.path.exists(os.path.join("docs_generator", "output")):
            for item in os.listdir(os.path.join("docs_generator", "output")):
                item_path = os.path.join("docs_generator", "output", item)
                if os.path.isdir(item_path):
                    if item not in ("raw", "modules"):
                        shutil.rmtree(item_path)
                elif item.endswith(".docx") or item.endswith(".md"):
                    os.remove(item_path)
            if os.path.exists(os.path.join("docs_generator", "output", "modules")):
                shutil.rmtree(os.path.join("docs_generator", "output", "modules"))
                os.makedirs(os.path.join("docs_generator", "output", "modules"), exist_ok=True)

    if force or not os.path.exists(master_json_path):
        with open(master_json_path, "w", encoding="utf-8") as f:
            json.dump([], f)

    files_processed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, file, cache_manager, force): file for file in files_to_scan}
        
        for future in concurrent.futures.as_completed(futures):
            # Result returns True if it successfully documented a .py file
            if future.result():
                files_processed += 1

    print(f"Pipeline file processing finished! Generated/Updated docs for {files_processed} files.")

    # --- Post-Processing Project Synthesis ---
    print("Layer 2: Starting Project Synthesis...")
    try:
        with open(master_json_path, "r", encoding="utf-8") as f:
            all_docs = json.load(f)
        
        # Filter docs to only include files that are part of the current project run
        project_file_names = {f["file_name"] for f in files_to_scan}
        project_docs = [doc for doc in all_docs if doc.get("file_name") in project_file_names]
        
        if project_docs:
            print(f"Synthesizing Project Overview from {len(project_docs)} files...")
            overview_prompt = build_project_overview_prompt(project_docs)
            overview_content = generate_documentation(overview_prompt)
            save_markdown_file("project_overview.md", overview_content)

            print("Synthesizing Architecture Document...")
            arch_prompt = build_architecture_prompt(project_docs)
            arch_content = generate_documentation(arch_prompt)
            save_markdown_file("architecture.md", arch_content)

            print("Synthesizing API Reference...")
            api_prompt = build_api_reference_prompt(project_docs)
            api_content = generate_documentation(api_prompt)
            save_markdown_file("api_reference.md", api_content)

            print("Project Synthesis Complete!")
        else:
            print("No valid file documentation found to synthesize.")
    except Exception as e:
        print(f"Failed to synthesize project documents: {e}")


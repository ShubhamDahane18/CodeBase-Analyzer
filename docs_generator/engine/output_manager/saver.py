import json
import os
import re
import threading

_json_lock = threading.Lock()

def save_single_doc(doc: dict):
    """
    Saves a single document:
    1. Appends to Master JSON file (thread-safe) in the raw/ folder.
    2. Generates individual Markdown file in the modules/ folder.
    """
    os.makedirs(os.path.join("docs_generator", "output", "raw"), exist_ok=True)
    os.makedirs(os.path.join("docs_generator", "output", "modules"), exist_ok=True)
    
    master_json_path = os.path.join("docs_generator", "output", "raw", "all_documentation.json")

    # 1. Update master JSON incrementally in a thread-safe way
    with _json_lock:
        all_docs = []
        if os.path.exists(master_json_path):
            try:
                with open(master_json_path, "r", encoding="utf-8") as f:
                    all_docs = json.load(f)
            except json.JSONDecodeError:
                all_docs = []

        all_docs.append(doc)

        with open(master_json_path, "w", encoding="utf-8") as f:
            json.dump(all_docs, f, indent=4)

    # 2. Generate Markdown file
    try:
        raw_output = doc.get("documentation", "")

        if not raw_output.strip():
            print(f"No documentation content for {doc['file_name']}")
            return

        # Clean the output of weird markdown block fences if present
        cleaned_output = re.sub(r"^```markdown", "", raw_output, flags=re.IGNORECASE)
        cleaned_output = re.sub(r"```$", "", cleaned_output)
        cleaned_output = cleaned_output.strip()

        file_name = doc["file_name"].replace(".py", "")
        output_file = os.path.join("docs_generator", "output", "modules", f"{file_name}.md")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cleaned_output)

        print(f"Markdown created for {doc['file_name']}")

    except Exception as e:
        print(f"Failed to generate Markdown for {doc['file_name']}: {e}")


def save_markdown_file(filename: str, content: str):
    """
    Saves a raw string (markdown) directly to the docs_generator/output folder.
    """
    os.makedirs(os.path.join("docs_generator", "output"), exist_ok=True)
    
    # Strip json/markdown wrapper if the LLM adds it by accident
    content = re.sub(r"^```markdown", "", content, flags=re.IGNORECASE)
    content = re.sub(r"```$", "", content)
    content = content.strip()

    file_path = os.path.join("docs_generator", "output", filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Markdown created and saved: {filename}")


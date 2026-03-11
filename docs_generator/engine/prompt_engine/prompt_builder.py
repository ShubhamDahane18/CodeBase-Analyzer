def build_prompt(context: dict) -> str:
    """
    Converts context data into an LLM-ready prompt
    that forces STRICT JSON output.
    """

    file_name = context["file_name"]
    file_type = context["type"]
    data = context["summary_data"]

    if file_type == "script":
        content_block = f"""
File Name: {file_name}

Imports:
{data.get("imports")}

Source Code:
{data.get("module_source")}
"""
    else:
        content_block = f"""
File Name: {file_name}

Module Docstring:
{data.get("module_docstring")}

Imports:
{data.get("imports")}

Functions:
{data.get("functions")}

Classes:
{data.get("classes")}
"""

    prompt = f"""
You are a senior software engineer.

Generate professional developer documentation for this Python file.

Include the following sections:

1. Module Overview
2. Architecture / Workflow
3. Dependencies
4. Public API (functions/classes)
5. Function Documentation
6. Parameters
7. Return Values
8. Example Usage
9. Developer Notes

Code:
{content_block}
"""

    return prompt.strip()


def _reduce_doc_size(all_docs: list) -> list:
    """Reduces the size of the documentation block for project overview and architecture synthesis."""
    reduced_docs = []
    for doc in all_docs:
        new_doc = {"file_name": doc.get("file_name")}
        full_text = doc.get("documentation", "")
        
        # We only really need Overview, Architecture, and Dependencies for overview synthesis.
        # Cut off at "Public API" or "Function Documentation"
        cutoff = len(full_text)
        for marker in [
            "### Public API", "**Public API", "Public API (functions/classes)", 
            "### Function Documentation", "**Function Documentation",
            "### Parameters", "**Parameters"
        ]:
            idx = full_text.find(marker)
            if idx != -1 and idx < cutoff:
                cutoff = idx
                
        truncated = full_text[:cutoff].strip()
        if len(truncated) > 1500:
            truncated = truncated[:1500] + "...\n[Truncated for length]"
            
        new_doc["documentation_summary"] = truncated
        reduced_docs.append(new_doc)
    return reduced_docs

def _reduce_api_doc_size(all_docs: list) -> list:
    """Reduces the size of the documentation block specifically for API reference synthesis."""
    reduced_docs = []
    for doc in all_docs:
        new_doc = {"file_name": doc.get("file_name")}
        full_text = doc.get("documentation", "")
        
        # For API generation, we care about "Public API" and functions, but can discard developer notes
        # and example usage
        cutoff = len(full_text)
        for marker in [
            "### Example Usage", "**Example Usage", 
            "### Developer Notes", "**Developer Notes"
        ]:
            idx = full_text.find(marker)
            if idx != -1 and idx < cutoff:
                cutoff = idx
                
        truncated = full_text[:cutoff].strip()
        if len(truncated) > 3000:
            truncated = truncated[:3000] + "...\n[Truncated for length]"
            
        new_doc["api_documentation"] = truncated
        reduced_docs.append(new_doc)
    return reduced_docs


def build_project_overview_prompt(all_docs: list) -> str:
    """
    Builds a prompt to generate a high-level project overview 
    based on the documentation of all individual files.
    """
    import json
    reduced_docs = _reduce_doc_size(all_docs)
    docs_json = json.dumps(reduced_docs, indent=2)
    
    prompt = f"""
You are a Staff Software Engineer writing comprehensive documentation.

Given the following JSON array containing the individual documentation for all files in a Python project, synthesize a high-level `project_overview.md`.

Your output MUST be well-formatted Markdown and include:
1. Project Title & High Level Purpose
2. Core Features
3. Technology Stack (inferred from imports/descriptions)
4. Getting Started / Quick Start (if inferable)
5. Folder / Component Structure Summary

Do not wrap the output in any JSON formatting. Output pure Markdown.

Project File Data:
{docs_json}
"""
    return prompt.strip()


def build_architecture_prompt(all_docs: list) -> str:
    """
    Builds a prompt to generate an architectural review document.
    """
    import json
    reduced_docs = _reduce_doc_size(all_docs)
    docs_json = json.dumps(reduced_docs, indent=2)
    
    prompt = f"""
You are a Principal Software Architect.

Given the following JSON array containing the individual documentation for all files in a Python project, synthesize a detailed `architecture.md`.

Your output MUST be well-formatted Markdown and include:
1. System Architecture Overview
2. High-Level Data Flow / Pipeline
3. Core Modules and Responsibilities
4. Interactions between Major Components
5. Design Patterns Observed

Do not wrap the output in any JSON formatting. Output pure Markdown.

Project File Data:
{docs_json}
"""
    return prompt.strip()


def build_api_reference_prompt(all_docs: list) -> str:
    """
    Builds a prompt to generate a consolidated API Reference document.
    """
    import json
    reduced_docs = _reduce_api_doc_size(all_docs)
    docs_json = json.dumps(reduced_docs, indent=2)
    
    prompt = f"""
You are a Technical Writer.

Given the following JSON array containing the individual documentation for all files in a Python project, synthesize a comprehensive `api_reference.md`.

Your output MUST be well-formatted Markdown and include:
1. An introduction to the API
2. A categorized list of all significant Public classes and functions
3. Brief description of the parameters and return values (if present in the context)

Do not wrap the output in any JSON formatting. Output pure Markdown.

Project File Data:
{docs_json}
"""
    return prompt.strip()
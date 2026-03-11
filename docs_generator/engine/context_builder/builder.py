def build_context(file_metadata: dict, parsed_data: dict) -> dict:
    """
    Builds LLM-ready context from parsed AST data.
    """

    context = {
        "file_name": file_metadata["file_name"],
        "file_path": file_metadata["file_path"],
        "type": None,
        "summary_data": None
    }

    # Detect script-style
    if parsed_data.get("is_script"):
        context["type"] = "script"

        context["summary_data"] = {
            "imports": parsed_data.get("imports", []),
            "module_source": parsed_data.get("module_source")
        }

    else:
        context["type"] = "structured"

        context["summary_data"] = {
            "module_docstring": parsed_data.get("module_docstring"),
            "imports": parsed_data.get("imports", []),
            "functions": parsed_data.get("functions", []),
            "classes": parsed_data.get("classes", [])
        }

    return context

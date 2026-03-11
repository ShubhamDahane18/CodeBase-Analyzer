import ast


def parse_python_file(file_content: str) -> dict:
    """
    Parses Python file content using AST
    and extracts structured metadata.
    """

    try:
        tree = ast.parse(file_content)
    except SyntaxError as e:
     print(f"Syntax error while parsing: {e}")
     return {
        "module_docstring": None,
        "imports": [],
        "functions": [],
        "classes": [],
        "module_source": file_content,
        "is_script": True,
        "parse_error": True
     }


    parsed_data = {
        "module_docstring": ast.get_docstring(tree),
        "imports": [],
        "functions": [],
        "classes": [],
        "module_source": file_content,
        "is_script": False
    }

    for node in ast.walk(tree):

        # --- IMPORTS ---
        if isinstance(node, ast.Import):
            for alias in node.names:
                parsed_data["imports"].append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ""
            for alias in node.names:
                parsed_data["imports"].append(f"{module}.{alias.name}")

        # --- FUNCTIONS ---
        elif isinstance(node, ast.FunctionDef):
            function_data = {
                "name": node.name,
                "parameters": [arg.arg for arg in node.args.args],
                "docstring": ast.get_docstring(node),
                "line_number": node.lineno,
                "source_code": ast.unparse(node) if hasattr(ast, "unparse") else None
            }
            parsed_data["functions"].append(function_data)

        # --- CLASSES ---
        elif isinstance(node, ast.ClassDef):
            class_data = {
                "name": node.name,
                "base_classes": [
                    base.id if isinstance(base, ast.Name)
                    else ast.unparse(base)
                    for base in node.bases
                ],
                "docstring": ast.get_docstring(node),
                "methods": []
            }

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_data = {
                        "name": item.name,
                        "parameters": [arg.arg for arg in item.args.args],
                        "docstring": ast.get_docstring(item),
                        "line_number": item.lineno,
                        "source_code": ast.unparse(item) if hasattr(ast, "unparse") else None
                    }
                    class_data["methods"].append(method_data)

            parsed_data["classes"].append(class_data)

    # --- Detect script-style modules ---
    non_import_nodes = [
        node for node in tree.body
        if not isinstance(node, (ast.Import, ast.ImportFrom))
    ]

    if (
        len(parsed_data["functions"]) == 0 and
        len(parsed_data["classes"]) == 0 and
        len(non_import_nodes) > 0
    ):
        parsed_data["is_script"] = True

    return parsed_data

import ast
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_python_file(file_path: Path, content: str) -> Dict[str, Any]:
    """
    Parses a Python file using the built-in ast module.
    Extracts defined classes, functions, and structured docstrings.
    
    Args:
        file_path (Path): Path to the Python file.
        content (str): The raw text content of the Python file.
        
    Returns:
        dict: A dictionary containing the file name, classes, functions, and docstrings.
    """
    result = {
        "file": file_path.name,
        "functions": [],
        "classes": [],
        "docstrings": [],
        "excerpt": "\n".join(content.splitlines()[:50])
    }
    
    try:
        # Parse the source code into an AST tree
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        logger.warning(f"Syntax error in Python file {file_path.name}: {e}")
        # If the file has a syntax error, we can't reliably parse it via AST, 
        # so we return the empty structures.
        return result

    # Extract module-level docstring if it exists
    module_docstring = ast.get_docstring(tree)
    if module_docstring:
        result["docstrings"].append({
            "type": "module",
            "name": file_path.name,
            "docstring": module_docstring.strip()
        })

    # Walk through all nodes in the AST to find classes and functions
    for node in ast.walk(tree):
        # Handle Classes
        if isinstance(node, ast.ClassDef):
            result["classes"].append(node.name)
            
            # Extract class docstring
            class_doc = ast.get_docstring(node)
            if class_doc:
                result["docstrings"].append({
                    "type": "class",
                    "name": node.name,
                    "docstring": class_doc.strip()
                })
                
        # Handle Functions (both top-level and methods)
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            result["functions"].append(node.name)
            
            # Extract function docstring
            func_doc = ast.get_docstring(node)
            if func_doc:
                result["docstrings"].append({
                    "type": "function",
                    "name": node.name,
                    "docstring": func_doc.strip()
                })

    return result

def parse_code_file(file_path: str) -> Dict[str, Any]:
    """
    Reads a code file from disk and parses its structural information.
    Currently specifically optimized for Python using AST.
    
    Args:
        file_path (str): The absolute path to the code file.
        
    Returns:
        dict: A structured dictionary containing classes, functions, and docstrings.
    """
    path = Path(file_path)
    
    # Initialize a default response structure for unsupported/empty files
    result = {
        "file": path.name,
        "functions": [],
        "classes": [],
        "docstrings": [],
        "excerpt": ""
    }
    
    if not path.exists() or not path.is_file():
        logger.error(f"Cannot parse file. Path does not exist or is not a file: {file_path}")
        return result

    try:
        # Read the file content safely
        content = path.read_text(encoding="utf-8", errors="replace")
        
        # Grab the first 50 lines as an excerpt for fallback generation
        lines = content.splitlines()
        result["excerpt"] = "\n".join(lines[:50])
        
        if path.suffix.lower() == ".py":
            logger.debug(f"Parsing Python file: {path.name}")
            return parse_python_file(path, content)
        else:
            # For other languages (JS, TS, Java, C++), we would implement matching 
            # AST parsers or regex fallback here in the future.
            # For now, just return the base structure to keep it modular.
            logger.info(f"Parsing for {path.suffix} is not fully implemented yet. Returning base structure.")
            return result
            
    except Exception as e:
        logger.error(f"Error parsing file {file_path}: {e}")
        return result

if __name__ == "__main__":
    # Small test case
    import tempfile
    
    sample_python_code = '''
"""
This is a module level docstring.
"""

class AuthManager:
    """Manages user authentication lifecycle."""
    
    def __init__(self):
        pass

def login_user(username, password):
    """Logs the user in."""
    return True

async def logout_user(session_token):
    return False
'''

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "auth.py"
        test_file.write_text(sample_python_code)
        
        print(f"Testing Parser on {test_file.name}...\n")
        output = parse_code_file(str(test_file))
        
        import json
        print(json.dumps(output, indent=2))

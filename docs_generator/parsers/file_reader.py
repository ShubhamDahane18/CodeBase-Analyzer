from pathlib import Path


def read_python_file(file_path: str) -> str:
    """
    Reads a Python file and returns its content as string.
    Handles encoding issues safely.
    """

    try:
        path = Path(file_path)
        with path.open("r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        # Fallback encoding if UTF-8 fails
        with path.open("r", encoding="latin-1") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""
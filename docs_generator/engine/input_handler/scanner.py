import os
from pathlib import Path
from typing import Iterator


def scan_directory(path: Path) -> Iterator[dict]:
    ignore_folders = {
        ".git",
        "__pycache__",
        "venv",
        "node_modules",
        "dist",
        "build"
    }

    allowed_extensions = {".py"}

    for root, dirs, files in os.walk(path):
        # Prevent traversing into ignored directories
        ignored = set(d for d in dirs if d in ignore_folders)
        for d in ignored:
            dirs.remove(d)

        for file in files:
            file_path = Path(root) / file

            if file_path.suffix in allowed_extensions or file.lower() == "readme.md":
                yield {
                    "file_path": str(file_path.resolve()),
                    "file_name": file_path.name,
                    "extension": file_path.suffix
                }

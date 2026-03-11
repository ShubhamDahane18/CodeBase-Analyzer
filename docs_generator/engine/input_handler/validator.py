from pathlib import Path
import sys


def validate_path(project_path: str) -> Path:
    path = Path(project_path)

    if not path.exists():
        print(f"Error: Path does not exist. (Tried to resolve: {path.resolve()})")
        sys.exit(1)

    if not path.is_dir():
        print(f"Error: Provided path is not a directory. (Tried to resolve: {path.resolve()})")
        sys.exit(1)

    if not any(path.iterdir()):
        print(f"Error: Directory is empty. (Tried to resolve: {path.resolve()})")
        sys.exit(1)

    return path

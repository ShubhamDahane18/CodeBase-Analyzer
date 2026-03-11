import sys
import os
import argparse

# Ensure the root project directory is in PYTHONPATH so absolute imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from docs_generator.engine.core.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="AI Documentation Generator")
    parser.add_argument("project_path", help="Path to the Python project directory")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force regeneration of all documentation (bypasses file hashing cache)"
    )
    
    args = parser.parse_args()

    try:
        run_pipeline(args.project_path, force=args.force)
    except Exception as e:
        print(f"Pipeline execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
import hashlib
import json
import os
import threading

class CacheManager:
    def __init__(self, cache_file: str = ".doc_cache.json"):
        self.cache_file = cache_file
        self.lock = threading.Lock()
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_cache(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=4)

    def compute_hash(self, file_path: str) -> str:
        """Computes the SHA-256 hash of a file's contents."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks for memory efficiency on large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except FileNotFoundError:
            return ""

    def is_cached(self, file_path: str) -> bool:
        """Returns True if the file hash matches the cached hash."""
        current_hash = self.compute_hash(file_path)
        with self.lock:
            cached_hash = self.cache.get(file_path)
            return current_hash != "" and current_hash == cached_hash

    def update_cache(self, file_path: str):
        """Updates the cache with the file's current hash."""
        current_hash = self.compute_hash(file_path)
        if current_hash:
            with self.lock:
                self.cache[file_path] = current_hash
                self._save_cache()

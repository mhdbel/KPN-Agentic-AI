import json
import os
from typing import Dict, Any

class PersistenceManager:
    def __init__(self, storage_dir: str = "sessions"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_file_path(self, thread_id: str) -> str:
        return os.path.join(self.storage_dir, f"{thread_id}.json")

    def save_state(self, thread_id: str, state: Dict[str, Any]) -> None:
        file_path = self._get_file_path(thread_id)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def load_state(self, thread_id: str) -> Dict[str, Any]:
        file_path = self._get_file_path(thread_id)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def clear_state(self, thread_id: str) -> None:
        file_path = self._get_file_path(thread_id)
        if os.path.exists(file_path):
            os.remove(file_path)

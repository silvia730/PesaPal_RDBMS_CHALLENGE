
import json
import os
import shutil
from typing import Dict, Any, List, Optional
import threading

class StorageManager:
    """
    Handles file I/O and table-level locking.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        # Simple in-memory locks for threadsafety (and rudimentary transaction simulation)
        self.locks: Dict[str, threading.Lock] = {} 

    def _get_lock(self, table_name: str):
        if table_name not in self.locks:
            self.locks[table_name] = threading.Lock()
        return self.locks[table_name]

    def load_table(self, table_name: str) -> Dict[str, Any]:
        """Loads table data (schema + rows) from disk."""
        filepath = os.path.join(self.data_dir, f"{table_name}.json")
        if not os.path.exists(filepath):
            raise ValueError(f"Table {table_name} does not exist.")
        
        with self._get_lock(table_name):
            with open(filepath, 'r') as f:
                return json.load(f)

    def save_table(self, table_name: str, data: Dict[str, Any]):
        """Saves table data to disk."""
        filepath = os.path.join(self.data_dir, f"{table_name}.json")
        with self._get_lock(table_name):
            # Atomic write (write to temp then rename) to prevent corruption
            tmp_path = filepath + ".tmp"
            with open(tmp_path, 'w') as f:
                json.dump(data, f, indent=2)
            shutil.move(tmp_path, filepath)

    def create_table(self, table_name: str, schema: Dict[str, str]):
        filepath = os.path.join(self.data_dir, f"{table_name}.json")
        if os.path.exists(filepath):
            raise ValueError(f"Table {table_name} already exists.")
        
        data = {"schema": schema, "rows": [], "indexes": {}}
        # No lock needed for creation as file doesn't exist yet
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def drop_table(self, table_name: str):
        filepath = os.path.join(self.data_dir, f"{table_name}.json")
        with self._get_lock(table_name):
            if os.path.exists(filepath):
                os.remove(filepath)
            else:
                raise ValueError(f"Table {table_name} does not exist.")
    
    def list_tables(self) -> List[str]:
        return [f[:-5] for f in os.listdir(self.data_dir) if f.endswith(".json")]

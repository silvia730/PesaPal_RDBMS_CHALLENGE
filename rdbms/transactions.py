
from typing import Dict, Any, List
import copy

class TransactionManager:
    """
    Manages transaction state (BEGIN, COMMIT, ROLLBACK).
    Uses a log/journal approach in memory for uncommitted changes.
    """
    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.active_transaction = False
        self.transaction_diffs: Dict[str, Dict[str, Any]] = {} 
        # structure: {table_name: {rows: [new_rows], deleted_ids: []}}?
        # Simpler approach: Load Modified Tables into Memory fully during transaction.
        # On Commit: Save Memory tables to Disk.
        # On Rollback: Discard Memory tables.
        
        self.temp_tables: Dict[str, Dict[str, Any]] = {} 

    def begin(self):
        if self.active_transaction:
            raise ValueError("Transaction already in progress")
        self.active_transaction = True
        self.temp_tables = {} # Cache for modified tables

    def commit(self):
        if not self.active_transaction:
            raise ValueError("No active transaction")
        
        # Persist all temp_tables
        for table_name, data in self.temp_tables.items():
            self.storage.save_table(table_name, data)
        
        self.active_transaction = False
        self.temp_tables = {}

    def rollback(self):
        if not self.active_transaction:
            raise ValueError("No active transaction")
        self.active_transaction = False
        self.temp_tables = {}

    def get_table_data(self, table_name: str) -> Dict[str, Any]:
        """
        Returns table data. If in transaction and modified, returns temp version.
        Else loads from storage.
        """
        if self.active_transaction and table_name in self.temp_tables:
            return self.temp_tables[table_name]
        
        # Load from storage
        data = self.storage.load_table(table_name)
        
        # If in transaction but not yet modified, add to temp_tables to provide isolation (Snapshot)
        if self.active_transaction:
            self.temp_tables[table_name] = copy.deepcopy(data)
            return self.temp_tables[table_name]
            
        return data

    def mark_modified(self, table_name: str, data: Dict[str, Any]):
        """
        Updates the table data in the current context.
        """
        if self.active_transaction:
            self.temp_tables[table_name] = data
        else:
            # Auto-commit mode
            self.storage.save_table(table_name, data)

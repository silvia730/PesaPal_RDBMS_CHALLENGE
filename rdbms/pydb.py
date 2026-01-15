
from rdbms.storage import StorageManager
from rdbms.parser import SQLParser
from rdbms.transactions import TransactionManager
from rdbms.executor import Executor
from rdbms.typesystem import TypeSystem
from typing import Any, List, Dict
import datetime

class DatabaseResult:
    def __init__(self, data):
        self.data = data
    def fetchall(self):
        return self.data

class Database:
    def __init__(self, data_dir="data"):
        self.storage = StorageManager(data_dir)
        self.tm = TransactionManager(self.storage)
        self.parser = SQLParser()
        self.executor = Executor(self.tm)

    def execute(self, sql: str) -> Any:
        try:
            ast = self.parser.parse(sql)
            result = self.executor.execute(ast)
            return result
        except Exception as e:
            print(f"Execution Error: {e}")
            raise e
    
    def query(self, sql: str) -> List[Any]:
        # Helper for select specifically?
        # execute returns list for select, str for others
        return self.execute(sql)


from typing import Dict, Any, List

class IndexManager:
    """
    Manages Hash Indexes for tables.
    """
    # In-memory Structure: indexes[table][column] = {value: [row_indices]}
    
    @staticmethod
    def build_index(rows: List[Dict[str, Any]], column: str) -> Dict[Any, List[int]]:
        """
        Builds a hash index for a specific column.
        Returns Dict: value -> list of row indices in the 'rows' list.
        """
        index = {}
        for i, row in enumerate(rows):
            val = row.get(column)
            if val not in index:
                index[val] = []
            index[val].append(i)
        return index

    @staticmethod
    def search(index: Dict[Any, List[int]], value: Any) -> List[int]:
        return index.get(value, [])

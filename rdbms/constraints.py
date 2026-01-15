
from typing import Dict, Any, List, Optional

class ConstraintManager:
    """
    Manages and validates table constraints (PRIMARY KEY, UNIQUE, NOT NULL).
    """
    
    @staticmethod
    def parse_constraints(column_def: str) -> Dict[str, bool]:
        """
        Parses a column definition string to extract constraints.
        Example: "INTEGER PRIMARY KEY" -> {'primary_key': True, 'type': 'INTEGER'}
        """
        constraints = {
            'primary_key': False,
            'unique': False,
            'not_null': False,
            'type': ''
        }
        
        # Normalize
        parts = column_def.upper().split()
        
        # Type is usually the first part
        constraints['type'] = parts[0]
        
        # Check tokens
        if 'PRIMARY' in parts and 'KEY' in parts:
            constraints['primary_key'] = True
            constraints['unique'] = True # PK implies Unique
            constraints['not_null'] = True # PK implies Not Null
            
        if 'UNIQUE' in parts:
            constraints['unique'] = True
            
        if 'NOT' in parts and 'NULL' in parts:
            constraints['not_null'] = True
            
        return constraints

    def validate_insert(self, table_name: str, row: Dict[str, Any], table_data: Dict[str, Any]):
        """
        Validates a row against the table's schema constraints before insertion.
        """
        schema = table_data.get('schema', {})
        existing_rows = table_data.get('rows', [])
        
        # We need extended schema info. 
        # Since currently schema is just {col: type_str}, we have to re-parse the type_str 
        # to check constraints on every insert? 
        # Optimization: Ideally schema should store parsed constraints. 
        # For this implementation, we will parse on the fly or rely on updated storage structure.
        # Let's assume we proceed with on-the-fly parsing of the stored schema string for simplicity 
        # strictly avoiding massive refactor of storage format if possible.
        
        for col, type_def in schema.items():
            constraints = self.parse_constraints(type_def)
            val = row.get(col)
            
            # 1. NOT NULL Check
            if constraints['not_null'] and val is None:
                 raise ValueError(f"Constraint Violation: Column '{col}' cannot be NULL.")
            
            # 2. UNIQUE / PRIMARY KEY Check
            if (constraints['unique'] or constraints['primary_key']) and val is not None:
                # Scan existing rows (O(N) - slow but functional for this challenge)
                # In real DB, would use Index.
                for r in existing_rows:
                    if r.get(col) == val:
                        raise ValueError(f"Constraint Violation: Duplicate value '{val}' for unique column '{col}'.")

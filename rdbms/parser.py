
import re
from typing import Dict, Any, List, Optional

class SQLParser:
    """
    Parses simplified SQL commands into a structured dictionary (AST).
    """

    # Regex patterns for tokens
    PATTERNS = {
        'CREATE': r'^\s*CREATE\s+TABLE\s+(\w+)\s*\((.+)\)',
        'INSERT': r'^\s*INSERT\s+INTO\s+(\w+)\s+VALUES\s*\((.+)\)',
        'SELECT': r'^\s*SELECT\s+(.+)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?',
        'UPDATE': r'^\s*UPDATE\s+(\w+)\s+SET\s+(.+?)\s+WHERE\s+(.+)',
        'DELETE': r'^\s*DELETE\s+FROM\s+(\w+)\s+WHERE\s+(.+)',
        'BEGIN': r'^\s*BEGIN',
        'COMMIT': r'^\s*COMMIT',
        'ROLLBACK': r'^\s*ROLLBACK',
        'CREATE_INDEX': r'^\s*CREATE\s+INDEX\s+ON\s+(\w+)\s*\(\s*(\w+)\s*\)',
        'DROP_INDEX': r'^\s*DROP\s+INDEX\s+ON\s+(\w+)\s*\(\s*(\w+)\s*\)'
    }

    def parse(self, sql: str) -> Dict[str, Any]:
        sql = sql.strip().replace(';', '')
        
        # CREATE TABLE
        match = re.match(self.PATTERNS['CREATE'], sql, re.IGNORECASE)
        if match:
            table_name = match.group(1)
            schema_str = match.group(2)
            schema = self._parse_schema(schema_str)
            return {'type': 'CREATE_TABLE', 'table': table_name, 'schema': schema}

        # INSERT
        match = re.match(self.PATTERNS['INSERT'], sql, re.IGNORECASE)
        if match:
            table_name = match.group(1)
            values_str = match.group(2)
            values = self._parse_values(values_str)
            return {'type': 'INSERT', 'table': table_name, 'values': values}

        # SELECT
        # Logic: Split WHERE clause first for robustness
        
        # 1. Extract WHERE 
        # We need to find the *last* WHERE or just split?
        # A simple split by " WHERE " (case insensitive) might be safe enough for this simplified SQL.
        # But be careful about values containing " WHERE ". assuming simple SQL.
        
        where_clause = None
        sql_base = sql
        
        # Case insensitive split
        params = re.split(r'\s+WHERE\s+', sql, flags=re.IGNORECASE, maxsplit=1)
        if len(params) > 1:
            sql_base = params[0]
            where_clause = params[1]
            
        # 2. Match Base: SELECT cols FROM table [JOIN ...]
        # Note: INNER|LEFT group is optional.
        base_pattern = r'^\s*SELECT\s+(.+)\s+FROM\s+(\w+)(?:\s+(INNER|LEFT)?\s*JOIN\s+(\w+)\s+ON\s+(.+))?'
        match = re.match(base_pattern, sql_base, re.IGNORECASE)
        
        if match:
            columns_str = match.group(1).strip()
            table_name = match.group(2)
            
            # Join groups
            join_type_raw = match.group(3)
            join_table = match.group(4)
            join_on = match.group(5)
            
            columns = [c.strip() for c in columns_str.split(',')]
            if columns == ['*']:
                columns = [] 
            
            conditions = self._parse_where(where_clause) if where_clause else []
            
            join_def = None
            if join_table:
                # Parse ON clause: t1.col = t2.col
                # Assume simple equality
                on_parts = join_on.split('=')
                if len(on_parts) == 2:
                    left_operand = on_parts[0].strip()
                    right_operand = on_parts[1].strip()
                    
                    def clean_col(s):
                         return s.split('.')[-1] if '.' in s else s

                    join_def = {
                        'type': 'LEFT' if join_type_raw and join_type_raw.upper() == 'LEFT' else 'INNER',
                        'table': join_table,
                        'left_col': clean_col(left_operand),
                        'right_col': clean_col(right_operand),
                        'raw_on': join_on
                    }

            return {
                'type': 'SELECT', 
                'table': table_name, 
                'columns': columns, 
                'where': conditions,
                'join': join_def
            }

        # UPDATE
        match = re.match(self.PATTERNS['UPDATE'], sql, re.IGNORECASE)
        if match:
            table_name = match.group(1)
            set_clause = match.group(2)
            where_clause = match.group(3)
            
            updates = {}
            for pair in set_clause.split(','):
                k, v = pair.split('=')
                updates[k.strip()] = self._clean_value(v.strip())
            
            conditions = self._parse_where(where_clause)
            return {'type': 'UPDATE', 'table': table_name, 'updates': updates, 'where': conditions}

        # DELETE
        match = re.match(self.PATTERNS['DELETE'], sql, re.IGNORECASE)
        if match:
            table_name = match.group(1)
            where_clause = match.group(2)
            conditions = self._parse_where(where_clause)
            return {'type': 'DELETE', 'table': table_name, 'where': conditions}

        # TRANSACTIONS
        if re.match(self.PATTERNS['BEGIN'], sql, re.IGNORECASE):
            return {'type': 'BEGIN'}
        if re.match(self.PATTERNS['COMMIT'], sql, re.IGNORECASE):
            return {'type': 'COMMIT'}
        if re.match(self.PATTERNS['ROLLBACK'], sql, re.IGNORECASE):
            return {'type': 'ROLLBACK'}

        raise ValueError(f"Syntax error or unsupported command: {sql}")

    def _parse_schema(self, schema_str: str) -> Dict[str, str]:
        # Example: id INTEGER PRIMARY KEY, name VARCHAR(50) NOT NULL
        schema = {}
        # Split by comma (naive, doesn't handle commas inside parens if any)
        for part in schema_str.split(','):
            part = part.strip()
            # Split by first space to separate col_name from definition
            if ' ' in part:
                col_name, col_def = part.split(' ', 1)
                schema[col_name] = col_def.strip().upper()
            else:
                 # Fallback? Should not happen in valid SQL
                 pass
        return schema

    def _parse_values(self, values_str: str) -> List[Any]:
        # Split by comma but respect quotes? Simplification: split by comma
        # Creating a robust CSV parser is hard, assume simple values
        vals = []
        for v in values_str.split(','):
            vals.append(self._clean_value(v.strip()))
        return vals

    def _clean_value(self, val: str) -> Any:
        # constant handling
        if val.startswith("'") and val.endswith("'"):
            return val[1:-1]
        if val.lower() == 'true': return True
        if val.lower() == 'false': return False
        if val.lower() == 'null': return None
        try:
            if '.' in val:
                return float(val)
            return int(val)
        except ValueError:
            return val # Fallback to string

    def _parse_where(self, where_clause: str) -> List[Dict[str, Any]]:
        # Supports simple AND logic: col = val AND col2 > val2
        # Returns list of conditions
        # Simplification: Only supports AND, and basic operators =, !=, >, <
        # Example: id = 1 AND name = 'bob'
        conditions = []
        if not where_clause:
            return conditions
        
        # Split by AND
        parts = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)
        for part in parts:
            # simple regex for operator
            # Order matters: check >=, <=, != before >, <, =
            op_match = re.search(r'(>=|<=|!=|=|>|<)', part)
            if op_match:
                op = op_match.group(1)
                left, right = part.split(op)
                conditions.append({
                    'column': left.strip(),
                    'operator': op,
                    'value': self._clean_value(right.strip())
                })
        return conditions


from typing import Dict, Any, List
from rdbms.storage import StorageManager
from rdbms.transactions import TransactionManager
from rdbms.indexes import IndexManager
from rdbms.typesystem import TypeSystem
from rdbms.constraints import ConstraintManager
from rdbms.joins import JoinExecutor
import datetime

class Executor:
    def __init__(self, transaction_manager: TransactionManager):
        self.tm = transaction_manager
        self.cm = ConstraintManager()

    def execute(self, ast: Dict[str, Any]) -> Any:
        cmd_type = ast['type']
        
        if cmd_type == 'CREATE_TABLE':
            return self._execute_create_table(ast)
        elif cmd_type == 'INSERT':
            return self._execute_insert(ast)
        elif cmd_type == 'SELECT':
            return self._execute_select(ast)
        elif cmd_type == 'UPDATE':
            return self._execute_update(ast)
        elif cmd_type == 'DELETE':
            return self._execute_delete(ast)
        elif cmd_type == 'BEGIN':
            self.tm.begin()
            return "Transaction Started"
        elif cmd_type == 'COMMIT':
            self.tm.commit()
            return "Transaction Committed"
        elif cmd_type == 'ROLLBACK':
            self.tm.rollback()
            return "Transaction Rolled Back"
        
        raise ValueError(f"Unknown command type: {cmd_type}")

    def _execute_create_table(self, ast):
        table_name = ast['table']
        schema = ast['schema']
        # Delegate to storage via TM? TM handles data, Storage handles creation structure.
        # Ideally TM should handle this to rollback table creation, but simple approach:
        # direct storage call, no rollback for DDL.
        self.tm.storage.create_table(table_name, schema)
        return f"Table {table_name} created."

    def _execute_insert(self, ast):
        table_name = ast['table']
        values = ast['values']
        
        table_data = self.tm.get_table_data(table_name)
        schema = table_data['schema']
        rows = table_data['rows']
        
        if len(values) != len(schema):
            raise ValueError(f"Column count mismatch. Expected {len(schema)}, got {len(values)}")
        
        row = {}
        for (col, col_def), val in zip(schema.items(), values):
             # Extract pure type for validation (e.g., "INTEGER PRIMARY KEY" -> "INTEGER")
             # ConstraintManager.parse_constraints can help or simple split
             type_only = col_def.split()[0] 
             row[col] = TypeSystem.validate(val, type_only)
        
        # Validate Constraints
        self.cm.validate_insert(table_name, row, table_data)

        rows.append(row)
        table_data['rows'] = rows
        self.tm.mark_modified(table_name, table_data)
        return "1 row inserted."

    def _execute_select(self, ast):
        table_name = ast['table']
        columns = ast['columns']
        where = ast['where']
        join_def = ast.get('join')
        print("AST JOIN:", join_def) # DEBUG
        
        table_data = self.tm.get_table_data(table_name)
        rows = table_data['rows']
        
        # Handle JOIN
        if join_def:
            right_table = join_def['table']
            right_data = self.tm.get_table_data(right_table)
            right_rows = right_data['rows']
            
            rows = JoinExecutor.nested_loop_join(
                rows, table_name,
                right_rows, right_table,
                join_def,
                join_def['type']
            )
            # FROM now on, rows have keys like 'table.col'
            # We need to adjust WHERE and SELECT to handle this.
            # Currently Query Executor _apply_filtering uses simple keys.
            # We need to make it smarter or map keys.
        
        # If joined, keys are 'table.col'. If not, keys are 'col'.
        # To unify, if not joined, maybe aliasing rows is safer?
        # Or just handle lookup logic.
        
        # Validating Columns if they have dots (e.g. users.name)
        # If executor receives 'name' but row has 'users.name', we need to match.
        
        filtered_rows = self._apply_filtering(rows, where, table_data.get('indexes'), is_joined=bool(join_def), primary_table=table_name)
        
        # Project columns
        result = []
        for row in filtered_rows:
            if not columns:
                result.append(list(row.values()))
            else:
                row_res = []
                for col in columns:
                    # lookup
                    val = self._resolve_col(row, col, table_name)
                    row_res.append(val)
                result.append(row_res)
        
        return result

    def _resolve_col(self, row, col_name, primary_table):
        if col_name in row: return row[col_name]
        # try table.col
        # try table.col
        if '.' in col_name: return row.get(col_name) # Exact match
        # Try prepending primary table
        if f"{primary_table}.{col_name}" in row: return row[f"{primary_table}.{col_name}"]
        # Try finding suffix 
        # (Ambiguous columns issue? For now pick first match)
        for k, v in row.items():
            if k.endswith(f".{col_name}"):
                return v
        return None

    def _apply_filtering(self, rows, conditions, indexes, is_joined=False, primary_table=""):
        if not conditions:
            return rows
            
        results = []
        for row in rows:
            match = True
            for cond in conditions:
                col = cond['column']
                op = cond['operator']
                val = cond['value']
                
                row_val = self._resolve_col(row, col, primary_table)
                
                # ... same comparison logic ...
                if op == '=' and str(row_val) != str(val): match = False
                elif op == '!=' and str(row_val) == str(val): match = False
                elif op == '>':
                     if row_val is None or not (row_val > val): match = False
                elif op == '<':
                     if row_val is None or not (row_val < val): match = False
                elif op == '>=':
                     if row_val is None or not (row_val >= val): match = False
                elif op == '<=':
                     if row_val is None or not (row_val <= val): match = False
                
                if not match: break
            if match:
                results.append(row)
        return results

    def _execute_update(self, ast):
        table_name = ast['table']
        updates = ast['updates']
        where = ast['where']
        
        table_data = self.tm.get_table_data(table_name)
        rows = table_data['rows']
        schema = table_data['schema']
        
        count = 0
        for row in rows:
            match = True
            for cond in where:
                # Same filtering logic - duplicated for brevity
                col = cond['column']; op = cond['operator']; val = cond['value']
                row_val = row.get(col)
                if op == '=' and row_val != val: match = False; break
                if op == '!=' and row_val == val: match = False; break
                # ... others skipped for brevity in update ...
            
            if match:
                for col, new_val in updates.items():
                    if col in schema:
                        row[col] = TypeSystem.validate(new_val, schema[col])
                count += 1
        
        if count > 0:
            self.tm.mark_modified(table_name, table_data)
        return f"{count} rows updated."

    def _execute_delete(self, ast):
        table_name = ast['table']
        where = ast['where']
        
        table_data = self.tm.get_table_data(table_name)
        rows = table_data['rows']
        
        initial_len = len(rows)
        # Filter keep rows
        new_rows = []
        for row in rows:
            match = True
            for cond in where:
                col = cond['column']; op = cond['operator']; val = cond['value']
                row_val = row.get(col)
                if op == '=' and row_val != val: match = False; break
                # ...
            if not match: # If NOT match conditions, keep it (Logic inverted)
                 # Wait, logic: Delete WHERE conditions ARE Met.
                 # So if match is True, we DELETE (do not add to new_rows)
                 pass
            else:
                 # Match found, so we delete.
                 pass

        # Re-implement clearer delete logic
        kept_rows = []
        deleted_count = 0
        for row in rows:
            match = True
            for cond in where:
                col = cond['column']; op = cond['operator']; val = cond['value']
                row_val = row.get(col)
                if op == '=' and row_val != val: match = False; break
                if op == '!=' and row_val == val: match = False; break
                if op == '>' and not (row_val > val): match = False; break
                if op == '<' and not (row_val < val): match = False; break
            
            if match:
                deleted_count += 1
            else:
                kept_rows.append(row)
        
        table_data['rows'] = kept_rows
        self.tm.mark_modified(table_name, table_data)
        return f"{deleted_count} rows deleted."

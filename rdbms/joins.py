
from typing import List, Dict, Any, Tuple
from typing import List, Dict, Any, Tuple
# from rdbms.executor import Executor -- circular import avoided

class JoinExecutor:
    """
    Executes JOIN operations (Nested Loop Join).
    """
    
    @staticmethod
    def nested_loop_join(
            left_rows: List[Dict[str, Any]], 
            left_table_name: str,
            right_rows: List[Dict[str, Any]], 
            right_table_name: str,
            join_condition: Dict[str, Any],
            join_type: str = 'INNER'
    ) -> List[Dict[str, Any]]:
        """
        Performs a Nested Loop Join.
        Returns a list of flattened rows with keys 'tablename.colname'.
        """
        results = []
        
        # Parse condition: table1.col = table2.col
        # condition dict: {'left_col': ..., 'right_col': ...} derived from parser?
        # Or Just pass the raw condition and evaluate it?
        # Let's assume parser gives us: left_col, right_col (simple equality join for now)
        
        left_key = join_condition['left_col']
        right_key = join_condition['right_col'] 
        
        # Pre-process rows to have "table.col" keys to avoid collisions
        # This is expensive but necessary for result set
        processed_left = []
        for r in left_rows:
            new_r = {f"{left_table_name}.{k}": v for k, v in r.items()}
            processed_left.append(new_r)
            
        processed_right = []
        for r in right_rows:
            new_r = {f"{right_table_name}.{k}": v for k, v in r.items()}
            processed_right.append(new_r)
            
        for l_row in processed_left:
            matched = False
            l_val = l_row.get(f"{left_table_name}.{left_key}")
            
            for r_row in processed_right:
                r_val = r_row.get(f"{right_table_name}.{right_key}")
                
                # Check match
                if str(l_val) == str(r_val):
                    # Merge
                    merged = {**l_row, **r_row}
                    results.append(merged)
                    matched = True
            
            if join_type == 'LEFT' and not matched:
                # Add left row with NULLs for right cols
                # Need to know right schema or just fill what we can?
                # Just adding l_row is fine if we handle missing keys as None later, 
                # but better to explicitly add None for right keys if we knew schema.
                # For dynamic dicts, just adding l_row is enough, keys from right won't exist.
                results.append(l_row)
                
        return results

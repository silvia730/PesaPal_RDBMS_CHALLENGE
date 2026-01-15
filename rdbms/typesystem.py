
import datetime
from typing import Any

class TypeSystem:
    @staticmethod
    def validate(value: Any, expected_type: str) -> Any:
        if value is None:
            return None
        try:
            expected_type = expected_type.upper()
            if expected_type.startswith("VARCHAR"):
                max_len = int(expected_type.split("(")[1].split(")")[0])
                val_str = str(value)
                if len(val_str) > max_len:
                    raise ValueError(f"Value '{val_str}' exceeds max length {max_len}")
                return val_str
            
            elif expected_type == "INTEGER":
                return int(value)
            
            elif expected_type == "BOOLEAN":
                if isinstance(value, bool):
                     return value
                if str(value).lower() in ('true', '1', 'yes'):
                    return True
                if str(value).lower() in ('false', '0', 'no'):
                    return False
                raise ValueError(f"Invalid boolean value: {value}")
                
            elif expected_type == "DATE":
                # Expects 'YYYY-MM-DD'
                if isinstance(value, datetime.date):
                    return value.isoformat()
                try:
                    datetime.datetime.strptime(str(value), "%Y-%m-%d")
                    return str(value)
                except ValueError:
                     raise ValueError(f"Invalid date format (expected YYYY-MM-DD): {value}")
            else:
                 # Fallback
                 return value
                
        except (ValueError, TypeError) as e:
            raise ValueError(f"Type validation failed for type {expected_type}: {str(e)}")

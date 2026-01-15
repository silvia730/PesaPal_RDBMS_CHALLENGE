
import re

sql = "SELECT users.name, posts.title FROM users INNER JOIN posts ON users.id = posts.user_id"


print(f"Testing SQL: '{sql}'")

# Split WHERE
where_clause = None
if ' WHERE ' in sql.upper():
    parts = re.split(r'\s+WHERE\s+', sql, flags=re.IGNORECASE, maxsplit=1)
    sql_base = parts[0]
    where_clause = parts[1]
else:
    sql_base = sql

print(f"Base: '{sql_base}', WHERE: '{where_clause}'")

# Parse Base: SELECT ... FROM ... [JOIN ...]
base_pattern = r'^\s*SELECT\s+(.+)\s+FROM\s+(\w+)(?:\s+(INNER|LEFT)?\s*JOIN\s+(\w+)\s+ON\s+(.+))?'
match = re.match(base_pattern, sql_base, re.IGNORECASE)

if match:
    print("Match Groups:", match.groups())
else:
    print("No Match")

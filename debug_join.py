
import os
import shutil
from rdbms.pydb import Database

if os.path.exists("debug_data"):
    shutil.rmtree("debug_data")

db = Database(data_dir="debug_data")
db.execute("CREATE TABLE users (id INTEGER, name VARCHAR(50))")
db.execute("CREATE TABLE posts (id INTEGER, user_id INTEGER, title VARCHAR(50))")

db.execute("INSERT INTO users VALUES (1, 'Alice')")
db.execute("INSERT INTO posts VALUES (10, 1, 'Post 1')")

print("--- Running Query ---")
results = db.query("SELECT users.name, posts.title FROM users INNER JOIN posts ON users.id = posts.user_id")
print("Results:", results)

# Inspect internal row structure by hacking executor if needed, 
# but simply seeing empty list or None values helps.

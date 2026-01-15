
import pytest
import shutil
import os
from rdbms.pydb import Database

TEST_DB_DIR = "test_data_joins"

@pytest.fixture
def db():
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)
    db = Database(data_dir=TEST_DB_DIR)
    yield db
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)

def test_inner_join(db):
    db.execute("CREATE TABLE users (id INTEGER, name VARCHAR(50))")
    db.execute("CREATE TABLE posts (id INTEGER, user_id INTEGER, title VARCHAR(50))")
    
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    db.execute("INSERT INTO users VALUES (2, 'Bob')")
    
    db.execute("INSERT INTO posts VALUES (10, 1, 'Post 1')")
    db.execute("INSERT INTO posts VALUES (11, 1, 'Post 2')")
    db.execute("INSERT INTO posts VALUES (12, 3, 'Post 3')") # Orphan post
    
    # Inner Join
    results = db.query("SELECT users.name, posts.title FROM users INNER JOIN posts ON users.id = posts.user_id")
    # Expect 2 rows: (Alice, Post 1), (Alice, Post 2)
    assert len(results) == 2
    names = sorted([r[0] for r in results])
    assert names == ['Alice', 'Alice']

def test_left_join(db):
    db.execute("CREATE TABLE users (id INTEGER, name VARCHAR(50))")
    db.execute("CREATE TABLE posts (id INTEGER, user_id INTEGER, title VARCHAR(50))")
    
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    db.execute("INSERT INTO users VALUES (2, 'Bob')") # Bob has no posts
    
    db.execute("INSERT INTO posts VALUES (10, 1, 'Post 1')")
    
    # Left Join
    results = db.query("SELECT users.name, posts.title FROM users LEFT JOIN posts ON users.id = posts.user_id")
    # Expect: (Alice, Post 1), (Bob, None)
    
    # Find Bob
    bob_found = False
    for r in results:
        if r[0] == 'Bob':
            bob_found = True
            assert r[1] is None # Left join should put None
    assert bob_found
    assert len(results) == 2

def test_join_with_where(db):
    db.execute("CREATE TABLE users (id INTEGER, name VARCHAR(50))")
    db.execute("CREATE TABLE posts (id INTEGER, user_id INTEGER, title VARCHAR(50))")
    
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    db.execute("INSERT INTO posts VALUES (10, 1, 'Alice Post')")
    db.execute("INSERT INTO posts VALUES (11, 1, 'Ignored Post')")
    
    # Filter on Joined Table
    results = db.query("SELECT users.name, posts.title FROM users JOIN posts ON users.id = posts.user_id WHERE posts.title = 'Alice Post'")
    
    assert len(results) == 1
    assert results[0][1] == 'Alice Post'

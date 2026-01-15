
import pytest
import shutil
import os
from rdbms.pydb import Database

TEST_DB_DIR = "test_data_constraints"

@pytest.fixture
def db():
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)
    db = Database(data_dir=TEST_DB_DIR)
    yield db
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)

def test_primary_key_constraint(db):
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(50))")
    
    # First insert OK
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    
    # Duplicate ID -> Fail
    with pytest.raises(Exception) as exc:
        db.execute("INSERT INTO users VALUES (1, 'Bob')")
    assert "Duplicate value '1'" in str(exc.value)

def test_unique_constraint(db):
    db.execute("CREATE TABLE users (id INTEGER, email VARCHAR(50) UNIQUE)")
    
    db.execute("INSERT INTO users VALUES (1, 'alice@test.com')")
    
    # Duplicate Email -> Fail
    with pytest.raises(Exception) as exc:
        db.execute("INSERT INTO users VALUES (2, 'alice@test.com')")
    assert "Duplicate value 'alice@test.com'" in str(exc.value)

def test_not_null_constraint(db):
    db.execute("CREATE TABLE users (id INTEGER, name VARCHAR(50) NOT NULL)")
    
    # Normal insert OK
    db.execute("INSERT INTO users VALUES (1, 'Alice')")
    
    # Insert NULL -> Fail (Input 'NULL' string which basic parser might treat as string "NULL" or None if cleaned?
    # RDBMS parser _clean_value handles 'null' -> None.
    with pytest.raises(Exception) as exc:
        db.execute("INSERT INTO users VALUES (2, NULL)")
    assert "cannot be NULL" in str(exc.value)

def test_composite_constraints(db):
    # Test multiple constraints on one column
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(50) NOT NULL UNIQUE)")
    
    db.execute("INSERT INTO users VALUES (1, 'unique@test.com')")
    
    with pytest.raises(Exception): # Fail PK
        db.execute("INSERT INTO users VALUES (1, 'other@test.com')")
        
    with pytest.raises(Exception): # Fail Unique
        db.execute("INSERT INTO users VALUES (2, 'unique@test.com')")
        
    with pytest.raises(Exception): # Fail Not Null
        db.execute("INSERT INTO users VALUES (3, NULL)")

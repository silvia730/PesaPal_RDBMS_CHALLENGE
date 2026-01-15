
import pytest
import os
import shutil
from rdbms.pydb import Database, TypeSystem

TEST_DB_DIR = "test_data"

@pytest.fixture
def db():
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)
    db = Database(storage_dir=TEST_DB_DIR)
    yield db
    # Cleanup
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)

def test_type_system_validation():
    assert TypeSystem.validate(123, "INTEGER") == 123
    assert TypeSystem.validate("hello", "VARCHAR(10)") == "hello"
    with pytest.raises(ValueError):
        TypeSystem.validate("toolongstring", "VARCHAR(5)")
    assert TypeSystem.validate("true", "BOOLEAN") is True
    assert TypeSystem.validate("2023-01-01", "DATE") == "2023-01-01"

def test_create_table(db):
    schema = {"id": "INTEGER", "name": "VARCHAR(50)"}
    table = db.create_table("users", schema)
    assert table.name == "users"
    assert table.schema == schema
    assert os.path.exists(os.path.join(TEST_DB_DIR, "users.json"))

def test_insert_and_select(db):
    schema = {"id": "INTEGER", "name": "VARCHAR(50)", "active": "BOOLEAN"}
    table = db.create_table("users", schema)
    
    table.insert({"id": 1, "name": "Alice", "active": True})
    table.insert({"id": 2, "name": "Bob", "active": False})
    
    rows = table.select()
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"
    
    # Test filtering
    active_users = table.select({"active": True})
    assert len(active_users) == 1
    assert active_users[0]["name"] == "Alice"

def test_persistence(db):
    schema = {"id": "INTEGER"}
    table = db.create_table("persistent", schema)
    table.insert({"id": 100})
    
    # Reload DB
    new_db = Database(storage_dir=TEST_DB_DIR)
    loaded_table = new_db.get_table("persistent")
    assert len(loaded_table.rows) == 1
    assert loaded_table.rows[0]["id"] == 100

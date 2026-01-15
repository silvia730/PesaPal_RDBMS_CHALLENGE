# PyDB: Custom Relational Database System

**PyDB** is a fully functional, lightweight Relational Database Management System (RDBMS) built from scratch in Python. It demonstrates core database concepts including SQL parsing, transaction management (ACID), indexing, and query execution without relying on any external database libraries (like SQLite or SQLAlchemy).

This project was built to demonstrate deep understanding of database internals and software architecture.

---

## 🚀 Key Features

### 1. SQL Engine
- **Custom Parser**: Regex-based parser supporting a subset of ANSI SQL.
- **Commands**: `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`, `DROP TABLE`.
- **Filtering**: `WHERE` clause support with operators (`=`, `!=`, `>`, `<`, `>=`, `<=`).

### 2. Advanced Query Features
- **JOIN Operations**: Implements **Nested Loop Join** algorithm to support `INNER JOIN` and `LEFT JOIN`.
- **Projections**: Support for specific column selection (e.g., `SELECT users.name, posts.title`).

### 3. Data Integrity & Constraints
- **Primary Keys**: Enforces uniqueness on ID columns.
- **Unique Constraints**: Ensures no duplicate values in specified columns.
- **Not Null Constraints**: Prevents NULL values in critical fields.
- **Type System**: Strict typing for `INTEGER`, `VARCHAR`, `BOOLEAN`, and `DATE`.

### 4. Transactions (ACID)
- **Snapshot Isolation**: Implements atomic transactions using a copy-on-write mechanism.
- **Commands**: `BEGIN`, `COMMIT`, `ROLLBACK`.
- **Concurrency**: Table-level locking ensures thread safety during write operations.

### 5. Indexing
- **Hash Indexing**: In-memory Hash Maps for `O(1)` lookups on equality queries (e.g., `WHERE id = 5`).

---

## 🏗️ Architecture

The system is modularized into distinct components following separation of concerns:

```mermaid
graph TD
    User[Client / Web App] --> Facade[Database Facade (pydb.py)]
    Facade --> Parser[SQL Parser (parser.py)]
    Parser --> AST[Abstract Syntax Tree]
    Facade --> Executor[Query Executor (executor.py)]
    Executor --> AST
    Executor --> Optimizer[Index Selector]
    Executor --> Join[Join Executor (joins.py)]
    Executor --> Constraints[Constraint Manager (constraints.py)]
    Executor --> Transactions[Transaction Manager (transactions.py)]
    Transactions --> Storage[Storage Engine (storage.py)]
    Storage --> Disk[(JSON Files)]
```

- **Storage Engine**: Persists data as JSON files (`db_data/`). Handles file I/O and locking.
- **Transaction Manager**: Manages temporary state for active transactions, applying changes to storage only on `COMMIT`.
- **Executor**: The brain of the DB. Coordinates joins, constraints, and data retrieval.
- **Constraint Manager**: Validates schema requirements before writes.

---

## 💻 Web Application Demo

A Flask-based **Product Inventory Management** system is included to visually demonstrate the database capabilities.

### Features
- **Inventory List**: Displays products joined with their Categories (`LEFT JOIN`).
- **Add/Edit Product**: Full CRUD interface with Constraint validation (shows errors for duplicates).
- **SQL Console**: Power-user interface to run raw SQL and manually control Transactions.

### How to Run

1. **Start the Application**:
   ```bash
   export PATH=$PATH:/home/bugsquasher/.local/bin
   python3 app.py
   ```
2. **Access**: Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🛠️ CLI Interface (REPL)

Interact with the database directly from the terminal:

```bash
python3 repl.py
```

**Example Session:**
```sql
pydb> BEGIN;
pydb> INSERT INTO inventory VALUES (10, 'Test Item', 500, 10, '2025-01-01', 1);
pydb> SELECT * FROM inventory WHERE id = 10;
pydb> ROLLBACK;
pydb> SELECT * FROM inventory WHERE id = 10; -- Returns empty
```

---

## 🧪 Testing

The project includes a comprehensive test suite using `pytest` covering:
- Unit tests for Parser regex logic.
- Integration tests for Joins and Constraints.
- Transaction atomicity verification.

Run tests:
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```

---

## 🔮 Future Improvements
- **B-Tree Indexing**: to support range queries (`<`, `>`) efficiently.
- **Query Optimizer**: Cost-based optimization to choose between Nested Loop and Hash Joins.
- **Durability**: Write-Ahead Logging (WAL) for better crash recovery.

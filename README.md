# PyDB — A Custom Relational Database Management System (RDBMS)

PyDB is a lightweight yet fully functional Relational Database Management System built entirely from scratch in Python. The project demonstrates a deep understanding of database internals, software architecture, and system design by implementing core RDBMS features without relying on external database engines such as SQLite or ORM frameworks like SQLAlchemy.

## 🎯 Project Motivation

This project was built to demonstrate a deep, fundamental understanding of how databases work at their core—from parsing SQL to guaranteeing ACID properties. Rather than using existing database libraries, I implemented each component from scratch to showcase system design and algorithmic thinking.
---
## 🚀 Quick Installation

```bash
# Clone the repository
git clone https://github.com/your-username/pydb-rdbms.git
cd pydb-rdbms

# Install dependencies (only 2 required!)
pip install -r requirements.txt

# Run the web demo
python app.py
# Open http://localhost:5000

#### Verification Screenshot (Proof It Works)**
```markdown
## ✅ Proof of Working Features

| Feature | Screenshot | What It Demonstrates |
|---------|------------|---------------------|
| **Web Interface** | ![Web App](screenshots/web-app.png) | Real CRUD application |
| **SQL Console** | ![SQL Interface](screenshots/sql-console.png) | Raw SQL execution |
| **JOIN Results** | ![Join Output](screenshots/join-output.png) | Relational queries working |
| **Constraint Error** | ![Error](screenshots/constraint-error.png) | Data integrity enforcement |
## ✨ Features Overview

### SQL Engine

* Custom-built, regex-based SQL parser supporting a subset of ANSI SQL
* Supported commands:

  * `CREATE TABLE`
  * `INSERT`
  * `SELECT`
  * `UPDATE`
  * `DELETE`
  * `DROP TABLE`
* `WHERE` clause filtering with comparison operators (`=`, `!=`, `>`, `<`, `>=`, `<=`)

### Query Capabilities

* **Joins**: Supports `INNER JOIN` and `LEFT JOIN` using a Nested Loop Join algorithm
* **Projections**: Column-level selection (e.g., `SELECT users.name, orders.total`)

### Data Integrity & Constraints

* **Primary Key Enforcement**
* **Unique Constraints**
* **NOT NULL Constraints**
* **Strict Type System**:

  * `INTEGER`
  * `VARCHAR`
  * `BOOLEAN`
  * `DATE`

### Transactions (ACID Properties)

* Atomic transactions implemented using snapshot isolation (copy-on-write)
* Transaction commands:

  * `BEGIN`
  * `COMMIT`
  * `ROLLBACK`
* Table-level locking to ensure thread-safe write operations

### Indexing

* In-memory Hash Indexes for constant-time (`O(1)`) lookups on equality predicates

---

## 🏗️ System Architecture

PyDB follows a modular architecture with clear separation of concerns:

```
Client / Web App
        ↓
Database Facade (pydb.py)
        ↓
     SQL Parser
        ↓
 Abstract Syntax Tree (AST)
        ↓
 Query Executor
        ↓
 ┌───────────────┬─────────────────┬──────────────────┐
 │ Join Executor │ Constraint Mgmt │ Transaction Mgmt │
 └───────────────┴─────────────────┴──────────────────┘
        ↓
  Storage Engine (JSON Persistence)
```

### Component Responsibilities

* **Parser**: Converts SQL input into structured AST representations
* **Executor**: Coordinates query execution, joins, constraints, and indexing
* **Transaction Manager**: Handles transactional state and isolation
* **Storage Engine**: Persists tables as JSON files and manages disk I/O
* **Constraint Manager**: Enforces schema-level rules prior to writes

---

## 🌐 Web Application Demo

PyDB includes a Flask-based Product Inventory Management web application to demonstrate real-world usage.

### Demo Features

* Product inventory listing with category data via `LEFT JOIN`
* Full CRUD operations with constraint validation
* Embedded SQL console for manual queries and transaction control

### Running the Web App

```bash
export PATH=$PATH:/home/bugsquasher/.local/bin
python3 app.py
```

Access the application at:

```
http://127.0.0.1:5000
```

---

## 🖥️ Command-Line Interface (REPL)

PyDB provides an interactive REPL for executing SQL commands directly.

### Start the REPL

```bash
python3 repl.py
```

### Example Session

```sql
pydb> BEGIN;
pydb> INSERT INTO inventory VALUES (10, 'Test Item', 500, 10, '2025-01-01', 1);
pydb> SELECT * FROM inventory WHERE id = 10;
pydb> ROLLBACK;
pydb> SELECT * FROM inventory WHERE id = 10;
```

---

## 🧪 Testing

The project includes a comprehensive automated test suite built with `pytest`.

### Test Coverage

* SQL parser unit tests
* Join execution and constraint validation
* Transaction atomicity and rollback correctness

### Run Tests

```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```

---

## 🔮 Future Enhancements

* B-Tree or LSM-based indexing for efficient range queries
* Cost-based query optimizer
* Write-Ahead Logging (WAL) for crash recovery and durability
* Improved concurrency control (row-level locking)

---

## Designed and buillt by :
DEVELOPER : Silvia Njeri
EMAIL: silvianjeri730@gmail.com


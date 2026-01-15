
import argparse
import sys
from rdbms.pydb import Database
from tabulate import tabulate # External lib? May not exist.
# Fallback table printer

def print_table(data):
    if not data:
        print("No results.")
        return
    if isinstance(data, list) and data and isinstance(data[0], list):
        # List of lists (rows)
        for row in data:
            print(row)
    else:
        print(data)

def main():
    parser = argparse.ArgumentParser(description="Custom RDBMS Shell")
    parser.add_argument("--db", default="db_data", help="Database directory")
    args = parser.parse_args()

    db = Database(data_dir=args.db)
    print("Welcome to PyDB REPL. Type 'exit' to quit.")
    
    while True:
        try:
            try:
                sql = input("pydb> ")
            except EOFError:
                break
                
            if sql.strip().lower() in ('exit', 'quit'):
                break
            if not sql.strip():
                continue
                
            result = db.execute(sql)
            print_table(result)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

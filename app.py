
from flask import Flask, render_template, request, redirect, url_for, flash
import os
from rdbms.pydb import Database
from rdbms.executor import Executor

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Initialize DB
DB_DIR = os.path.join(os.getcwd(), 'db_data')
db = Database(data_dir=DB_DIR)

# Ensure Tables Exist
try:
    # 1. Categories Table (Constraint: ID PK, Name Unique)
    db.execute("CREATE TABLE categories (id INTEGER PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL)")
    # Default categories
    try:
        db.execute("INSERT INTO categories VALUES (1, 'Electronics')")
        db.execute("INSERT INTO categories VALUES (2, 'Books')")
        db.execute("INSERT INTO categories VALUES (3, 'Clothing')")
    except:
        pass # Already exist
        
    # 2. Inventory Table with Constraints and Relation
    # Note: Foreign Key syntax is parsed but enforcement is manual or not fully implemented in this phase.
    # We focus on PK, Unique, Not Null and Joining.
    cols = "id INTEGER PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL, price INTEGER, quantity INTEGER, restocked DATE, category_id INTEGER"
    db.execute(f"CREATE TABLE inventory ({cols})")
except Exception as e:
    # print(f"Init Error: {e}")
    pass

@app.route('/')
def index():
    # Fetch inventory with JOIN to get Category Name
    items = []
    try:
        # JOIN Query
        sql = """
        SELECT inventory.id, inventory.name, inventory.price, inventory.quantity, inventory.restocked, categories.name 
        FROM inventory 
        LEFT JOIN categories ON inventory.category_id = categories.id
        """
        raw_data = db.query(sql)
        # Map list to dict for template
        for row in raw_data:
             items.append({
                 'id': row[0],
                 'name': row[1],
                 'price': row[2],
                 'quantity': row[3],
                 'restocked': row[4],
                 'category': row[5] if row[5] else 'Uncategorized'
             })
    except Exception as e:
        flash(f"Error loading inventory: {e}", "danger")
    
    return render_template('inventory_list.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        try:
            name = request.form['name']
            price = request.form['price']
            qty = request.form['quantity']
            date = request.form['restocked']
            cat_id = request.form['category_id']
            
            # Simple ID generation: max + 1
            existing = db.query("SELECT id FROM inventory")
            new_id = 1
            if existing:
                ids = [r[0] for r in existing]
                new_id = max(ids) + 1
            
            sql = f"INSERT INTO inventory VALUES ({new_id}, '{name}', {price}, {qty}, '{date}', {cat_id})"
            db.execute(sql)
            flash("Item added successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error: {e}", "danger")  # Should show constraint error
            
    # Load categories for dropdown
    categories = []
    try:
        categories = db.query("SELECT * FROM categories")
    except:
        pass
    return render_template('add_item.html', categories=categories)

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if request.method == 'POST':
        try:
            name = request.form['name']
            price = request.form['price']
            qty = request.form['quantity']
            date = request.form['restocked']
            cat_id = request.form['category_id']
            
            # Update Query
            sql = f"UPDATE inventory SET name='{name}', price={price}, quantity={qty}, restocked='{date}', category_id={cat_id} WHERE id={item_id}"
            db.execute(sql)
            
            flash("Item updated successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error updating item: {e}", "danger")
    
    # Existing item fetch
    item = {}
    try:
        # We need raw category_id here
        raw = db.query(f"SELECT * FROM inventory WHERE id={item_id}")
        if raw:
            r = raw[0]
            item = {
                'id': r[0],
                'name': r[1],
                'price': r[2],
                'quantity': r[3],
                'restocked': r[4],
                'category_id': r[5]
            }
    except Exception as e:
        flash(f"Error fetching item: {e}", "warning")
        
    # Categories for dropdown
    categories = []
    try:
         categories = db.query("SELECT * FROM categories")
    except:
         pass
         
    return render_template('edit_item.html', item=item, categories=categories)

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    try:
        db.execute(f"DELETE FROM inventory WHERE id = {item_id}")
        flash("Item deleted.", "success")
    except Exception as e:
        flash(f"Error deleting: {e}", "danger")
    return redirect(url_for('index'))

@app.route('/query', methods=['GET', 'POST'])
def query_interface():
    result = None
    sql = ""
    error = None
    if request.method == 'POST':
        # Check for quick action
        quick = request.form.get('quick_action')
        if quick:
            sql = quick
        else:
            sql = request.form['sql']
            
        try:
            result = db.execute(sql)
            if quick:
                 flash(f"Executed: {quick}", "success")
        except Exception as e:
            error = str(e)
            
    return render_template('query.html', result=result, sql=sql, error=error)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

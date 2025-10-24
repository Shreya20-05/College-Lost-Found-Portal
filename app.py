import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

# Initialize Flask App
app = Flask(__name__)
app.secret_key = 'a_very_secret_key_for_production'
app.config['UPLOAD_FOLDER'] = 'uploads'

# --- MySQL Configuration ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'shreya@2005', # Your MySQL password
    'database': 'lost_found_db'
}

# --- Database Connection Helper ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# --- Database Initialization ---
def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        with open('schema.sql', 'r') as f:
            for statement in f.read().split(';'):
                if statement.strip():
                    cursor.execute(statement)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully.")

# --- CLI Command for Admin Creation ---
@app.cli.command("create-admin")
def create_admin_command():
    conn = get_db_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", ('admin',))
        if cursor.fetchone():
            cursor.execute("UPDATE users SET password = %s WHERE username = %s", ('admin123', 'admin'))
            print("Admin password updated.")
        else:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", ('admin', 'admin123', 'admin'))
            print("Admin user created.")
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# --- Main Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('admin_dashboard')) if session.get('role') == 'admin' else redirect(url_for('student_home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if not conn: return render_template('login.html', error='Database connection failed.')
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if not conn: return render_template('register.html', error='Database connection failed.')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)', (username, password, 'student'))
            conn.commit()
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            return render_template('register.html', error='Username already exists')
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Student Routes ---

@app.route('/home')
def student_home():
    if 'user_id' not in session or session.get('role') != 'student': return redirect(url_for('login'))
    return render_template('student_home.html', username=session['username'])

@app.route('/report_page')
def report_page():
    if 'user_id' not in session or session.get('role') != 'student': return redirect(url_for('login'))
    return render_template('student_report.html', username=session['username'])

@app.route('/my_reports')
def my_reports():
    if 'user_id' not in session or session.get('role') != 'student': return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM items WHERE user_id = %s ORDER BY report_date DESC', (session['user_id'],))
    my_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('student_my_reports.html', username=session['username'], items=my_items)

# In app.py, find and update the community_reports route

@app.route('/community_reports')
def community_reports():
    if 'user_id' not in session or session.get('role') != 'student': return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get search query and item type from URL parameters
    search_query = request.args.get('query', '')
    item_type_filter = request.args.get('item_type', '')

    sql_query = """
        SELECT items.*, users.username 
        FROM items 
        JOIN users ON items.user_id = users.id 
        WHERE 1=1 -- This is a placeholder that always true, making it easy to append conditions
    """
    query_params = []

    # Add search query condition
    if search_query:
        sql_query += " AND (items.description LIKE %s OR items.location LIKE %s)"
        query_params.append(f"%{search_query}%")
        query_params.append(f"%{search_query}%")

    # Add item type filter condition
    if item_type_filter:
        sql_query += " AND items.item_type = %s"
        query_params.append(item_type_filter)
    
    sql_query += " ORDER BY items.report_date DESC" # Always order by date

    cursor.execute(sql_query, tuple(query_params))
    all_items = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('community_reports.html', username=session['username'], items=all_items)

@app.route('/report', methods=['POST'])
def report_item():
    if 'user_id' not in session: return redirect(url_for('login'))
    item_type = request.form['type']
    description = request.form['description']
    location = request.form['location']
    student_name = request.form.get('student_name')
    department = request.form.get('department')
    roll_no = request.form.get('roll_no')
    file = request.files.get('image')
    filename = ''
    if file and file.filename:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = ('INSERT INTO items (user_id, item_type, description, location, image_path, student_name, department, roll_no) '
           'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)')
    values = (session['user_id'], item_type, description, location, filename, student_name, department, roll_no)
    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('my_reports'))

@app.route('/update_status/<int:item_id>', methods=['POST'])
def update_status(item_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET status = 'found_by_owner' WHERE id = %s AND user_id = %s", (item_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('my_reports'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Admin Routes ---

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin': return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT items.*, users.username FROM items JOIN users ON items.user_id = users.id ORDER BY report_date DESC')
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_dashboard.html', items=items)

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if 'user_id' not in session or session.get('role') != 'admin': return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# --- Main Execution ---
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM users LIMIT 1")
            cursor.fetchone() 
        except mysql.connector.Error as err:
            if err.errno == 1146:
                print("Tables not found. Initializing database...")
                init_db()
                print("Database created. Please run 'flask create-admin' to set up the admin user.")
        finally:
            cursor.close()
            conn.close()
    app.run(debug=True)
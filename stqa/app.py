import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, cli
import os

# Initialize the Flask application
app = Flask(__name__)
# Set the path for the database file
app.config['DATABASE'] = 'todo.db'

# --- Database Management Functions ---

def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context and stores it in `g`.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # This allows accessing columns by name, like a dictionary
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """
    Closes the database connection at the end of the request.
    This is called automatically by Flask.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    Initializes the database by running the schema.sql script.
    This will create the tables and insert initial data.
    """
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('init-db')
def init_db_command():
    """Defines a command-line command `flask init-db` to create the database."""
    with app.app_context():
        init_db()
    cli.echo('Initialized the database.')


# --- Application Routes ---

@app.route('/')
def index():
    """
    Renders the main page with the list of all todo items from the database.
    """
    db = get_db()
    # Fetch all todos from the database, ordering by ID
    todos_cursor = db.execute('SELECT id, task, done FROM todos ORDER BY id')
    todos = todos_cursor.fetchall()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    """
    Handles the addition of a new todo item to the database.
    """
    task_content = request.form.get('task')
    # Add the task only if the content is not empty and not just whitespace
    if task_content and task_content.strip():
        db = get_db()
        db.execute(
            'INSERT INTO todos (task, done) VALUES (?, ?)',
            (task_content.strip(), False) # New tasks are not done by default
        )
        db.commit()
    # Redirect back to the main page to see the updated list
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit(todo_id):
    """
    Handles editing of an existing task.
    GET: Displays the edit page for a specific task.
    POST: Updates the task in the database.
    """
    db = get_db()
    todo = db.execute('SELECT id, task FROM todos WHERE id = ?', (todo_id,)).fetchone()

    if todo is None:
        # If no todo is found with that ID, redirect to the homepage.
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_task_content = request.form.get('task')
        if new_task_content and new_task_content.strip():
            db.execute(
                'UPDATE todos SET task = ? WHERE id = ?',
                (new_task_content.strip(), todo_id)
            )
            db.commit()
        return redirect(url_for('index'))

    # For a GET request, render the edit page
    return render_template('edit.html', todo=todo)


@app.route('/update/<int:todo_id>')
def update(todo_id):
    """
    Toggles the 'done' status of a specific todo item in the database.
    """
    db = get_db()
    # First, get the current status of the todo item
    todo = db.execute('SELECT done FROM todos WHERE id = ?', (todo_id,)).fetchone()
    if todo:
        # Toggle the boolean value (0 becomes 1, 1 becomes 0)
        new_status = not todo['done']
        db.execute('UPDATE todos SET done = ? WHERE id = ?', (new_status, todo_id))
        db.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    """
    Deletes a todo item from the database based on its ID.
    """
    db = get_db()
    db.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # This check is a convenience for running `python app.py` directly.
    # It creates the database on the first run if it doesn't exist.
    # The recommended way to initialize is `flask init-db`.
    if not os.path.exists(app.config['DATABASE']):
        with app.app_context():
            init_db()
        print(f"Database '{app.config['DATABASE']}' created and initialized.")

    app.run(debug=True, port=5001)


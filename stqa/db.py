import sqlite3

# This will create todo.db in the current folder
conn = sqlite3.connect('todo.db')
cursor = conn.cursor()

# Create the todos table
"""
cursor.execute('''
CREATE TABLE todos (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0
);
''')
"""

cursor.execute("""
INSERT INTO todos (task, done) VALUES
('Learn Flask fundamentals', 1),
('Build a Todo List App', 1),
('Switch to using SQLite', 1),
('Perform black-box testing', 0),
('Perform white-box testing', 0);               
""")
               
conn.commit()
conn.close()

print("Database and table created!")

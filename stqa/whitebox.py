import os
import tempfile
import unittest
import sqlite3
from app import app, init_db, get_db

class TodoAppWhiteBoxTest(unittest.TestCase):

    def setUp(self):
        """Set up a temporary database and Flask test client."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        app.config['TESTING'] = True
        self.client = app.test_client()

        with app.app_context():
            init_db()

    def tearDown(self):
        """Close and remove the temporary database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_add_task(self):
        """Test inserting a new task into the DB."""
        response = self.client.post('/add', data={'task': 'Test Task'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with app.app_context():
            db = get_db()
            task = db.execute('SELECT task FROM todos WHERE task = ?', ('Test Task',)).fetchone()
            self.assertIsNotNone(task, "Task was not inserted")

    def test_edit_task(self):
        """Test editing an existing task."""
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO todos (task, done) VALUES (?, ?)", ("Old Task", False))
            db.commit()
            task_id = db.execute("SELECT id FROM todos WHERE task = ?", ("Old Task",)).fetchone()['id']

        response = self.client.post(f'/edit/{task_id}', data={'task': 'Updated Task'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with app.app_context():
            db = get_db()
            updated = db.execute("SELECT task FROM todos WHERE id = ?", (task_id,)).fetchone()
            self.assertEqual(updated['task'], "Updated Task")

    def test_update_toggle_done(self):
        """Test toggling a task's done status."""
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO todos (task, done) VALUES (?, ?)", ("Toggle Task", False))
            db.commit()
            task_id = db.execute("SELECT id FROM todos WHERE task = ?", ("Toggle Task",)).fetchone()['id']

        self.client.get(f'/update/{task_id}', follow_redirects=True)

        with app.app_context():
            db = get_db()
            updated = db.execute("SELECT done FROM todos WHERE id = ?", (task_id,)).fetchone()
            self.assertEqual(updated['done'], 1)  # True

    def test_delete_task(self):
        """Test deleting a task from the DB."""
        with app.app_context():
            db = get_db()
            db.execute("INSERT INTO todos (task, done) VALUES (?, ?)", ("Delete Task", False))
            db.commit()
            task_id = db.execute("SELECT id FROM todos WHERE task = ?", ("Delete Task",)).fetchone()['id']

        self.client.get(f'/delete/{task_id}', follow_redirects=True)

        with app.app_context():
            db = get_db()
            deleted = db.execute("SELECT * FROM todos WHERE id = ?", (task_id,)).fetchone()
            self.assertIsNone(deleted, "Task was not deleted")

if __name__ == '__main__':
    unittest.main()

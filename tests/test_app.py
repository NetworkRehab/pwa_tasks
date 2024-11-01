import unittest

from app import app, db, Task, CompletedTask

class AppTestCase(unittest.TestCase):
    def setUp(self):
        # Set up a test client and use an in-memory database
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        # Clean up after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_index_page(self):
        # Test that the index page loads correctly
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Daily Tasks', response.data)
    
    def test_add_task(self):
        # Test adding a new task
        response = self.app.post('/add', data={'task': 'Test Task'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Task', response.data)
    
    def test_toggle_task(self):

        # Test toggling a task's completion status and logging it

        with app.app_context():
            task = Task(name='Test Task')
            db.session.add(task)
            db.session.commit()
            task_id = task.id

            # Mark as completed
            response = self.app.post(f'/toggle/{task_id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Check task is marked completed
            task = Task.query.get(task_id)
            self.assertTrue(task.completed)

            # Check a CompletedTask entry was created
            completed_tasks = CompletedTask.query.filter_by(task_id=task_id).all()
            self.assertEqual(len(completed_tasks), 1)

            # Toggle back to incomplete
            response = self.app.post(f'/toggle/{task_id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Task should be incomplete
            task = Task.query.get(task_id)
            self.assertFalse(task.completed)

            # CompletedTask entry should still exist
            completed_tasks = CompletedTask.query.filter_by(task_id=task_id).all()
            self.assertEqual(len(completed_tasks), 1)

    
    def test_update_points(self):
        # Test updating a task's points
        with app.app_context():
            task = Task(name='Test Task')
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        response = self.app.post(f'/update_points/{task_id}', data={'points': '10'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            task = Task.query.get(task_id)
            self.assertEqual(task.points, 10)
    
    def test_clear_tasks(self):
        # Test clearing all tasks
        with app.app_context():
            task = Task(name='Test Task')
            db.session.add(task)
            db.session.commit()
        response = self.app.post('/clear', follow_redirects=True)
        self.assertEqual(response.status_code, 204)
        with app.app_context():
            tasks = Task.query.all()
            self.assertEqual(len(tasks), 0)

if __name__ == '__main__':
    unittest.main()

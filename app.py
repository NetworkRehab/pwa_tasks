from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import defaultdict

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configure SQLite database
if app.config.get('TESTING'):
    # Use in-memory database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.String(50), nullable=True)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Task {self.name}>"

class CompletedTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    completed_at = db.Column(db.String(50), nullable=True)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<CompletedTask {self.name} at {self.completed_at}>"

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tasks = Task.query.all()
    # Fetch all completed tasks from CompletedTask table
    completed_tasks = CompletedTask.query.order_by(CompletedTask.id.desc()).all()

    # Calculate total points per day
    totals_per_day = defaultdict(int)
    for task in completed_tasks:
        if task.completed_at:
            date_str = task.completed_at.split(' ')[0]
            totals_per_day[date_str] += task.points

    return render_template('index.html', tasks=tasks, completed_tasks=completed_tasks, totals_per_day=totals_per_day)

@app.route('/add', methods=['POST'])
def add():
    task_name = request.form['task']
    new_task = Task(name=task_name)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    if task.completed:
        # Mark task as completed
        task.completed_at = datetime.now().strftime("%m-%d-%Y %I:%M %p")
        # Log the completion event
        completed_task = CompletedTask(
            task_id=task.id,
            name=task.name,
            completed_at=task.completed_at,
            points=task.points
        )
        db.session.add(completed_task)
    else:
        # Unmark task as completed
        task.completed_at = None
        # Do not remove entries from CompletedTask
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_points/<int:task_id>', methods=['POST'])
def update_points(task_id):
    points = request.form.get('points', 0)
    task = Task.query.get_or_404(task_id)
    try:
        task.points = int(points)
    except ValueError:
        task.points = 0
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_tasks():
    Task.query.delete()
    db.session.commit()
    return '', 204  # No Content

if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)
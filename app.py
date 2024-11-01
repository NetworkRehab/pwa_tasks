from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import defaultdict

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configure SQLite database
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

class PointsBank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_points = db.Column(db.Integer, default=0)

# Create the database and tables
with app.app_context():
    db.create_all()
    # Initialize PointsBank if it doesn't exist
    if not PointsBank.query.first():
        bank = PointsBank(total_points=0)
        db.session.add(bank)
        db.session.commit()

@app.route('/')
def index():
    tasks = Task.query.all()
    completed_tasks = Task.query.filter_by(completed=True).all()
    
    # Calculate total points per day
    totals_per_day = defaultdict(int)
    for task in completed_tasks:
        if task.completed_at:
            date_str = task.completed_at.split(' ')[0]  # Extract MM-DD-YYYY
            totals_per_day[date_str] += task.points
    
    bank = PointsBank.query.first()
    bank_total = bank.total_points if bank else 0
    return render_template('index.html', tasks=tasks, completed_tasks=completed_tasks, totals_per_day=totals_per_day, bank_total=bank_total)

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
        # Format the date as MM-DD-YYYY and time as HH:MM AM/PM
        task.completed_at = datetime.now().strftime("%m-%d-%Y %I:%M %p")
    else:
        task.completed_at = None
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

@app.route('/add_to_bank', methods=['POST'])
def add_to_bank():
    amount = request.form.get('amount', 0)
    try:
        amount = int(amount)
    except ValueError:
        amount = 0
    bank = PointsBank.query.first()
    bank.total_points += amount
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/remove_from_bank', methods=['POST'])
def remove_from_bank():
    amount = request.form.get('amount', 0)
    try:
        amount = int(amount)
    except ValueError:
        amount = 0
    bank = PointsBank.query.first()
    bank.total_points -= amount
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)
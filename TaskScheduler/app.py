from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import urllib.parse
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc:///@localhost/TaskDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=Lenovo101\SQLEXPRESS;"  # Or your instance: localhost\\SQLEXPRESS
    "DATABASE=TaskDB;"
    "Trusted_Connection=yes;"
)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
# Or with credentials: 'mssql+pyodbc://username:password@localhost/TaskDB?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='to do')  # 'to do', 'in progress', 'complete'
    due_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        status = request.form['status']
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()

        task = Task(title=title, description=description, status=status, due_date=due_date)
        db.session.add(task)
        db.session.commit()
        flash('Task created')
        return redirect(url_for('index'))

    start = request.args.get('start_date')
    end = request.args.get('end_date')

    query = Task.query
    if start and end:
        s = datetime.strptime(start, '%Y-%m-%d').date()
        e = datetime.strptime(end, '%Y-%m-%d').date()
        query = query.filter(Task.due_date.between(s, e))

    tasks = query.order_by(Task.due_date).all()
    return render_template('index.html', tasks=tasks)

@app.route('/update/<int:task_id>', methods=['GET', 'POST'])
def update(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        new_title = request.form['title']
        new_desc = request.form['description']
        new_status = request.form['status']
        new_due = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()

        if task.status != 'complete':
            task.title = new_title
            task.description = new_desc
        task.status = new_status
        task.due_date = new_due
        db.session.commit()
        flash('Updated')
        return redirect(url_for('index'))

    return render_template('update.html', task=task)

@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Deleted')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
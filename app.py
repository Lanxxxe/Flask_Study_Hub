from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'poiuytrewq56321'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)
    course = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    note = db.Column(db.String(1000), nullable=True)
    deadline = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))

    return render_template('index.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        password = form.password.data
        new_user = User(name=name, username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/addWork', methods=['POST'])
def addWork():
    topic = request.form.get('topic')
    course = request.form.get('course')
    description = request.form.get('description')
    note = request.form.get('note')
    deadline = request.form.get('deadline')
    user_id = session.get('user_id')

    if user_id is not None:
        user = User.query.get(user_id)
        if user:
            added_task = Task(topic=topic, course=course, description=description, note=note, deadline=deadline, user_id=user.id)
            db.session.add(added_task)
            db.session.commit()

            return redirect(url_for('home'))
    
    flash('User not found. Please log in again.', 'danger')
    return redirect(url_for('login'))

@app.route('/deleteWork/<int:task_id>', methods=['GET'])
def deleteWork(task_id):
    user_id = session.get('user_id')

    if user_id is not None:
        user = User.query.get(user_id)
        if user:
            task_to_delete = Task.query.get(task_id)

            if task_to_delete:
                if task_to_delete.user_id == user.id:
                    db.session.delete(task_to_delete)
                    db.session.commit()
                    return redirect(url_for('home'))
                else:
                    flash('Unauthorized to delete this task.', 'danger')
            else:
                flash('Task not found.', 'danger')
    
    return redirect(url_for('login'))

@app.route('/dashboard')
def home():
    user_id = session.get('user_id')
    if user_id is not None:
        user = User.query.filter_by(id=user_id).first()
        if user:
            tasks = Task.query.filter_by(user=user).all()
            return render_template('dashboard.html', user=user, tasks=tasks)

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

#Importing required libraries/packages
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_gravatar import Gravatar
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
import os

#Importing forms
from forms import LoginForm, RegisterForm, NewTaskForm

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

#Creating a Flask App
app = Flask(__name__)

#Creating a CSRF key for wt forms to work
app.config["SECRET_KEY"] = os.getenv("FLASK_KEY")

#Creating bootstrap for styling
bootstrap = Bootstrap5(app=app)

# For adding profile images to the comment section
gravatar = Gravatar(app,
                    size=45,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

#Creating a Database
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///todo.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app=app)

#Creating Modal Classes for the Database
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password:Mapped[str] = mapped_column(String, nullable=False)

    #Creating a relationship between user and tasks
    tasks = relationship("Task", back_populates="task_author")


class Task(db.Model):
    __tablename__ = "tasks"
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String, nullable=False)
    description:Mapped[str] = mapped_column(String, nullable=False)
    deadline:Mapped[str] = mapped_column(String, nullable=False)
    status:Mapped[str] = mapped_column(String, nullable=False)

    #Creating a relationship between user and tasks
    author_id:Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    task_author = relationship("User", back_populates="tasks")

with app.app_context():
    db.create_all()

#Configuring Flask-Login
login_manager = LoginManager()
login_manager.init_app(app=app)

# Creating a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

@app.route("/")
def home():
    if current_user.is_authenticated:
        user = current_user
    else:
        user = None
    return render_template("index.html", user=user)

@app.route("/login", methods=["POST","GET"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        #Checking this email in database
        result = db.session.execute(db.select(User).where(User.email==login_form.email.data))
        user = result.scalar()

        if not user:
            flash(message="This email is not registered. Try signing up with us.")
            return redirect(url_for('register'))
        
        #Checking for password
        elif not check_password_hash(user.password, login_form.password.data):
            flash(message="Kindly recheck the entered password.")

        else:
            login_user(user=user)
            return redirect(url_for('todo_list'))


    return render_template("login.html", form=login_form)

@app.route("/register", methods=["POST","GET"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email==register_form.email.data))
        user = result.scalar()

        #Checking if email already exists
        if user:
            flash("This email is associated with an account. Try logging in instead.")
            return redirect(url_for('login'))
        
        Hashed_password = generate_password_hash(password=register_form.password.data, method="pbkdf2:sha256", salt_length=8)
        new_user = User(
            email=register_form.email.data,
            name=register_form.name.data,
            password=Hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("todo_list"))
    
    return render_template("register.html", form=register_form)

@app.route("/logout")
@login_required
def log_out():
    logout_user()
    return redirect(url_for('home'))


@app.route("/todo_list")
@login_required
def todo_list():
    result = db.session.execute(db.select(Task).where(Task.author_id == current_user.id))
    tasks = result.scalars().all()
    user = current_user
    return render_template("todo.html", tasks=tasks, user=user)

@app.route("/add_task", methods=["POST","GET"])
@login_required
def add_task():
    add_task_form = NewTaskForm()
    if add_task_form.validate_on_submit():
        new_task = Task(
            title = add_task_form.title.data.title(),
            description = add_task_form.description.data.title(),
            deadline = add_task_form.deadline.data,
            status = add_task_form.status.data.title(),
            task_author = current_user
        )
        
        #Adding new task to database
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('todo_list'))
    
    return render_template("add.html", form=add_task_form)

@app.route("/todo_list/<title>")
@login_required
def show_task(title):
    result = db.session.execute(db.select(Task).where(Task.title == title))
    task = result.scalar()
    return render_template("task.html", task=task)


@app.route("/delete_task/<title>")
@login_required
def delete_task(title):
    result = db.session.execute(db.select(Task).where(Task.title == title))
    task = result.scalar()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('todo_list'))

@app.route("/complete_task/<title>")
@login_required
def complete_task(title):
    result = db.session.execute(db.select(Task).where(Task.title == title))
    task = result.scalar()
    task.status = "Completed"
    db.session.commit()
    return redirect(url_for('todo_list'))


#Running the flask app
if __name__ == "__main__":
    app.run(debug=True)
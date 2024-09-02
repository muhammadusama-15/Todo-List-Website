#Importing libraries
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, StringField
from wtforms.validators import DataRequired

#Creating Login Form
class LoginForm(FlaskForm):
    email = EmailField(label="Email:", validators=[DataRequired()])
    password = PasswordField(label="Password:", validators=[DataRequired()])
    login_button = SubmitField(label="Sign In", validators=[DataRequired()])

class RegisterForm(FlaskForm):
    name = StringField(label="Name:", validators=[DataRequired()])
    email = EmailField(label="Email:", validators=[DataRequired()])
    password = PasswordField(label="Password:", validators=[DataRequired()])
    regiter_button = SubmitField(label="Sign Up", validators=[DataRequired()])

class NewTaskForm(FlaskForm):
    title = StringField(label="Title:" ,validators=[DataRequired()])
    description = StringField(label="Brief Description:" ,validators=[DataRequired()])
    deadline = StringField(label="Deadline (YYYY-MM-DD):" ,validators=[DataRequired()])
    status = StringField(label="Status 'Pending or Completed':", validators=[DataRequired()])
    add_button = SubmitField(label="Add Task", validators=[DataRequired()])
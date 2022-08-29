from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Email

class RegisterForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired('Please enter a username')])
    password = PasswordField("Password:", validators=[InputRequired('Please enter a password')])
    email = StringField("Email:", validators=[InputRequired('Please enter your email adress')])
    first_name = StringField("First Name:", validators=[InputRequired('Please enter your name')])
    last_name = StringField("Last Name:", validators=[InputRequired('Please enter your last name')])

class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired('Username is required')])
    password = PasswordField("Password:", validators=[InputRequired('Password is required')])

class FeedbackForm(FlaskForm):
    title = StringField("Title:", validators=[InputRequired('Please enter a title')])
    content = TextAreaField("Content:", validators=[InputRequired('Please fill out the form')])

class PasswordResetForm(FlaskForm):
    email = StringField("Email:", validators=[InputRequired('Please enter your email adress')])

class PasswordResetPassword(FlaskForm):
    email = StringField("Email:", validators=[InputRequired('Please enter your email adress')])
    password = PasswordField("New Password:", validators=[InputRequired('Please enter a password')])
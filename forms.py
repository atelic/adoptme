from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password', [
        validators.DataRequired(),
    ])


class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    github_id = StringField('GitHub username', [validators.DataRequired()])

class ApplicationForm(FlaskForm):
    justification = StringField('Justification', [validators.Length(min=0, max=200)])

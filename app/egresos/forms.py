from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField

class CapturaEgresos(FlaskForm):
    username = TextField('Username', id='username_create')
    email = TextField('Email')
    password = PasswordField('Password', id='pwd_create')

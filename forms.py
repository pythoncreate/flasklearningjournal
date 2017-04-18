from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, DateField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo, Optional)
from models import User


def name_exists(form,field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists')


def email_exists(form,field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('Email with that name already exists')


class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters"
                        "numbers, and underscores only.")
    ),
     name_exists
    ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=5),
            EqualTo('password2', message='Passwords must match')
        ]
    )
    password2 = PasswordField(
        'Confirm Password',
        validators = [DataRequired()]
    )

class LoginForm(Form):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class PostForm(Form):
    timestamp = DateField('Start Date', format='%d/%m/%Y', validators=[Optional()])
    title = StringField('Title', validators=[DataRequired()])
    timespent = StringField('TimeSpent', validators=[DataRequired()])
    learned = TextAreaField('Learned', validators=[DataRequired()])
    resources = TextAreaField('Resources', validators=[DataRequired()])
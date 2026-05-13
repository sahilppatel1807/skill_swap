from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional


class LoginForm(FlaskForm):
    identifier = StringField(
        'Email or Nickname',
        validators=[
            DataRequired(message='Email or nickname is required.')
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.')
        ]
    )


class SignupForm(FlaskForm):
    name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Full name is required.'),
            Length(max=100)
        ]
    )

    nickname = StringField(
        'Nickname',
        validators=[
            DataRequired(message='Nickname is required.'),
            Length(max=80)
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Please enter a valid email address.'),
            Length(max=150)
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=8, message='Password must be at least 8 characters long.'),
            Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d).+$',
                message='Password must include at least one letter and one number.'
            )
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords do not match.')
        ]
    )

    course = StringField(
        'Course / Major',
        validators=[
            Optional(),
            Length(max=150)
        ]
    )

    bio = TextAreaField(
        'Bio',
        validators=[
            Optional()
        ]
    )

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        'Current Password',
        validators=[
            DataRequired(message='Current password is required.')
        ]
    )

    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='New password is required.'),
            Length(min=8, message='Password must be at least 8 characters long.'),
            Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d).+$',
                message='Password must include at least one letter and one number.'
            )
        ]
    )
    
class ChangeNicknameForm(FlaskForm):
    nickname = StringField(
        'New Nickname',
        validators=[
            DataRequired(message='Nickname is required.'),
            Length(max=80, message='Nickname must be 80 characters or fewer.')
        ]
    )

class ChangeEmailForm(FlaskForm):
    email = StringField(
        'New Email',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Please enter a valid email address.'),
            Length(max=150)
        ]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required.')]
    )


class DeleteAccountForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required.')]
    )
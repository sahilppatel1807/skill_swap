import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional

STUDENT_EMAIL_MESSAGE = (
    'Please use your Australian student email address (must end with .edu.au).'
)
# WTForms Regexp uses re.match (start of string), so the pattern must span the full email.
STUDENT_EMAIL_REGEX = r'^[^@]+@[^@]+\.edu\.au$'


class LoginForm(FlaskForm):
    identifier = StringField(
        'Email or Nickname',
        validators=[
            DataRequired(message='Email or nickname is required.'),
            Length(max=150, message='Input is too long.')
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(max=128, message='Password is too long.')
        ]
    )


class SignupForm(FlaskForm):
    name = StringField('Name', validators=[
    DataRequired(),
    Length(max=100, message='Name must be 100 characters or fewer.')
])

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
            Regexp(STUDENT_EMAIL_REGEX, flags=re.IGNORECASE, message=STUDENT_EMAIL_MESSAGE),
            Length(max=150,message='Email must be 150 characters or fewer.')
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
        Length(min=8, message='Confirm password must be at least 8 characters long.'),
        Regexp(
            r'^(?=.*[A-Za-z])(?=.*\d).+$',
            message='Confirm password must include at least one letter and one number.'
        ),
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

class ChangeNameForm(FlaskForm):
    name = StringField(
        'New Full Name',
        validators=[
            DataRequired(message='Full name is required.'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters.'),
            Regexp(r'^[A-Za-z\s\-]+$',
                   message='Name can only contain letters, spaces and hyphens.')
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
            Regexp(STUDENT_EMAIL_REGEX, flags=re.IGNORECASE, message=STUDENT_EMAIL_MESSAGE),
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
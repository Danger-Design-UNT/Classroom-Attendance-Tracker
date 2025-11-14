from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class SignupForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=100),
            Regexp(r'^[A-Za-z0-9@._+-]+$', message="Invalid characters in email.")
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=128),
            Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,128}$',
                message="Password must include letters, numbers, and symbols."
            )
        ]
    )
    confirm_password = PasswordField(
    "Confirm Password",
    validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match.")
        ]
    )

    role = SelectField(
        "Role",
        choices=[("student", "Student"), ("teacher", "Teacher")],
        validators=[DataRequired()]
    )

    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Invalid email format."),
            Length(max=100),
            Regexp(r'^[A-Za-z0-9@._+-]+$', message="Invalid characters in email.")
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, max=128, message="Password must be 8-128 characters."),
            Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,128}$',
                message="Password must include letters, numbers, and symbols."
            )
        ]
    )

    submit = SubmitField("Login")

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class SignupForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=100)
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
    role = StringField(
        "Role",
        validators=[
            DataRequired(),
            Regexp(r'^(student|teacher)$', message="Role must be 'student' or 'teacher'.")
        ]
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Invalid email format."),
            Length(max=100)
        ]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8, max=128, message="Password must be 8-128 characters."),
            # Optional: enforce at least one number and symbol
            Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,128}$',
                message="Password must include letters, numbers, and symbols."
            )
        ]
    )
    submit = SubmitField("Login")

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError, Optional
from wtforms.fields import DateField
from app.models import User

# Registration Form for new users
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'(?=.*[A-Z])(?=.*[^a-zA-Z0-9])',
               message="Password must contain at least one uppercase letter and one special character")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register')

    # Custom validator to ensure the username is unique
    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('This username is already taken. Please choose a different one.')

    # Custom validator to ensure the email is unique
    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('This email is already registered. Please use a different one.')

# Login Form for existing users
class LoginForm(FlaskForm):
    email_or_username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Form for submitting comments
class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Submit Comment')

# Form for editing 'About Me' information
class AboutMeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    hometown = StringField('Hometown')
    submit = SubmitField('Save')

# Form for adding work experience
class WorkExperienceForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d',validators=[DataRequired()])
    submit = SubmitField('Save Work Experience')


# Form for adding education experience
class EducationExperienceForm(FlaskForm):
    school_name = StringField('School Name', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d',validators=[DataRequired()])
    learn_details = StringField('Learning Details')
    submit = SubmitField('Save Education Experience')

# Form for adding skills
class SkillForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('Computer Skills', 'Computer Skills'),
        ('Snowboarding Skills', 'Snowboarding Skills')
    ])
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Skill')

# Form for adding detailed work experience
class WorkDetailForm(FlaskForm):
    responsibility = StringField('Responsibility', validators=[DataRequired()])
    achievement = StringField('Achievement', validators=[Optional()])
    submit = SubmitField('Save Work Detail')
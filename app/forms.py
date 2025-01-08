from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError, Optional
from app.models import User

# 用户注册表单
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

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('This username is already taken. Please choose a different one.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('This email is already registered. Please use a different one.')

# 用户登录表单
class LoginForm(FlaskForm):
    email_or_username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# 关于我表单
class AboutMeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    hometown = StringField('Hometown')
    submit = SubmitField('Save')

# 评论表单
class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Submit Comment')

# 工作经历表单
class WorkExperienceForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    start_date = StringField('Start Date (yyyy/mm/dd)')
    end_date = StringField('End Date (yyyy/mm/dd)')
    submit = SubmitField('Save Work Experience')

# 详细工作经历表单
class WorkDetailForm(FlaskForm):
    responsibility = StringField('Responsibility', validators=[DataRequired()])
    achievement = StringField('Achievement', validators=[Optional()])
    submit = SubmitField('Save Work Detail')

# 教育经历表单
class EducationExperienceForm(FlaskForm):
    school_name = StringField('School Name', validators=[DataRequired()])
    start_date = StringField('Start Date (yyyy/mm/dd)', validators=[DataRequired()])
    end_date = StringField('End Date (yyyy/mm/dd)', validators=[DataRequired()])
    learn_details = StringField('Learning Details')
    submit = SubmitField('Save Education Experience')

# 技能表单
class SkillForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('Computer Skills', 'Computer Skills'),
        ('Snowboarding Skills', 'Snowboarding Skills')
    ])
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Skill')

# 个人信息表单
class ManagementForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    hometown = StringField('Hometown')
    submit = SubmitField('Save About Me')

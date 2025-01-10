from app import db
from flask_login import UserMixin
from app import login_manager, bcrypt
from datetime import date
from sqlalchemy import Date

# User Model - Represents users in the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Hash the user's password
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Check if the provided password matches the stored hash
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# Flask-Login loader function to retrieve a user by ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Function to create an admin account if it doesn't already exist
def create_admin():
    from app import db, bcrypt
    if not User.query.filter_by(username="heronsun").first():
        hashed_password = bcrypt.generate_password_hash("Pa55word01").decode('utf-8')
        admin = User(username="heronsun", email="SunH27@cardiff.ac.uk", password_hash=hashed_password, is_admin=True)
        db.session.add(admin)
        db.session.commit()

# Comment Model - Represents user comments on pages
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='comments', lazy=True)
    page = db.Column(db.String(50))  # 'about' or 'skills'
    is_deleted = db.Column(db.Boolean, default=False)

    # Check if a user has permission to delete a comment
    def can_delete(self, user):
        return user.is_admin or self.user_id == user.id

    # Soft delete method for comments
    def soft_delete(self):
        self.is_deleted = True

# About Me Model - Represents the user's basic information
class AboutMe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hometown = db.Column(db.String(100))

# Work Detail Model - Represents details for a specific work experience
class WorkDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_experience_id = db.Column(db.Integer, db.ForeignKey('work_experience.id'), nullable=False)
    responsibility = db.Column(db.String(200), nullable=False)
    achievement = db.Column(db.Text, nullable=True)  # Optional achievement

# Education Experience Model - Represents the user's educational background
class EducationExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    learn_details = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Work Experience Model - Represents the user's work history
class WorkExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Skill Model - Represents the user's skills and expertise
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

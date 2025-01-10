import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()  # Database instance
bcrypt = Bcrypt()  # Password hashing utility
login_manager = LoginManager()  # User session management
csrf = CSRFProtect()  # CSRF protection for forms

# Configure login settings
login_manager.login_view = 'main.login'  # Redirect unauthorized users to login page
login_manager.login_message_category = 'info'  # Category for login flash messages

# Flask application factory function
def create_app():
    app = Flask(__name__)

    # Configure app from environment variables
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app import routes
    app.register_blueprint(routes.bp)  # Main routes blueprint

    # Create database tables and seed an admin user
    with app.app_context():
        db.create_all()
        from app.models import create_admin
        create_admin()

    return app

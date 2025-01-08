import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 Flask 扩展
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

# 设置未登录跳转页面
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

# 创建 Flask 应用工厂函数
def create_app():
    app = Flask(__name__)

    # 使用环境变量进行配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化扩展库
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # 注册蓝图
    from app import routes
    app.register_blueprint(routes.bp)

    # 数据库创建及管理员账户创建
    with app.app_context():
        db.create_all()
        from app.models import create_admin
        create_admin()

    return app

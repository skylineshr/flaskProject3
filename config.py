import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'  # 推荐使用环境变量以提高安全性
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'  # 支持环境变量配置数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭SQLAlchemy的事件跟踪，提升性能

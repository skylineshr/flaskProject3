from app import db
from flask_login import UserMixin
from app import login_manager, bcrypt

# 用户模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# 用户加载器
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 创建管理员账户
def create_admin():
    from app import db, bcrypt
    if not User.query.filter_by(username="heronsun").first():
        hashed_password = bcrypt.generate_password_hash("Pa55word01").decode('utf-8')
        admin = User(username="heronsun", email="SunH27@cardiff.ac.uk", password_hash=hashed_password, is_admin=True)
        db.session.add(admin)
        db.session.commit()

# 评论模型
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='comments', lazy=True)
    page = db.Column(db.String(50))  # 'about' 或 'skills'
    is_deleted = db.Column(db.Boolean, default=False)

    # 封装权限检查方法
    def can_delete(self, user):
        """检查用户是否有权限删除此评论"""
        return user.is_admin or self.user_id == user.id

    def soft_delete(self):
        """执行逻辑删除"""
        self.is_deleted = True

# 关于我模型
class AboutMe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hometown = db.Column(db.String(100))

# 工作详细信息模型
class WorkDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_experience_id = db.Column(db.Integer, db.ForeignKey('work_experience.id'), nullable=False)
    responsibility = db.Column(db.String(200), nullable=False)
    achievement = db.Column(db.Text, nullable=True)  # 可选

# 教育经历模型
class EducationExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(10), nullable=False)
    end_date = db.Column(db.String(10), nullable=True)
    learn_details = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# 工作经历模型
class WorkExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(10), nullable=False)
    end_date = db.Column(db.String(10), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# 技能模型
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

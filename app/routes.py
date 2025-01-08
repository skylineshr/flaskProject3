from flask import (
    Blueprint, render_template, flash, redirect,
    url_for, request, jsonify
)
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from app.forms import (
    RegistrationForm, AboutMeForm, LoginForm, SkillForm,
    CommentForm, ManagementForm, WorkExperienceForm, EducationExperienceForm
)
from app.models import (
    AboutMe, Comment, Skill, User,
    WorkExperience, EducationExperience
)
from flask_paginate import Pagination, get_page_args

bp = Blueprint('main', __name__)

# 首页
@bp.route("/")
def home():
    return "Welcome to my personal digital portfolio!"

# 用户注册
@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

# 用户登录
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.about'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.email == form.email_or_username.data) |
            (User.username == form.email_or_username.data)
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.about'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)

# 用户登出
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

# 关于我页面
@bp.route("/about", methods=["GET", "POST"])
@login_required
def about():
    about_me = AboutMe.query.first()
    work_experiences = WorkExperience.query.all()
    education_experiences = EducationExperience.query.all()
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        comment = Comment(content=comment_form.content.data, user_id=current_user.id, page="about")
        db.session.add(comment)
        db.session.commit()
        flash('Comment submitted successfully!', 'success')
        return redirect(url_for('main.about'))

    page_num, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page", per_page=5)
    comments_query = Comment.query.filter_by(page="about", is_deleted=False).order_by(Comment.date_posted.desc())
    total = comments_query.count()
    comments = comments_query.offset(offset).limit(per_page).all()
    pagination = Pagination(page=page_num, per_page=5, total=total, css_framework="bootstrap4", format="~{page}", format_number=True)

    return render_template('about.html', about_me=about_me, work_experiences=work_experiences,
                           education_experiences=education_experiences, comment_form=comment_form,
                           comments=comments, pagination=pagination)

# 删除记录
@bp.route('/delete/<model_name>/<int:item_id>', methods=['POST'])
@login_required
def delete_record(model_name, item_id):
    from flask_wtf.csrf import validate_csrf, CSRFError

    csrf_token = request.form.get('csrf_token')
    try:
        validate_csrf(csrf_token)
    except CSRFError:
        flash('CSRF Token is invalid or missing!', 'danger')
        return redirect(url_for('main.management_page'))

    if not current_user.is_admin:
        flash('You do not have permission to perform this action!', 'danger')
        return redirect(url_for('main.home'))

    model_mapping = {
        'skill': Skill,
        'work': WorkExperience,
        'education': EducationExperience
    }

    model = model_mapping.get(model_name)
    if model:
        item = model.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        flash('Record deleted successfully!', 'success')
    else:
        flash('Invalid record type.', 'danger')

    return redirect(url_for('main.management_page'))

# 技能页面路由 (移除了 HTML 提交逻辑，只使用 AJAX)
@bp.route("/skills", methods=["GET"])
@login_required
def skills():
    form = SkillForm()
    comment_form = CommentForm()
    skill_form = SkillForm()

    skills_computer = Skill.query.filter_by(category="Computer Skills").all()
    skills_skiing = Skill.query.filter_by(category="Snowboarding Skills").all()

    # 分页逻辑
    page_num, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page", per_page=5)
    comments_query = Comment.query.filter_by(page="skills", is_deleted=False).order_by(Comment.date_posted.desc())
    total = comments_query.count()
    comments_paginated = comments_query.offset(offset).limit(per_page).all()
    pagination = Pagination(page=page_num, per_page=5, total=total, css_framework="bootstrap4")

    return render_template(
        'skills.html',
        form=form,
        skill_form=skill_form,
        comment_form=comment_form,
        skills_computer=skills_computer,
        skills_skiing=skills_skiing,
        comments=comments_paginated,
        pagination=pagination
    )

# 管理页面路由
@bp.route('/management_page', methods=['GET', 'POST'])
@login_required
def management_page():
    if not current_user.is_admin:
        flash('您没有权限访问此页面！', 'danger')
        return redirect(url_for('main.home'))

    # 获取数据
    about_me = AboutMe.query.first()
    work_experiences = WorkExperience.query.all()
    education_experiences = EducationExperience.query.all()
    skills = Skill.query.all()

    # 表单实例化
    about_me_form = ManagementForm(obj=about_me)
    work_experience_form = WorkExperienceForm()
    education_experience_form = EducationExperienceForm()
    skill_form = SkillForm()

    # 处理表单提交
    form_submit = request.form.get('form_submit')

    if form_submit == "submit_about_me" and about_me_form.validate_on_submit():
        if about_me:
            about_me.name = about_me_form.name.data
            about_me.hometown = about_me_form.hometown.data
        else:
            new_about_me = AboutMe(name=about_me_form.name.data, hometown=about_me_form.hometown.data)
            db.session.add(new_about_me)
        db.session.commit()
        flash('关于我信息已保存！', 'success')
        return redirect(url_for('main.management_page'))

    elif form_submit == "submit_work_experience" and work_experience_form.validate_on_submit():
        work_experience = WorkExperience(
            company_name=work_experience_form.company_name.data,
            start_date=work_experience_form.start_date.data,
            end_date=work_experience_form.end_date.data,
            user_id=current_user.id
        )
        db.session.add(work_experience)
        db.session.commit()
        flash('工作经历已成功保存！', 'success')
        return redirect(url_for('main.management_page'))

    elif form_submit == "submit_education_experience" and education_experience_form.validate_on_submit():
        education_experience = EducationExperience(
            school_name=education_experience_form.school_name.data,
            start_date=education_experience_form.start_date.data,
            end_date=education_experience_form.end_date.data,
            learn_details=education_experience_form.learn_details.data,
            user_id=current_user.id
        )
        db.session.add(education_experience)
        db.session.commit()
        flash('教育经历已成功保存！', 'success')
        return redirect(url_for('main.management_page'))

    elif form_submit == "submit_skill" and skill_form.validate_on_submit():
        skill = Skill(
            category=skill_form.category.data,
            title=skill_form.title.data,
            description=skill_form.description.data,
            user_id=current_user.id
        )
        db.session.add(skill)
        db.session.commit()
        flash('技能已成功保存！', 'success')
        return redirect(url_for('main.management_page'))

    return render_template(
        'management_page.html',
        about_me_form=about_me_form,
        work_experience_form=work_experience_form,
        education_experience_form=education_experience_form,
        skill_form=skill_form,
        work_experiences=work_experiences,
        education_experiences=education_experiences,
        skills=skills
    )

# 评论删除
@bp.route("/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.can_delete(current_user):
        comment.soft_delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Comment deleted successfully!'})
    else:
        return jsonify({'success': False, 'message': 'You are not authorized to delete this comment.'}), 403



@bp.route('/api/submit_comment', methods=['POST'])
@login_required
def submit_comment():
    from flask import request, jsonify

    data = request.get_json()
    content = data.get('content')
    page = data.get('page')

    if not content or not page:
        return jsonify({'success': False, 'message': 'Content or page is missing!'}), 400

    # 保存评论
    comment = Comment(content=content, user_id=current_user.id, page=page)
    db.session.add(comment)
    db.session.commit()

    # ✅ 返回 JSON 格式的消息
    return jsonify({
        'success': True,
        'message': 'Comment submitted successfully!',
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'user': current_user.username,
            'date_posted': comment.date_posted.strftime('%Y-%m-%d %H:%M')
        }
    })



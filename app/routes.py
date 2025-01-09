from flask import (
    Blueprint, render_template, flash, redirect,
    url_for, request, jsonify
)
from flask_login import login_user, logout_user, current_user, login_required
from app import bcrypt
from app.forms import (
    RegistrationForm, AboutMeForm, LoginForm, SkillForm,
    CommentForm, ManagementForm, WorkExperienceForm, EducationExperienceForm
)
from flask_paginate import get_page_args
from app.dao import (
    UserDAO, CommentDAO, SkillDAO, AboutMeDAO, WorkExperienceDAO,
    EducationExperienceDAO
)


bp = Blueprint('main', __name__)


# route
@bp.route("/")
def home():
    return "Welcome to my personal digital portfolio!"

# user register
@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        UserDAO.create_user(form.username.data, form.email.data, hashed_password)
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


# user login
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.about'))

    form = LoginForm()
    if form.validate_on_submit():
        user = UserDAO.get_user_by_username_or_email(form.email_or_username.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.about'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)


# user logout
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# About me page
@bp.route("/about", methods=["GET", "POST"])
@login_required
def about():
    about_me = AboutMeDAO.get_about_me()
    work_experiences = WorkExperienceDAO.get_all_work_experiences()
    education_experiences = EducationExperienceDAO.get_all_education_experiences()
    education_experience_form = EducationExperienceForm()
    work_experience_form = WorkExperienceForm()

    return render_template('about.html',
                           about_me=about_me,
                           work_experiences=work_experiences,
                           education_experiences=education_experiences,
                           education_experience_form=education_experience_form,  # ✅ 传递到模板
                           work_experience_form=work_experience_form)


# get comments route
@bp.route("/comments/<page_name>", methods=["GET"])
@login_required
def get_comments(page_name):
    page_num, per_page, _ = get_page_args(page_parameter="page", per_page_parameter="per_page", per_page=5)
    comments, pagination = CommentDAO.get_comments(page_num, per_page, filter_by_page=page_name)
    return render_template("comments.html", comments=comments, pagination=pagination)


# management comments route(delete and add)
@bp.route("/api/comments/<page_name>", methods=["POST"])
@login_required
def manage_comments(page_name):
    data = request.get_json()
    if "content" in data:
        CommentDAO.add_comment(data['content'], current_user.id, page_name)
        return jsonify({'success': True, 'message': 'Comment added successfully!'})
    elif "comment_id" in data:
        if CommentDAO.delete_comment_by_id(data['comment_id'], current_user):
            return jsonify({'success': True, 'message': 'Comment deleted successfully!'})
    return jsonify({'success': False, 'message': 'Invalid operation!'}), 400


# delete info(skills, experience)
@bp.route('/delete/<model_name>/<int:item_id>', methods=['POST'])
@login_required
def delete_record(model_name, item_id):
    from flask_wtf.csrf import validate_csrf, CSRFError

    csrf_token = request.form.get('csrf_token')
    try:
        validate_csrf(csrf_token)
    except CSRFError:
        return jsonify({'success': False, 'message': 'CSRF Token is invalid or missing!'}), 400

    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action!'}), 403

    model_mapping = {
        'skill': SkillDAO,
        'work': WorkExperienceDAO,
        'education': EducationExperienceDAO
    }

    dao = model_mapping.get(model_name)
    if dao and dao.delete_by_id(item_id):
        return jsonify({'success': True, 'message': 'Record deleted successfully!'}), 200
    return jsonify({'success': False, 'message': 'Invalid record type or record not found.'}), 400


# skills page routes
@bp.route("/skills", methods=["GET"])
@login_required
def skills():
    skill_form = SkillForm()

    skills_computer = SkillDAO.get_skills_by_category("Computer Skills")
    skills_skiing = SkillDAO.get_skills_by_category("Snowboarding Skills")

    return render_template(
        'skills.html',
        skill_form=skill_form,
        skills_computer=skills_computer,
        skills_skiing=skills_skiing
    )


# management page route
@bp.route('/management_page', methods=['GET', 'POST'])
@login_required
def management_page():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))

    about_me_form = ManagementForm()
    work_experience_form = WorkExperienceForm()
    education_experience_form = EducationExperienceForm()
    skill_form = SkillForm()

    form_submit = request.form.get('form_submit')

    if form_submit == "submit_about_me" and about_me_form.validate_on_submit():
        AboutMeDAO.add_about_me(
            about_me_form.name.data,
            about_me_form.hometown.data
        )
        return redirect(url_for('main.management_page'))

    elif form_submit == "submit_work_experience" and work_experience_form.validate_on_submit():
        WorkExperienceDAO.add_work_experience(
            work_experience_form.company_name.data,
            work_experience_form.start_date.data,
            work_experience_form.end_date.data,
            current_user.id
        )
        return redirect(url_for('main.management_page'))

    elif form_submit == "submit_education_experience" and education_experience_form.validate_on_submit():
        EducationExperienceDAO.add_education_experience(
            education_experience_form.school_name.data,
            education_experience_form.start_date.data,
            education_experience_form.end_date.data,
            education_experience_form.learn_details.data,
            current_user.id
        )
        return redirect(url_for('main.management_page'))

    elif form_submit == "submit_skill" and skill_form.validate_on_submit():
        SkillDAO.add_skill(
            skill_form.title.data,
            skill_form.description.data,
            skill_form.category.data,
            current_user.id
        )
        return redirect(url_for('main.management_page'))

    return render_template(
        'management_page.html',
        about_me_form=about_me_form,
        work_experience_form=work_experience_form,
        education_experience_form=education_experience_form,
        skill_form=skill_form
    )

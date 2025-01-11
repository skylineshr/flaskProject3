from flask import (
    Blueprint, render_template, flash, redirect,
    url_for, request, jsonify
)
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import (
    RegistrationForm, AboutMeForm, LoginForm, SkillForm,
    WorkExperienceForm, EducationExperienceForm, WorkProjectForm
)
from app.dao import (
    UserDAO, CommentDAO, SkillDAO, AboutMeDAO, WorkExperienceDAO,
    EducationExperienceDAO, WorkProjectDAO
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
        UserDAO.create_user(form.username.data, form.email.data, form.password.data)
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
                           education_experience_form=education_experience_form,
                           work_experience_form=work_experience_form)


# get comments route
@bp.route("/api/comments/<page_name>", methods=["GET"])
@login_required
def get_comments(page_name):
    page_num = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    comments, pagination = CommentDAO.get_comments(page_num, per_page, filter_by_page=page_name)

    comments_list = [
        {
            'id': comment.id,
            'content': comment.content,
            'username': comment.user.username,
            'user_id': comment.user.id,
            'is_admin': current_user.is_admin,
            'current_user_id': current_user.id,
            'created_at': comment.date_posted.strftime("%Y-%m-%d %H:%M:%S")
        } for comment in comments
    ]

    return jsonify({
        'comments': comments_list,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'current_user_id': current_user.id
    })


# management comments route(delete and add)
@bp.route("/api/comments/<page_name>", methods=["POST"])
@login_required
def manage_comments(page_name):
    data = request.get_json()
    if "content" in data and data["content"].strip():
        CommentDAO.add_comment(data['content'], current_user.id, page_name)
        return jsonify({'success': True, 'message': 'Comment added successfully!'})
    elif "comment_id" in data:
        if CommentDAO.delete_comment_by_id(data['comment_id'], current_user):
            return jsonify({'success': True, 'message': 'Comment deleted successfully!'})
    return jsonify({'success': False, 'message': 'Invalid operation!'}), 400


# delete info (skills, experience, projects)
@bp.route('/delete/<model_name>/<int:item_id>', methods=['POST'])
@login_required
def delete_record(model_name, item_id):
    from flask_wtf.csrf import validate_csrf, CSRFError

    csrf_token = request.form.get('csrf_token')
    try:
        validate_csrf(csrf_token)
    except CSRFError:
        flash("CSRF Token is invalid or missing!", "danger")
        return redirect(request.referrer or url_for('main.management_page'))

    if not current_user.is_admin:
        flash("You do not have permission to perform this action!", "danger")
        return redirect(request.referrer or url_for('main.management_page'))

    # 删除逻辑映射表
    model_mapping = {
        'skill': SkillDAO.delete_skill_by_id,
        'work': WorkExperienceDAO.delete_work_experience_by_id,
        'education': EducationExperienceDAO.delete_education_experience_by_id,
        'project': WorkProjectDAO.delete_project
    }

    # 如果是删除公司，需要检查其下是否还有项目
    if model_name == 'work':
        projects = WorkProjectDAO.get_projects_by_work_experience(item_id)
        if projects:
            flash("Cannot delete this company as there are existing projects.", "danger")
            return redirect(request.referrer or url_for('main.management_page'))

    # 执行删除操作
    delete_method = model_mapping.get(model_name)
    if delete_method and delete_method(item_id):
        flash(f'{model_name.capitalize()} deleted successfully!', 'success')
    else:
        flash('Invalid record type or record not found.', 'danger')

    return redirect(request.referrer or url_for('main.management_page'))



# skills page routes
@bp.route("/skills", methods=["GET"])
@login_required
def skills():
    skill_form = SkillForm()

    skills_computer = SkillDAO.get_skills_by_category("Computer Skills")
    skills_skiing = SkillDAO.get_skills_by_category("Snowboarding Skills")

    print("Computer Skills: ", skills_computer)
    print("Snowboarding Skills: ", skills_skiing)

    return render_template(
        'skills.html',
        skill_form=skill_form,
        skills_computer=skills_computer,
        skills_skiing=skills_skiing
    )


# management page route
@bp.route('/management_page', methods=['GET'])
@login_required
def management_page():
    if not current_user.is_admin:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.index'))

    about_me_form = AboutMeForm()
    work_experience_form = WorkExperienceForm()
    education_experience_form = EducationExperienceForm()
    skill_form = SkillForm()
    work_project_form = WorkProjectForm()

    work_experiences = WorkExperienceDAO.get_all_work_experiences()
    work_project_form.work_experience_id.choices = [(work.id, work.company_name) for work in work_experiences]

    return render_template('management_page.html',
                           about_me_form=about_me_form,
                           work_experience_form=work_experience_form,
                           education_experience_form=education_experience_form,
                           skill_form=skill_form,
                           work_project_form=work_project_form)


@bp.route('/submit_form', methods=['POST'])
@login_required
def submit_form():
    form_submit = request.form.get('form_submit')

    if not form_submit:
        flash("Error: No form submit value received!", "danger")
        return redirect(url_for('main.management_page'))

    if form_submit == "submit_about_me":
        about_me_form = AboutMeForm(request.form)
        if about_me_form.validate_on_submit():
            AboutMeDAO.add_about_me(
                about_me_form.name.data,
                about_me_form.hometown.data,
                about_me_form.email.data
            )
            flash("About Me updated successfully!", "success")
        else:
            flash("Error submitting the About Me form.", "danger")

    elif form_submit == "submit_work_experience":
        work_experience_form = WorkExperienceForm(request.form)
        if work_experience_form.validate_on_submit():
            WorkExperienceDAO.add_work_experience(
                company_name=work_experience_form.company_name.data,
                start_date=work_experience_form.start_date.data,
                end_date=work_experience_form.end_date.data if work_experience_form.end_date.data else None,
                user_id=current_user.id
            )
            flash("Work Experience updated successfully!", "success")
        else:
            flash("Error submitting the Work Experience form.", "danger")

    elif form_submit == "submit_education_experience":
        education_experience_form = EducationExperienceForm(request.form)
        if education_experience_form.validate_on_submit():
            EducationExperienceDAO.add_education_experience(
                school_name=education_experience_form.school_name.data,
                start_date=education_experience_form.start_date.data,
                end_date=education_experience_form.end_date.data,
                learn_details=education_experience_form.learn_details.data,
                user_id=current_user.id
            )
            flash("Education Experience updated successfully!", "success")
        else:
            flash("Error submitting the Education Experience form.", "danger")

    elif form_submit == "submit_skill":
        skill_form = SkillForm(request.form)
        if skill_form.validate_on_submit():
            SkillDAO.add_skill(
                skill_form.title.data,
                skill_form.description.data,
                skill_form.category.data,
                current_user.id
            )
            flash("Skill added successfully!", "success")
        else:
            flash("Error submitting the Skill form.", "danger")

    return redirect(url_for('main.management_page'))


# add project routes
@bp.route('/add_project', methods=['POST'])
@login_required
def add_project():
    if not current_user.is_admin:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.index'))

    work_project_form = WorkProjectForm()
    work_experiences = WorkExperienceDAO.get_all_work_experiences()
    work_project_form.work_experience_id.choices = [(work.id, work.company_name) for work in work_experiences]

    if work_project_form.validate_on_submit():
        work_experience_id = work_project_form.work_experience_id.data
        project_name = work_project_form.project_name.data
        achievement = work_project_form.achievement.data

        # 校验公司是否存在
        if not any(work.id == work_experience_id for work in work_experiences):
            flash("Invalid company selected.", "danger")
            return redirect(url_for('main.management_page'))

        # 使用 DAO 层添加项目
        WorkProjectDAO.add_project(
            work_experience_id=work_experience_id,
            project_name=project_name,
            achievement=achievement
        )
        flash("Project added successfully!", "success")
        return redirect(url_for('main.management_page'))

    flash("Failed to add project. Please check the form.", "danger")
    return redirect(url_for('main.management_page'))

#delete project
@bp.route("/delete_project/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    if current_user.is_admin:
        WorkProjectDAO.delete_project(project_id)
    return redirect(url_for('main.about'))
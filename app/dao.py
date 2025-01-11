from app import db
from flask_paginate import Pagination, get_page_args
from datetime import datetime, date
from app.models import Comment, Skill, User, AboutMe, EducationExperience, WorkExperience, WorkProject



# control User db
class UserDAO:
    @staticmethod
    def create_user(username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_username_or_email(identifier):
        return User.query.filter((User.email == identifier) | (User.username == identifier)).first()


# control Comments db
class CommentDAO:
    @staticmethod
    def add_comment(content, user_id, page_name):
        comment = Comment(content=content, user_id=user_id, page=page_name)
        db.session.add(comment)
        db.session.commit()

    @staticmethod
    def get_comments(page_num, per_page, filter_by_page):
        query = Comment.query.filter_by(page=filter_by_page, is_deleted=False).order_by(Comment.date_posted.desc())
        pagination = query.paginate(page=page_num, per_page=per_page, error_out=False)
        return pagination.items, pagination

    @staticmethod
    def delete_comment_by_id(comment_id, user):
        comment = Comment.query.get(comment_id)
        if comment and comment.can_delete(user):
            comment.soft_delete()
            db.session.commit()
            return True
        return None

    @staticmethod
    def get_paginated_comments(page_num, per_page, filter_by_page):
        comments_query = Comment.query.filter_by(page=filter_by_page, is_deleted=False).order_by(
            Comment.date_posted.desc())
        total = comments_query.count()
        comments = comments_query.offset((page_num - 1) * per_page).limit(per_page).all()
        pagination = Pagination(page=page_num, per_page=per_page, total=total, css_framework="bootstrap4")
        return comments, pagination


# control about_me db
class AboutMeDAO:
    @staticmethod
    def get_about_me():
        return AboutMe.query.first()

    @staticmethod
    def add_about_me(name, hometown, email):
        about_me = AboutMe.query.first()  # 检查是否已有记录
        if about_me:
            about_me.name = name
            about_me.hometown = hometown
            about_me.email = email
        else:
            about_me = AboutMe(name=name, hometown=hometown, email=email)
            db.session.add(about_me)
        db.session.commit()
        return about_me


# control skills db
class SkillDAO:
    @staticmethod
    def get_skills_by_category(category):
        return Skill.query.filter_by(category=category).all()

    @staticmethod
    def add_skill(title, description, category, user_id):
        skill = Skill(title=title, description=description, category=category, user_id=user_id)
        db.session.add(skill)
        db.session.commit()
        return skill

    @staticmethod
    def delete_skill_by_id(skill_id):
        skill = Skill.query.get(skill_id)
        if skill:
            db.session.delete(skill)
            db.session.commit()
            return True
        return False


# control WorkExperience db
class WorkExperienceDAO:
    @staticmethod
    def get_all_work_experiences():
        """获取所有工作经历记录"""
        return WorkExperience.query.all()

    @staticmethod
    def add_work_experience(company_name, start_date, user_id, end_date=None):
        """添加工作经历记录"""
        if not isinstance(start_date, date):
            raise ValueError("start_date must be a date object.")
        if end_date and not isinstance(end_date, date):
            raise ValueError("end_date must be a date object.")

        work_experience = WorkExperience(
            company_name=company_name,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )
        db.session.add(work_experience)
        db.session.commit()
        return work_experience

    @staticmethod
    def delete_work_experience_by_id(work_experience_id):
        """
        删除工作经历记录，仅当该公司下无项目时可删除
        """
        projects = WorkProjectDAO.get_projects_by_work_experience(work_experience_id)
        if projects:
            # 如果存在项目，禁止删除公司
            return False

        work_experience = WorkExperience.query.get(work_experience_id)
        if work_experience:
            db.session.delete(work_experience)
            db.session.commit()
            return True
        return False


# control education_experience db
class EducationExperienceDAO:
    @staticmethod
    def get_all_education_experiences():
        return EducationExperience.query.all()

    @staticmethod
    def add_education_experience(school_name, start_date, user_id, end_date=None, learn_details=None):
        # 确保 start_date 和 end_date 是 date 类型
        if not isinstance(start_date, date):
            raise ValueError("start_date must be a date object.")

        if end_date and not isinstance(end_date, date):
            raise ValueError("end_date must be a date object.")

        education_experience = EducationExperience(
            school_name=school_name,
            start_date=start_date,
            end_date=end_date,
            learn_details=learn_details,
            user_id=user_id
        )
        db.session.add(education_experience)
        db.session.commit()
        return education_experience

    @staticmethod
    def delete_education_experience_by_id(education_experience_id):
        education_experience = EducationExperience.query.get(education_experience_id)
        if education_experience:
            db.session.delete(education_experience)
            db.session.commit()
            return True
        return False


# control WorkProject db
class WorkProjectDAO:
    @staticmethod
    def get_projects_by_work_experience(work_experience_id):
        """根据公司ID获取所有关联项目"""
        return WorkProject.query.filter_by(work_experience_id=work_experience_id).all()

    @staticmethod
    def add_project(work_experience_id, project_name, achievement):
        """添加新项目"""
        # 确保公司存在
        if not WorkExperience.query.get(work_experience_id):
            raise ValueError("Work experience not found.")

        project = WorkProject(
            work_experience_id=work_experience_id,
            project_name=project_name,
            achievement=achievement
        )
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def delete_project(project_id):
        project = WorkProject.query.get(project_id)
        if project:
            db.session.delete(project)
            db.session.commit()
            return True
        return False
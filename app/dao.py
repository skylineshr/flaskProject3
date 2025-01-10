from app import db
from flask_paginate import Pagination, get_page_args
from datetime import datetime, date
from app.models import Comment, Skill, User, AboutMe, EducationExperience, WorkExperience



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
    def add_about_me(name, hometown):
        about_me = AboutMe.query.first()  # 检查是否已有记录
        if about_me:
            about_me.name = name
            about_me.hometown = hometown
        else:
            about_me = AboutMe(name=name, hometown=hometown)
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


# control work_experience db
class WorkExperienceDAO:
    @staticmethod
    def get_all_work_experiences():
        return WorkExperience.query.all()

    @staticmethod
    def add_work_experience(company_name, start_date, user_id, end_date=None):
        # 确保 user_id 是整数
        if not isinstance(user_id, int):
            raise ValueError("user_id must be an integer.")

        # 确保 start_date 和 end_date 是 datetime.date 类型
        if isinstance(start_date, date):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        elif not isinstance(start_date, date):
            raise ValueError("start_date must be a date object or a valid date string.")

        if end_date:
            if isinstance(end_date, date):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            elif not isinstance(end_date, date):
                raise ValueError("end_date must be a date object or a valid date string.")

        # 创建新的工作经历记录
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
        workExperience = WorkExperience.query.get(work_experience_id)
        if workExperience:
            db.session.delete(workExperience)
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
        # 保证 start_date 和 end_date 都是 date 对象
        if not isinstance(user_id, int):
            raise ValueError("user_id must be an integer.")

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        elif not isinstance(start_date, datetime.date):
            raise ValueError("start_date must be a date object or a valid date string.")
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            elif not isinstance(end_date, datetime.date):
                raise ValueError("end_date must be a date object or a valid date string.")

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
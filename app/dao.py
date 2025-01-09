from app import db
from flask_paginate import Pagination, get_page_args
from app.models import Comment, Skill, User, AboutMe, WorkExperience, EducationExperience


# control User db
class UserDAO:
    @staticmethod
    def create_user(username, email, password):
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_username_or_email(identifier):
        return User.query.filter((User.email ==identifier) | (User.User.username == identifier)).first()


# control comment db
class CommentDAO:
    @staticmethod
    def get_comments(page, per_page, filter_by_page):
        query = Comment.query.filter_by(page=filter_by_page, is_deleted=False).order_by(Comment.created_posted.desc())
        total = query.count()
        comments = query.offset((page - 1) * per_page).limit(per_page).all()
        return comments, total

    @staticmethod
    def add_comment(content, user_id, page):
        comment = Comment(content=content, user_id=user_id, page=page)
        db.session.add(comment)
        db.session.commit()
        return comment

    @staticmethod
    def delete_comment_by_id(comment_id, user):
        comment = Comment.query.get(comment_id)
        if comment and comment.can_delete(user):
            comment.delete()
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
    def add_work_experience(title, description, category, user_id):
        workExperience = WorkExperience(title=title, description=description, category=category, user_id=user_id)
        db.session.add(workExperience)
        db.session.commit()
        return workExperience

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
    def add_education_experience(title, description, category, user_id):
        EducationExperience = EducationExperience(title=title, description=description, category=category, user_id=user_id)
        db.session.add(EducationExperience)
        db.session.commit()
        return EducationExperience

    @staticmethod
    def delete_education_experience_by_id(education_experience_id):
        EducationExperience.query.get(education_experience_id)
        if EducationExperience:
            db.session.delete(EducationExperience)
            db.session.commit()
            return True
        return False
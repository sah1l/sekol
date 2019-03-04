from flask_login import UserMixin
from sqlalchemy import Table, Column, String, Integer, Float, DateTime, ForeignKey, Boolean

from app import db, login


# Bind users and categories
users_categories_association_table = db.Table("users_categories_association",
                                        db.Column("category_name",
                                                  db.String(100),
                                                  db.ForeignKey("categories.name", ondelete="CASCADE")),
                                        db.Column("user_name",
                                                  db.String(100),
                                                  db.ForeignKey("users.name", ondelete="CASCADE")))

design_categories_association_table = db.Table("design_categories_association",
                                        db.Column("category_name",
                                                  db.String(100),
                                                  db.ForeignKey("categories.name", ondelete="CASCADE")),
                                        db.Column("design_name",
                                                  db.String(100),
                                                  db.ForeignKey("designs.name", ondelete="CASCADE")))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    name = Column(String(100), primary_key=True)
    type = Column(String(20))
    password = Column(String(20))
    allow_create = Column(Boolean)
    allow_upload = Column(Boolean)
    boss = Column(String(100))
    categories = db.relationship("Category",
                                 secondary=users_categories_association_table,
                                 back_populates="users")

    def __init__(self, name=None, password=None):
        self.name = name
        self.password = password

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def set_password(self, password):
        self.password_hash = password

    def check_password(self, password):
        return self.password==password

    def set_allow_create(self, allow_create):
        self.allow_create = allow_create

    def set_allow_upload(self, allow_upload):
        self.allow_upload = allow_upload

    def set_boss(self, boss):
        self.boss = boss

    def set_type(self, type):
        self.type= type

    def get_id(self):
        return self.name


class Category(db.Model):
    __tablename__ = "categories"

    name = db.Column(db.String(100), unique=True, index=True, primary_key=True)
    data_dir = db.Column(db.String(100))
    creator = db.Column(db.String(100))
    users = db.relationship("User",
                         secondary=users_categories_association_table,
                         back_populates="categories")
    designs = db.relationship("Design",
                         secondary=design_categories_association_table,
                         back_populates="categories")

class Design(db.Model):
    __tablename__ = "designs"

    name = db.Column(db.String(100), unique=True, index=True, primary_key=True)
    location = db.Column(db.String(100))
    creator = db.Column(db.String(100))
    categories = db.relationship("Category",
                         secondary=design_categories_association_table,
                         back_populates="designs")

@login.user_loader
def load_user(id):
    user_id = db.session.query(User).get(id)
    return user_id
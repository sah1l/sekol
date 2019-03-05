from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import current_user
from app import session_commit, session_add, session_delete
from app.mod_admin.forms import CategoryCreateForm, CategoryInfoForm, DesignCreateForm, DesignInfoForm
from app.models import User, Category, Design
from .forms import UserCreateForm, UserInfoForm, PasswordForm
from werkzeug.datastructures import CombinedMultiDict
from config import Config

import os

# define Blueprint for admin module
mod_admin = Blueprint('admin', __name__, url_prefix='/admin_panel')
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

@mod_admin.before_request
def check_authenticated_user():
    """
    Restrict access to admin panel to non-admin users
    """
    if not current_user.is_authenticated:  # user is not authenticated
        return redirect(url_for("home"))
    elif request.endpoint=='admin.add_user' and  not current_user.allow_create:
        return redirect(url_for("home"))
    elif request.endpoint in ['admin.change_userinfo', 'admin.change_password', 'admin.delete_user']:
        uid = request.view_args.get('user_id')
        if uid:
            if not User.query.filter_by(name=uid).first().boss == current_user.name and not uid == current_user.name\
                    and not 'admin' == current_user.type:
                return redirect(url_for("home"))

@mod_admin.route("/", methods=["GET"])
def show_panel():
    if current_user.type=='admin':
        users = User.query.all()
    else:
        users = User.query.filter((User.boss==current_user.name) | (User.name==current_user.name))
    return render_template("admin_panel/list_users.html", users=users)


@mod_admin.route("/add_user", methods=["GET", "POST"])
def add_user():
    form = UserCreateForm()
    # orgs = Organization.query.all()
    # form.organizations.choices = [(org.id, org.name) for org in orgs]

    if form.validate_on_submit():
        user = User(name=form.username.data,
                    password=form.password.data,
                    )
        user.set_type(form.type.data)
        user.set_allow_create(form.allow_create.data)
        user.set_allow_upload(form.allow_upload.data)
        user.set_boss(current_user.name)
        orgs = []

        # for org_id in form.organizations.data:
        #     org = Organization.query.filter_by(id=org_id).first()
        #     orgs.append(org)

        # user.organizations = orgs
        session_add(user)
        session_commit()

        return redirect(url_for("admin.show_panel"))

    return render_template('admin_panel/create_user.html', form=form)


@mod_admin.route("/edit_user/<user_id>", methods=["GET", "POST"])
def change_userinfo(user_id):
    user = User.query.filter_by(name=user_id).first()
    # orgs = Organization.query.all()
    form = UserInfoForm(type = user.type)

    if form.validate_on_submit():
        user.name = form.username.data
        user.allow_create = form.allow_create.data
        user.allow_upload = form.allow_upload.data
        user.type = form.type.data
        orgs = []

        # for org_id in form.organizations.data:
            # org = Organization.query.filter_by(id=org_id).first()
            # orgs.append(org)

        # user.organizations = orgs
        session_commit()

        return redirect(url_for("admin.show_panel"))

    return render_template("admin_panel/change_userinfo.html", form=form, user=user)


@mod_admin.route("/edit_user/<user_id>/password", methods=["GET", "POST"])
def change_password(user_id):
    form = PasswordForm()
    user = User.query.filter_by(name=user_id).first()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        session_commit()

        return redirect(url_for("admin.show_panel"))

    return render_template("admin_panel/change_password.html", form=form, user=user)


@mod_admin.route("/delete_user/<user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    user = User.query.filter_by(name=user_id).first()
    session_delete(user)
    session_commit()

    return redirect(url_for("admin.show_panel"))


@mod_admin.route("/list_categories", methods=["GET"])
def list_categories():
    categories = Category.query.all()

    return render_template("admin_panel/list_categories.html", categories=categories)


@mod_admin.route("/add_category", methods=["GET", "POST"])
def add_category():
    form = CategoryCreateForm()
    if current_user.type == 'admin':
        users = User.query.all()
    else:
        users = User.query.filter((User.boss == current_user.name) | (User.name == current_user.name))
    # empty_choice = [(0, " " * 10)]
    form.users.choices = [(user.name, user.name) for user in users]

    if form.validate_on_submit():
        category = Category(name=form.name.data,
                           data_dir=form.name.data)
        users = []

        for user_id in form.users.data:
            user = User.query.filter_by(name=user_id).first()
            users.append(user)

        category.users = users
        category.creator = current_user.name
        session_add(category)
        session_commit()

        return redirect(url_for("admin.add_category"))

    return render_template("admin_panel/create_category.html", form=form)


@mod_admin.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    form = CategoryInfoForm()
    if current_user.type == 'admin':
        users = User.query.all()
    else:
        users = User.query.filter((User.boss == current_user.name) | (User.name == current_user.name))
    form.users.choices = [(user.name, user.name) for user in users]
    category = Category.query.filter_by(name=category_id).first()
    form.users.data = [u.name for u in category.users]

    if form.validate_on_submit():
        category.name = form.name.data
        category.data_dir = form.name.data
        users = []

        for user_id in form.users.raw_data:
            user = User.query.filter_by(name=user_id).first()
            users.append(user)

        category.users = users
        session_commit()

        return redirect(url_for("admin.list_categories"))

    return render_template("admin_panel/edit_category.html", form=form, category=category)


@mod_admin.route("/delete_category/<category_id>", methods=["GET", "POST"])
def delete_category(category_id):
    category = Category.query.filter_by(name=category_id).first()
    session_delete(category)
    session_commit()

    return redirect(url_for("admin.list_categories"))


@mod_admin.route("/add_design", methods=["GET", "POST"])
def add_design():
    form = DesignCreateForm(CombinedMultiDict((request.files, request.form)))
    categories = Category.query.all()
    # empty_choice = [(0, " " * 10)]
    form.categories.choices = [(category.name, category.name) for category in categories]

    if form.validate_on_submit():
        file = form.file.data
        design = Design(name=form.name.data,
                           location=file.filename)
        categories = []

        for category_id in form.categories.data:
            category = Category.query.filter_by(name=category_id).first()
            categories.append(category)

        design.categories = categories
        design.creator = current_user.name

        if file and allowed_file(file.filename):
            out_path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
            out_dir = os.path.dirname(out_path)
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            file.save(out_path)
        session_add(design)
        session_commit()

        return redirect(url_for("admin.add_design"))

    return render_template("admin_panel/create_design.html", form=form)


@mod_admin.route("/list_designs", methods=["GET"])
def list_designs():
    designs = Design.query.all()

    return render_template("admin_panel/list_designs.html", designs=designs)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@mod_admin.route("/delete_design/<design_id>", methods=["GET", "POST"])
def delete_design(design_id):
    design = Design.query.filter_by(name=design_id).first()
    session_delete(design)
    session_commit()

    return redirect(url_for("admin.list_designs"))

@mod_admin.route("/edit_design/<design_id>", methods=["GET", "POST"])
def edit_design(design_id):
    form = DesignInfoForm()
    categories = Category.query.all()
    form.categories.choices = [(category.name, category.name) for category in categories]
    design = Design.query.filter_by(name=design_id).first()
    form.categories.data = [c.name for c in design.categories]

    if form.validate_on_submit():
        file = form.file.data
        design.name = form.name.data
        categories = []

        for category_id in form.categories.raw_data:
            category = Category.query.filter_by(name=category_id).first()
            categories.append(category)

        if file and allowed_file(file.filename):
            out_path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
            out_dir = os.path.dirname(out_path)
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            file.save(out_path)
            design.location = file.filename
        design.categories = categories
        session_commit()

        return redirect(url_for("admin.list_designs"))

    return render_template("admin_panel/edit_design.html", form=form, design=design)


@mod_admin.route("/category/<category_id>", methods=["GET"])
def get_designs(category_id):
    category = Category.query.filter_by(name=category_id).first()
    designs = category.designs
    return render_template("pages/show_designs.html", designs=designs, category=category_id)
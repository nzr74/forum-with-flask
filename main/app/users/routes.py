from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from app.users.models import User, Code, Follow
from app.users.forms import (
    UserRegistrationForm,
    UserCodeVerifyForm,
    UserLoginForm,
    EmptyForm,
)
from app.extentions import db  # sms_api
import random
import datetime


blueprint = Blueprint("users", __name__)


@blueprint.route("/register", methods=["post", "get"])
def register():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        rand_num = random.randint(10000, 99999)
        session["user_phone"] = form.phone.data
        # send sms
        code = Code(
            number=rand_num,
            expire=datetime.datetime.now() + datetime.timedelta(minutes=3),
            phone=form.phone.data,
        )
        db.session.add(code)
        db.session.commit()
        print(rand_num)
        return redirect(url_for("users.verify"))
    return render_template("users/register.html", form=form)


@blueprint.route("/verify", methods=["post", "get"])
def verify():
    user_phone = session["user_phone"]
    code = Code.query.filter_by(phone=user_phone).first()
    form = UserCodeVerifyForm()
    if form.validate_on_submit():
        if code.expire < datetime.datetime.now():
            flash("Expiration Error,please try again", "danger")
            return redirect(url_for("users.register"))
        if form.code.data != str(code.number):
            flash("your code is wrong", "danger")
            return redirect(url_for("users.verify"))
        user = User.query.filter_by(phone=user_phone).first()
        print(user)
        if user:
            login_user(user)
            flash("you logged in")
            return redirect("/")
        else:
            user = User(phone=user_phone)
            db.session.add(user)
            db.session.commit()
            flash("your account created successfully", "success")
            return redirect("/")
    return render_template("users/verify.html", form=form)


@blueprint.route("/login", methods=["post", "get"])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        rand_num = random.randint(10000, 99999)
        session[form.phone.data] = form.phone.data
        # send sms
        code = Code(
            number=rand_num,
            expire=datetime.datetime.now() + datetime.timedelta(minutes=3),
            phone=form.phone.data,
        )
        db.session.add(code)
        db.session.commit()
        print(rand_num)
        return redirect(url_for("users.verify", phone=form.phone.data))
    return render_template("users/login.html", form=form)


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flash("you logged out")
    return redirect("/")


@blueprint.route("/profile")
@login_required
def profile():
    return render_template("users/profile.html")


@blueprint.route("/user/<int:id>")
def user(id):
    following = False
    user = User.query.get_or_404(id)
    form = EmptyForm()
    relation = Follow.query.filter_by(
        follower=current_user.id, followed=user.id
    ).first()
    if relation:
        following = True
    return render_template("users/user.html", user=user, form=form, following=following)


@blueprint.route("/follow/<int:id>", methods=["post"])
@login_required
def follow(id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=id).first()
        if user is None:
            flash("User not found", "danger")
            return redirect("/")
        if user == current_user:
            flash("you cant follow yourself", "info")
        relation = Follow(follower=current_user.id, followed=user.id)
        db.session.add(relation)
        db.session.commit()
        flash(f"you followed {user.id}", "info")
        return redirect(url_for("users.user", id=user.id))
    return redirect("/")


@blueprint.route("/unfollow/<int:id>", methods=["post"])
@login_required
def unfollow(id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=id).first()
        if user is None:
            flash("User not found", "danger")
            return redirect("/")
        if user == current_user:
            flash("you cant unfollow yourself", "danger")
        relation = Follow.query.filter_by(
            follower=current_user.id, followed=user.id
        ).first()
        db.session.delete(relation)
        db.session.commit()
        flash(f"you unfollowed {user.id}", "info")
        return redirect(url_for("users.user", id=user.id))
    return redirect("/")

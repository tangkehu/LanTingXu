from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, current_user

from . import auth_bp
from .forms import LoginForm, RegisterForm
from app.models import User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))
    form = LoginForm()
    if form.validate_on_submit():
        login_user(User.query.filter_by(email=form.email.data).first(), True)
        return redirect(request.args.get('next') or url_for('main_bp.index'))
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        User.add(form.email.data, form.password.data)
        flash('注册成功，请登录。')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)

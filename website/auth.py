from flask import Blueprint, render_template, request, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return(redirect(url_for('views.home')))
            else:
                pass
        else:
            pass

    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        user = User.query.filter_by(username=username).first()
        if user:
            pass
        elif len(username) < 2:
            pass
        elif password != confirm_password:
            pass
        elif len(password) < 6:
            pass
        else:
            new_user = User(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return(redirect(url_for('views.home')))

    return render_template("sign_up.html")
from flask import Blueprint, render_template

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')


@auth_bp.route('/register')
def register():
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    from flask import redirect, url_for
    return redirect(url_for('main.index'))

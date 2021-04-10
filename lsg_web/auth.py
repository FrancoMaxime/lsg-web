import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash
from werkzeug.exceptions import abort
from lsg_web.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        mail = request.form['mail']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE mail = ?', (mail,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        elif user['actif'] == 0:
            error = 'Account desactivated.'

        if error is None:
            session.clear()
            session['id_user'] = user['id_user']
            session['id_permission'] = user['id_permission']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    id_user = session.get('id_user')

    if id_user is None:
        g.user = None
        g.group = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id_user = ?', (id_user,)
        ).fetchone()
        g.group = get_db().execute(
            "SELECT * FROM permission WHERE id_permission = ?", (g.user['id_permission'],)
        ).fetchone()
        g.person = get_db().execute(
            'SELECT * FROM person WHERE id_person = ?', (g.user['id_person'],)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


def security_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        elif g.user['id_permission'] != 1:
            return abort(403)
        return view(**kwargs)

    return wrapped_view

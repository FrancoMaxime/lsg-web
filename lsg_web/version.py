from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required
from lsg_web.db import get_db

bp = Blueprint('version', __name__, url_prefix='/version')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    versions = db.execute(
        'SELECT * FROM version'
    ).fetchall()
    return render_template('version/list.html', versions=versions)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    check_admin()
    if request.method == 'POST':
        error = check_version(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO version (name, release_date)'
                ' VALUES (?, ?)',
                (request.form['name'], request.form['date'])
            )
            db.commit()
            return redirect(url_for('version.listing'))
    return render_template('version/create.html')


def check_version(request):
    name = request.form['name']
    date = request.form['date']

    if not name:
        return "You must enter a name."
    elif not date:
        return 'You must enter a release date.'
    elif get_db().execute(
                'SELECT * FROM version WHERE name = ?', (name,)
        ).fetchone() is not None:
        return 'This version already exists'


def check_admin():
    if g.user['id_permission'] != 1:
        abort(403)

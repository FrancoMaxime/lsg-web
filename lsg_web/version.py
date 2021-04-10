from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required, security_required
from lsg_web.db import get_db
from datetime import date as dtdate
bp = Blueprint('version', __name__, url_prefix='/version')


@bp.route('/list')
@security_required
def listing():
    db = get_db()
    versions = db.execute(
        'SELECT * FROM version'
    ).fetchall()
    return render_template('version/list.html', versions=versions)


@bp.route('/create', methods=('GET', 'POST'))
@security_required
def create():
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

    if not name or name == "":
        return "You must enter a name."
    elif not date or date == "":
        return 'You must enter a release date.'

    is_valid = True
    try:
        dtdate.fromisoformat(date)
    except ValueError:
        is_valid = False
    if not is_valid:
        return 'You must enter a valid date.'

    elif get_db().execute(
                'SELECT * FROM version WHERE name = ?', (name,)
        ).fetchone() is not None:
        return 'This version already exists.'

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required, security_required
from lsg_web.db import get_db

bp = Blueprint('bug', __name__, url_prefix='/bug')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    bugs = db.execute(
        'SELECT * FROM bug WHERE corrected = 0'
    ).fetchall()
    return render_template('bug/list.html', bugs=bugs)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        error = check_bug(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO bug (title, information, bug_date, corrected)'
                ' VALUES (?, ?, date("now"), 0)',
                (request.form['title'], request.form['information'])
            )
            db.commit()
            return redirect(url_for('bug.listing'))
    return render_template('bug/create.html')


def check_bug(request):
    title = request.form['title']
    information = request.form['information']

    if not title:
        return "You must enter a title."
    elif not information:
        return 'You must enter some information.'
    elif get_db().execute(
                'SELECT * FROM bug WHERE title = ?', (title,)
        ).fetchone() is not None:
        return 'This title already exists.'


@bp.route('/<int:id>/delete', methods=('POST',))
@security_required
def delete(id):
    get_bug(id)
    db = get_db()
    db.execute('UPDATE bug SET corrected = 1 WHERE id_bug = ?', (id,))
    db.commit()
    return redirect(url_for('bug.listing'))


def get_bug(id):
    bug = get_db().execute('SELECT * FROM bug WHERE id_bug = ?', (id,)).fetchone()
    if bug is None:
        abort(404, "Bug id {0} doesn't exist.".format(id))

    return bug


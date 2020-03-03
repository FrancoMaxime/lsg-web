from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required
from lsg_web.db import get_db

bp = Blueprint('category', __name__, url_prefix='/category')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    categories = db.execute(
        'SELECT * FROM category'
    ).fetchall()
    return render_template('category/list.html', categories=categories)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    check_admin()
    if request.method == 'POST':
        error = check_category(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO category (name)'
                ' VALUES (?)',
                (request.form['name'])
            )
            db.commit()
            return redirect(url_for('category.listing'))
    return render_template('category/create.html')


def check_category(request):
    name = request.form['name']

    if not name:
        return "You must enter a name."
    elif get_db().execute(
                'SELECT * FROM category WHERE name = ?', (name,)
        ).fetchone() is not None:
        return 'This category already exists'


def check_admin():
    if g.user['id_permission'] != 1:
        abort(403)

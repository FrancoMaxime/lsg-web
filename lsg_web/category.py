from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required, security_required
from lsg_web.db import get_db

bp = Blueprint('category', __name__, url_prefix='/category')


@bp.route('/list', methods=('GET', ))
@login_required
def listing():
    db = get_db()
    categories = db.execute(
        'SELECT * FROM category'
    ).fetchall()
    return render_template('category/list.html', categories=categories)


@bp.route('/create', methods=('GET', 'POST'))
@security_required
def create():
    if request.method == 'POST':
        error = check_category(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO category (name) VALUES (?)', (request.form['name'],)
            )
            db.commit()
            return redirect(url_for('category.listing'))
    return render_template('category/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@security_required
def update(id):
    category = get_category(id)
    if request.method == 'POST':
        error = check_category(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE category SET name =? '
                'WHERE id_category = ?',
                (request.form['name'], id)
            )
            db.commit()
            return redirect(url_for('category.listing'))
    return render_template('category/update.html', category=category)


def check_category(request):
    name = request.form['name']
    if not name:
        return "You must enter a name."
    elif get_db().execute('SELECT * FROM category WHERE name = ?', (name,)).fetchone() is not None:
        return 'This category already exists.'


def get_category(id, recursive=False):
    category = get_db().execute(
        'SELECT * FROM category WHERE id_category = ?',
        (id,)
    ).fetchone()
    if recursive and category is None:
        return None
    elif category is None:
        abort(404, "Category id {0} doesn't exist.".format(id))

    return category
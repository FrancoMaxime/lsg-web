from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required
from lsg_web.db import get_db

bp = Blueprint('food', __name__, url_prefix='/food')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    foods = db.execute(
        'SELECT f.id_food as idfood, f.name as fname, c.name as cname, informations, u.name as uname, f.id_user '
        'FROM food f JOIN user u ON f.id_user = u.id_user JOIN category c ON f.id_category = c.id_category ORDER BY f.id_food ASC'
    ).fetchall()
    return render_template('food/list.html', foods=foods)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        error = check_food(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO food (name, id_category, informations, id_user)'
                ' VALUES (?, ?, ?, ?)',
                (request.form['name'], request.form['category'], request.form['informations'], g.user['id_user'])
            )
            db.commit()
            return redirect(url_for('food.listing'))
    categories = get_db().execute('SELECT * FROM category').fetchall()
    return render_template('food/create.html', categories=categories)


def check_food(request):
    name = request.form['name']
    category = request.form['category']
    informations = request.form['name']

    if not name:
        return "You must enter a name."
    elif not category:
        return 'You must enter a category'
    elif not informations:
        return 'You must enter some informations'
    elif get_db().execute(
                'SELECT * FROM category WHERE id_category = ?', (category,)
        ).fetchone() is None:
        return 'You must select a valid category.'


def get_food(id, check_admin=True):
    food = get_db().execute(
        'SELECT * FROM food WHERE id_food = ?',
        (id,)
    ).fetchone()

    if food is None:
        abort(404, "User id {0} doesn't exist.".format(id))

    if check_admin and not food['id_user'] == g.user['id_user'] and not g.user['id_permission'] == 1:
        abort(403)

    return food


@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def update(id):
    food = get_food(id)
    if request.method == 'POST':
        error = check_food(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE food SET name =?, id_category = ?, informations = ?, id_user = ? '
                'WHERE id_food = ?',
                (request.form['name'], request.form['category'], request.form['informations'], g.user['id_user'], id)
            )
            db.commit()
            return redirect(url_for('food.listing'))
    categories = get_db().execute('SELECT * FROM category').fetchall()
    return render_template('food/update.html', categories=categories, food=food)

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required, security_required
from lsg_web.db import get_db
from lsg_web.category import get_category

bp = Blueprint('food', __name__, url_prefix='/food')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    foods = db.execute(
        'SELECT f.id_food as idfood, f.name as fname, c.name as cname, information, p.name as uname, f.id_person '
        'FROM food f JOIN person p ON f.id_person = p.id_person JOIN category c ON f.id_category = c.id_category  ORDER BY f.id_food ASC'
    ).fetchall()
    return render_template('food/list.html', foods=foods)


@bp.route('/create', methods=('GET', 'POST'))
@security_required
def create():
    if request.method == 'POST':
        error = check_food(request)
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO food (name, id_category, information, id_person)'
                ' VALUES (?, ?, ?, ?)',
                (request.form['name'], request.form['category'], request.form['information'], g.user['id_person'])
            )
            db.commit()
            return redirect(url_for('food.listing'))

    categories = get_db().execute('SELECT * FROM category').fetchall()
    return render_template('food/create.html', categories=categories)


def check_food(request):
    name = request.form['name']
    category = request.form['category']
    information = request.form['information']

    if not name:
        return "You must enter a name."
    elif not category :
        return 'You must enter a category.'
    elif not information:
        return 'You must enter some information.'
    elif get_category(category, True) is None:
        return 'You must select a valid category.'


def get_food(id, recursive=False):
    food = get_db().execute(
        'SELECT * FROM food WHERE id_food = ?',
        (id,)
    ).fetchone()

    if food is None and not recursive:
        abort(404, "Food id {0} doesn't exist.".format(id))

    return food


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@security_required
def update(id):
    food = get_food(id)
    if request.method == 'POST':
        error = check_food(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE food SET name =?, id_category = ?, information = ?, id_person = ? '
                'WHERE id_food = ?',
                (request.form['name'], request.form['category'], request.form['information'], g.user['id_person'], id)
            )
            db.commit()
            return redirect(url_for('food.listing'))
    categories = get_db().execute('SELECT * FROM category').fetchall()
    return render_template('food/update.html', categories=categories, food=food)

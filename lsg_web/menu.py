from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required
from lsg_web.db import get_db

bp = Blueprint('menu', __name__, url_prefix='/menu')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    menus = db.execute(
        'SELECT id_menu , m.name as mname, u.name as uname, m.informations as minformations '
        'FROM menu m INNER JOIN user u on m.id_user = u.id_user WHERE m.actif = 1 ORDER BY m.id_menu ASC'
    ).fetchall()
    return render_template('menu/list.html', menus=menus)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        error = check_menu(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO menu (name, informations, actif, id_user)'
                ' VALUES (?, ?, ?, ?)',
                (request.form['name'], request.form['informations'], 1, g.user['id_user'])
            )
            db.commit()
            return redirect(url_for('menu.listing'))
    return render_template('menu/create.html')


def check_menu(request):
    name = request.form['name']
    informations = request.form['informations']
    if not name:
        return "You must enter a name."
    elif not informations:
        return 'You must enter some informations'


@bp.route('/<int:id>/info', methods=('GET',))
@login_required
def info(id):
    db = get_db()
    menu = db.execute(
        'SELECT id_menu , m.name as mname, u.name as uname, m.informations as minformations '
        'FROM menu m INNER JOIN user u on m.id_user = u.id_user WHERE id_menu = ? ORDER BY m.id_menu ASC',
        (id,)
    ).fetchone()
    composed = db.execute(
        'SELECT f.id_food as idfood, f.name as fname, c.name as cname, informations '
        'FROM composed c INNER JOIN food f ON c.id_food = f.id_food JOIN category c ON c.id_category = f.id_category '
        'WHERE c.id_menu = ?',
        (id,)
    )
    return render_template('menu/info.html', menu=menu, composed=composed)


def get_menu(id, check_admin=True):
    menu = get_db().execute(
        'SELECT * FROM menu WHERE id_menu = ?',
        (id,)
    ).fetchone()

    if menu is None:
        abort(404, "User id {0} doesn't exist.".format(id))

    if check_admin and not menu['id_user'] == g.user['id_user'] and not g.user['id_permission'] == 1:
        abort(403)

    return menu


@bp.route('/<int:id>/add', methods=('GET', 'POST'))
@login_required
def add(id):
    db = get_db()
    if request.method == 'POST':
        food = request.form['food']
        quantity = request.form['quantity']
        error = None

        if food is None:
            error = "You must select a food."
        elif quantity is None:
            error = "You must enter a quantity"
        elif db.execute(
                'SELECT * FROM composed WHERE id_menu = ? AND id_food = ?', (id, food)
        ).fetchone() is not None:
            error = 'Food is already in the menu.'

        if error is not None:
            flash(error)
        else:

            db.execute(
                'INSERT INTO composed (id_menu, id_food, quantity)'
                ' VALUES (?, ?, ?)',
                (id, food, quantity)
            )
            db.commit()
            return redirect(url_for('menu.info', id=id))
    menu = get_menu(id)
    foods = db.execute(
        'SELECT * FROM food WHERE id_food NOT IN (SELECT id_food FROM composed WHERE id_menu = ? )',
        (id,)
    )
    return render_template('menu/add.html', foods=foods, menu=menu)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_menu(id)
    db = get_db()
    db.execute('UPDATE menu SET actif = 0 WHERE id_menu = ?', (id,))
    db.commit()
    return redirect(url_for('menu.listing'))


@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def update(id):
    menu = get_menu(id)
    if request.method == 'POST':
        error = check_menu(request)
        actif = 0
        if 'actif' in request.form:
            actif = 1

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE menu SET name = ?, informations = ?, actif = ? '
                'WHERE id_menu = ?',
                (request.form['name'], request.form['informations'], actif, id)
            )
            db.commit()
            return redirect(url_for('menu.listing'))
    return render_template('menu/update.html', menu=menu)


@bp.route('/<int:id>/copy', methods=('GET', ))
@login_required
def copy(id):
    menu = get_menu(id)

    db = get_db()
    db.execute(
        'INSERT INTO menu (name, informations, actif, id_user)'
        ' VALUES (?, ?, ?, ?)',
        (menu['name']+'_copy', menu['informations'], 1, g.user['id_user'])
    )
    id_copy = db.execute(
        "SELECT last_insert_rowid();"
    ).fetchone()[0]

    all_composed = db.execute(
        "SELECT * FROM composed WHERE id_menu = ?",
        (id,)
    ).fetchall()

    for e in all_composed:
        print(e['quantity'])
        db.execute(
            "INSERT INTO composed(id_menu, id_food, quantity) VALUES "
            "(?, ?, ?)",
            (id_copy, e['id_food'], e['quantity'])
        )
    db.commit()
    return redirect(url_for('menu.info', id=id_copy))


@bp.route('/<int:id1>/<int:id2>/remove', methods=('GET', 'POST'))
@login_required
def remove(id1, id2):
    get_menu(id1)
    db = get_db()
    db.execute('DELETE FROM composed WHERE id_menu = ? AND id_food = ?', (id1, id2))
    db.commit()
    return redirect(url_for('menu.info', id=id1))

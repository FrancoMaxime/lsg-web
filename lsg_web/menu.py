from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required, security_required
from lsg_web.db import get_db
from lsg_web.food import get_food

bp = Blueprint('menu', __name__, url_prefix='/menu')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    menus = db.execute(
        'SELECT id_menu , m.name as mname, p.name as pname, m.information as minformation '
        'FROM menu m INNER JOIN person p on m.id_person = p.id_person WHERE m.actif = 1 ORDER BY m.id_menu ASC'
    ).fetchall()
    return render_template('menu/list.html', menus=menus)


@bp.route('/create', methods=('GET', 'POST'))
@security_required
def create():
    if request.method == 'POST':
        error = check_menu(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO menu (name, information, actif, id_person)'
                ' VALUES (?, ?, ?, ?)',
                (request.form['name'], request.form['information'], 1, g.user['id_person'])
            )
            db.commit()
            return redirect(url_for('menu.listing'))
    return render_template('menu/create.html')


def check_menu(request):
    name = request.form['name']
    information = request.form['information']
    if not name:
        return "You must enter a name."
    elif not information:
        return 'You must enter some information.'


def check_composed(quantity, id1, id2):
    db = get_db()
    food = id2
    quantity = quantity

    if food is None or food == "":
        return "You must select a food."
    elif quantity is None or quantity == "":
        return "You must enter a quantity."
    elif get_food(food, True) is None:
        return 'Food does not exist.'
    elif db.execute(
            'SELECT * FROM composed WHERE id_menu = ? AND id_food = ?', (id1, id2)
    ).fetchone() is not None:
        return 'Food is already in the menu.'


@bp.route('/<int:id>/info', methods=('GET',))
@login_required
def info(id):
    db = get_db()
    get_menu(id)
    menu = db.execute(
        'SELECT id_menu , m.name as mname, p.name as pname, m.information as minformation '
        'FROM menu m INNER JOIN person p on m.id_person = p.id_person WHERE id_menu = ? ORDER BY m.id_menu ASC',
        (id,)
    ).fetchone()
    composed = db.execute(
        'SELECT f.id_food as idfood, f.name as fname, c.name as cname, information '
        'FROM composed c INNER JOIN food f ON c.id_food = f.id_food JOIN category c ON c.id_category = f.id_category '
        'WHERE c.id_menu = ?',
        (id,)
    )
    return render_template('menu/info.html', menu=menu, composed=composed)


def get_menu(id, recursive=False):
    menu = get_db().execute(
        'SELECT * FROM menu WHERE id_menu = ?',
        (id,)
    ).fetchone()

    if menu is None and not recursive:
        abort(404, "Menu id {0} doesn't exist.".format(id))

    return menu


def get_composed(id1, id2):
    composed = get_db().execute(
        'SELECT * FROM composed WHERE id_menu = ? AND id_food = ?',
        (id1, id2)
    ).fetchone()

    if composed is None:
        abort(404, "The food {0} doesn't exist for the menu {1}.".format(id1,id2))

    return composed


@bp.route('/<int:id>/add', methods=('GET', 'POST'))
@security_required
def add(id):
    db = get_db()
    menu = get_menu(id, True)
    if request.method == 'POST':
        error = check_composed(request.form['quantity'], id, request.form['food'])
        if error is not None:
            flash(error)
        else:

            db.execute(
                'INSERT INTO composed (id_menu, id_food, quantity)'
                ' VALUES (?, ?, ?)',
                (id, request.form['food'], request.form['quantity'])
            )
            db.commit()
            return redirect(url_for('menu.info', id=id))
    foods = db.execute(
        'SELECT * FROM food WHERE id_food NOT IN (SELECT id_food FROM composed WHERE id_menu = ? )',
        (id,)
    )
    return render_template('menu/add.html', foods=foods, menu=menu)


@bp.route('/<int:id>/delete', methods=('POST',))
@security_required
def delete(id):
    get_menu(id)
    db = get_db()
    db.execute('UPDATE menu SET actif = 0 WHERE id_menu = ?', (id,))
    db.commit()
    return redirect(url_for('menu.listing'))


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@security_required
def update(id):
    menu = get_menu(id)
    if request.method == 'POST':
        error = check_menu(request)
        actif = 0
        if 'actif' in request.form:
            actif = request.form['actif']

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE menu SET name = ?, information = ?, actif = ? '
                'WHERE id_menu = ?',
                (request.form['name'], request.form['information'], actif, id)
            )
            db.commit()
            return redirect(url_for('menu.listing'))
    return render_template('menu/update.html', menu=menu)


@bp.route('/<int:id>/copy', methods=('POST', ))
@security_required
def copy(id):
    menu = get_menu(id)

    db = get_db()
    db.execute(
        'INSERT INTO menu (name, information, actif, id_person)'
        ' VALUES (?, ?, ?, ?)',
        (menu['name']+'_copy', menu['information'], 1, g.user['id_person'])
    )
    id_copy = db.execute(
        "SELECT last_insert_rowid();"
    ).fetchone()[0]

    all_composed = db.execute(
        "SELECT * FROM composed WHERE id_menu = ?",
        (id,)
    ).fetchall()

    for e in all_composed:
        db.execute(
            "INSERT INTO composed(id_menu, id_food, quantity) VALUES "
            "(?, ?, ?)",
            (id_copy, e['id_food'], e['quantity'])
        )
    db.commit()
    return redirect(url_for('menu.info', id=id_copy))


@bp.route('/<int:id1>/<int:id2>/remove', methods=('GET', 'POST'))
@security_required
def remove(id1, id2):
    get_menu(id1)
    db = get_db()
    db.execute('DELETE FROM composed WHERE id_menu = ? AND id_food = ?', (id1, id2))
    db.commit()
    return redirect(url_for('menu.info', id=id1))


@bp.route('/<int:id1>/<int:id2>/update', methods=('GET', 'POST'))
@security_required
def update_composed(id1, id2):
    menu = get_menu(id1)
    get_composed(id1, id2)
    food = get_food(id2)

    if request.method == 'POST':
        quantity = request.form['quantity']
        if quantity is None or quantity == "":
            flash("You must enter a quantity.")
        else:
            db = get_db()
            db.execute(
                'UPDATE composed SET  quantity = ? WHERE id_menu = ? AND id_food = ?',
                (quantity, id1, id2)
            )
            db.commit()
            return redirect(url_for('menu.info', id=id1))
    return render_template('menu/update_composed.html', food=food, menu=menu)

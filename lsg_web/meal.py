from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required
from lsg_web.db import get_db

bp = Blueprint('meal', __name__, url_prefix='/meal')


@bp.route('/list')
def listing():
    db = get_db()
    meals = db.execute(
        'SELECT id_meal, u.name as uname, m.name as mname, m.informations as minformations, t.name as tname '
        'FROM meal p JOIN user u ON p.id_user = u.id_user JOIN menu m ON m.id_menu = p.id_menu JOIN tray t ON t.id_tray = p.id_tray ORDER BY p.id_meal ASC'
    ).fetchall()
    return render_template('meal/list.html', meals=meals)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        error = check_meal(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO meal ( id_tray, id_menu, start, id_user)'
                ' VALUES (?, ?, datetime("now"), ?)',
                (request.form['tray'], request.form['menu'], g.user['id_user'])
            )
            db.execute(
                'UPDATE tray SET on_use = 1 WHERE id_tray = ?',
                (request.form['tray'],)
            )
            db.commit()
            return redirect(url_for('meal.listing'))

    menus = get_db().execute('SELECT * FROM menu WHERE actif = 1').fetchall()
    trays = get_db().execute('SELECT * FROM tray WHERE actif = 1 AND on_use = 0').fetchall()
    return render_template('meal/create.html', menus=menus, trays=trays)


def check_meal(request):
    menu = request.form['menu']
    tray = request.form['tray']

    if not menu:
        return "You must select a menu."
    elif not tray:
        return 'You must select a tray'
    elif get_db().execute(
            'SELECT * FROM menu WHERE id_menu = ? AND actif = 1', (menu,)
    ).fetchone() is None:
        return 'You must select a valid menu.'
    elif get_db().execute(
            'SELECT * FROM tray WHERE id_tray = ? AND actif = 1 AND on_use = 0', (tray,)
    ).fetchone() is None:
        return 'You must select a valid tray.'


def get_meal(id, check_admin=True):
    meal = get_db().execute(
        'SELECT * FROM meal WHERE id_meal = ?',
        (id,)
    ).fetchone()

    if meal is None:
        abort(404, "Meal id {0} doesn't exist.".format(id))

    if check_admin and not meal['id_user'] == g.user['id_user'] and not g.user['id_permission'] == 1:
        abort(403)

    return meal


@bp.route('/<int:id>/finished', methods=('POST', 'GET'))
@login_required
def finished(id):
    meal = get_meal(id)
    db = get_db()
    db.execute('UPDATE meal SET end = datetime("now") WHERE id_meal = ?', (id,))
    db.execute('UPDATE tray SET on_use = 0 WHERE id_tray = ?', (meal['id_tray'],))
    db.commit()
    return redirect(url_for('tray.listing'))

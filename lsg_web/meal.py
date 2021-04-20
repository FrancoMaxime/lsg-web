from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask import current_app as app
from flask import send_from_directory

from werkzeug.exceptions import abort

from lsg_web.auth import login_required, security_required
from lsg_web.db import get_db
from lsg_web.useful import set_actif

import paho.mqtt.publish as publish

bp = Blueprint('meal', __name__, url_prefix='/meal')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    meals = db.execute(
        'SELECT id_meal, u.name as uname, m.name as mname, m.information as minformation, t.name as tname, '
        'c.name as cname, end FROM meal p JOIN person u ON p.id_user = u.id_person JOIN menu m '
        'ON m.id_menu = p.id_menu JOIN tray t ON t.id_tray = p.id_tray JOIN person c ON p.id_candidate = c.id_person '
        'WHERE p.actif == 1 ORDER BY p.id_meal ASC'
    ).fetchall()
    return render_template('meal/list.html', meals=meals)


@bp.route('/create', methods=('GET', 'POST'))
@security_required
def create():
    if request.method == 'POST':
        error = check_meal_create(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO meal ( id_tray, id_menu, start, id_user, id_candidate, information, actif)'
                ' VALUES (?, ?, datetime("now", "localtime"), ?, ?, ?,?)',
                (request.form['tray'], request.form['menu'], g.user['id_person'], request.form['person'],
                 request.form['information'], 1)
            )
            tmp_id = db.execute("SELECT last_insert_rowid();").fetchone()[0]

            db.execute('UPDATE tray SET on_use = 1 WHERE id_tray = ?', (request.form['tray'],))
            trayname = db.execute("SELECT name FROM tray WHERE id_tray = ?", (request.form['tray'],)).fetchone()[0]
            #publish.single("lsg/" + trayname.lower(), "SERVER\tSTART MEAL\t" + str(tmp_id) + ".csv", hostname=app.config['MQTT_BROKER_URL'])
            db.commit()
            return redirect(url_for('index'))

    menus = get_db().execute('SELECT * FROM menu WHERE actif = 1').fetchall()
    trays = get_db().execute('SELECT * FROM tray WHERE actif = 1 AND on_use = 0 AND online = 1 AND timestamp > datetime("now", "-30 seconds")').fetchall()
    trays = get_db().execute('SELECT * FROM tray WHERE actif = 1 AND on_use = 0').fetchall()
    persons = get_db().execute('SELECT * FROM person ORDER BY id_person ASC').fetchall()
    return render_template('meal/create.html', menus=menus, trays=trays, persons=persons)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@security_required
def update(id):
    meal = get_meal(id)
    if request.method == 'POST':
        error = check_meal(request)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('UPDATE meal SET id_menu = ?, id_user = ?, id_candidate = ?, information = ?'
                       'WHERE id_meal = ?',
                       (request.form['menu'], g.user['id_person'], request.form['person'], request.form['information'],
                        id))
            db.commit()
            return redirect(url_for('meal.listing'))

    menus = get_db().execute('SELECT * FROM menu WHERE actif = 1').fetchall()
    persons = get_db().execute('SELECT * FROM person ORDER BY id_person ASC').fetchall()
    return render_template('meal/update.html', meal=meal, menus=menus, persons=persons)


def check_meal(request):
    menu = request.form['menu']
    person = request.form['person']
    information = request.form['information']

    if not menu:
        return "You must select a menu."
    elif not person:
        return 'You must select a person.'
    elif not information:
        return 'You must enter some information.'
    elif get_db().execute(
            'SELECT * FROM menu WHERE id_menu = ? AND actif = 1', (menu,)
    ).fetchone() is None:
        return 'You must select a valid menu.'
    elif get_db().execute(
            'SELECT * FROM person WHERE id_person = ? AND actif = 1', (person,)
    ).fetchone() is None:
        return 'You must select a valid person.'


def check_meal_create(request):
    error = check_meal(request)
    tray = request.form['tray']

    if not tray:
        return 'You must select a tray.'
    elif get_db().execute(
            'SELECT * FROM tray WHERE id_tray = ? AND actif = 1 AND on_use = 0', (tray,)
    ).fetchone() is None:
        return 'You must select a valid tray.'
    return error


def get_meal(id):
    meal = get_db().execute(
        'SELECT * FROM meal WHERE id_meal = ?',
        (id,)
    ).fetchone()

    if meal is None:
        abort(404, "Meal id {0} doesn't exist.".format(id))

    return meal


@bp.route('/<int:id>/finished', methods=('POST', 'GET'))
@security_required
def finished(id):
    meal = get_meal(id)
    db = get_db()
    db.execute('UPDATE meal SET end = datetime("now", "localtime") WHERE id_meal = ?', (id,))
    db.execute('UPDATE tray SET on_use = 0 WHERE id_tray = ?', (meal['id_tray'],))
    trayname = db.execute("SELECT name FROM tray WHERE id_tray = ?", (meal['id_tray'],)).fetchone()[0]
    #publish.single("lsg/" + trayname.lower(), "SERVER\tEND MEAL\t", hostname=app.config['MQTT_BROKER_URL'])
    db.commit()
    return redirect(url_for('index'))


@bp.route('/<int:id>/info', methods=('GET',))
@login_required
def info(id):
    meal = get_meal(id)
    db = get_db()
    meal = db.execute(
        'SELECT id_meal, u.name as uname, m.name as mname, m.information as menuinformation, t.name as tname, '
        'm.id_menu as idmenu, c.name as cname, p.information as mealinformation, end as date FROM meal p  '
        'JOIN menu m ON m.id_menu = p.id_menu JOIN tray t ON t.id_tray = p.id_tray JOIN person u '
        'ON p.id_user = u.id_person JOIN person c ON p.id_candidate = c.id_person WHERE id_meal = ?ORDER BY p.id_meal '
        'ASC', (id,)
    ).fetchone()
    return render_template('meal/info.html', meal=meal, imgname="data/" + str(id) + ".png")


@bp.route('/<int:id>/download', methods=('GET',))
@login_required
def download(id):
    meal = get_meal(id)
    filename = str(id) + ".csv"
    return send_from_directory(app.config["DATA_UPLOADS"], filename=filename)


@bp.route('/<int:id>/delete', methods=('POST',))
@security_required
def delete(id):
    get_meal(id)
    db = get_db()
    db.execute('UPDATE meal SET actif = 0 WHERE id_meal = ?', (id,))
    db.commit()
    return redirect(url_for('meal.listing'))

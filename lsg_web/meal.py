from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask import current_app as app
from flask import send_from_directory

from werkzeug.exceptions import abort

from lsg_web.auth import login_required
from lsg_web.db import get_db

import paho.mqtt.publish as publish

bp = Blueprint('meal', __name__, url_prefix='/meal')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    meals = db.execute(
        'SELECT id_meal, u.name as uname, m.name as mname, m.informations as minformations, t.name as tname, c.name as cname, end '
        'FROM meal p JOIN user u ON p.id_user = u.id_user JOIN menu m ON m.id_menu = p.id_menu JOIN tray t ON t.id_tray = p.id_tray JOIN user c ON p.id_client = c.id_user ORDER BY p.id_meal ASC'
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
                'INSERT INTO meal ( id_tray, id_menu, start, id_user, id_client, informations)'
                ' VALUES (?, ?, datetime("now"), ?, ?, ?)',
                (request.form['tray'], request.form['menu'], g.user['id_user'], request.form['user'], request.form['informations'])
            )
            tmp_id = db.execute("select last_insert_rowid();").fetchone()[0]
            db.execute(
                'UPDATE tray SET on_use = 1 WHERE id_tray = ?',
                (request.form['tray'],)
            )
            trayname = db.execute("SELECT name FROM tray WHERE id_tray = ?", (request.form['tray'],)).fetchone()[0]
            publish.single("lsg/" + trayname.lower(), "SERVER\tSTART MEAL\t" + str(tmp_id) + ".csv", hostname=app.config['MQTT_BROKER_URL'])
            db.commit()
            return redirect(url_for('index'))

    menus = get_db().execute('SELECT * FROM menu WHERE actif = 1').fetchall()
    #trays = get_db().execute('SELECT * FROM tray WHERE actif = 1 AND on_use = 0 AND online = 1 AND timestamp > datetime("now", "-30 seconds")').fetchall()
    trays = get_db().execute('SELECT * from tray').fetchall()
    users = get_db().execute(
        'SELECT *'
        ' FROM user ORDER BY id_user ASC'
    ).fetchall()
    return render_template('meal/create.html', menus=menus, trays=trays, users=users)


def check_meal(request):
    menu = request.form['menu']
    tray = request.form['tray']
    user = request.form['user']
    informations = request.form['informations']

    if not menu:
        return "You must select a menu."
    elif not tray:
        return 'You must select a tray'
    elif not user:
        return 'You must select a user'
    elif not informations:
        return 'You must enter some informations'
    elif get_db().execute(
            'SELECT * FROM menu WHERE id_menu = ? AND actif = 1', (menu,)
    ).fetchone() is None:
        return 'You must select a valid menu.'
    elif get_db().execute(
            'SELECT * FROM user WHERE id_user = ? ', (user,)
    ).fetchone() is None:
        return 'You must select a valid user.'
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
    trayname = db.execute("SELECT name FROM tray WHERE id_tray = ?", (meal['id_tray'],)).fetchone()[0]
    publish.single("lsg/" + trayname.lower(), "SERVER\tEND MEAL\t", hostname=app.config['MQTT_BROKER_URL'])
    db.commit()
    return redirect(url_for('meal.listing'))


@bp.route('/<int:id>/info', methods=('GET',))
@login_required
def info(id):
    db = get_db()
    meal = db.execute(
        'SELECT id_meal, u.name as uname, m.name as mname, m.informations as menuinformations, t.name as tname, m.id_menu as idmenu, c.name as cname, p.informations as mealinformations, end as date '
        'FROM meal p JOIN user u ON p.id_user = u.id_user JOIN menu m ON m.id_menu = p.id_menu JOIN tray t ON t.id_tray = p.id_tray JOIN user c ON p.id_client = c.id_user  WHERE id_meal = ?ORDER BY p.id_meal ASC',
        (id,)
    ).fetchone()
    return render_template('meal/info.html', meal=meal, imgname="data/" + str(id) + ".png")


@bp.route('/<int:id>/uploads', methods=['GET', 'POST'])
@login_required
def download(id):
    filename = str(id) + ".csv"
    return send_from_directory(app.config["DATA_UPLOADS"], filename=filename)

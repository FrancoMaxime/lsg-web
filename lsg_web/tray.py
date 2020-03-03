from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required
from lsg_web.db import get_db

bp = Blueprint('tray', __name__, url_prefix='/tray')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    trays = db.execute(
        'SELECT t.id_tray as id_tray,t.name as tname, v.name as vname, t.informations as informations, ip, online, t.on_use as on_use '
        'FROM tray t INNER JOIN version v on t.id_version = v.id_version ORDER BY id_tray ASC'
    ).fetchall()
    return render_template('tray/list.html', trays=trays)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if g.user['id_permission'] != 1:
        abort(403)

    if request.method == 'POST':
        name = request.form['name']
        version = request.form['version']
        informations = request.form['informations']

        error = check_tray(request)
        db = get_db()

        if db.execute(
                'SELECT id_tray FROM tray WHERE name = ?', (name,)
        ).fetchone() is not None:
            error = 'Tray {} is already registered.'.format(name)

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO tray (name, id_version, informations, ip, online, actif, on_use)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (name, version, informations, "None", 0, 1, 0)
            )
            db.commit()
            return redirect(url_for('tray.listing'))
    versions = get_db().execute('SELECT * FROM version').fetchall()
    return render_template('tray/create.html', versions=versions)


def check_tray(request):
    name = request.form['name']
    version = request.form['version']
    informations = request.form['informations']

    if not name:
        return "You must enter a name."
    elif not version:
        return 'You must enter a version'
    elif not informations:
        return 'You must enter some informations'
    elif get_db().execute(
                'SELECT * FROM version WHERE id_version = ?', (version,)
        ).fetchone() is None:
        return 'You must select a valid version.'


def get_tray(id, check_admin=True):
    tray = get_db().execute(
        'SELECT * FROM tray INNER JOIN version on tray.id_version = version.id_version WHERE id_tray = ?',
        (id,)
    ).fetchone()

    if tray is None:
        abort(404, "Tray id {0} doesn't exist.".format(id))

    if check_admin and not g.user['id_permission'] == 1:
        abort(403)

    return tray


@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def update(id):
    tray = get_tray(id)
    if request.method == 'POST':
        error = check_tray(request)
        actif = 0
        if 'actif' in request.form:
            actif = 1

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tray SET name =?, id_version = ?, informations = ?, actif = ? '
                'WHERE id_tray = ?',
                (request.form['name'], request.form['version'], request.form['informations'], actif, id)
            )
            db.commit()
            return redirect(url_for('tray.listing'))
    versions = get_db().execute('SELECT * FROM version').fetchall()
    return render_template('tray/update.html', versions=versions, tray=tray)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_tray(id)
    db = get_db()
    db.execute('UPDATE tray SET actif = 0 WHERE id_tray = ?', (id,))
    db.commit()
    return redirect(url_for('tray.listing'))
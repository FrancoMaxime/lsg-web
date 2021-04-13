import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flask import current_app as app
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from lsg_web.auth import security_required
from lsg_web.db import get_db
from lsg_web.useful import set_actif

bp = Blueprint('tray', __name__, url_prefix='/tray')


@bp.route('/list')
@security_required
def listing():
    db = get_db()
    trays = db.execute(
        'SELECT t.id_tray as id_tray,t.name as tname, v.name as vname, t.information as information, ip, online, t.on_use as on_use, t.timestamp as timestamp, DATETIME("now", "-30 seconds") as now '
        'FROM tray t INNER JOIN version v on t.id_version = v.id_version ORDER BY id_tray ASC'
    ).fetchall()
    return render_template('tray/list.html', trays=trays)


@bp.route('/create', methods=('GET', 'POST'))
@security_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        version = request.form['version']
        information = request.form['information']

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
                'INSERT INTO tray (name, id_version, information, ip, online, actif, on_use, timestamp)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, datetime("now", "-45 seconds"))',
                (name, version, information, "None", 0, 1, 0)
            )
            db.commit()
            return redirect(url_for('tray.listing'))
    versions = get_db().execute('SELECT * FROM version').fetchall()
    return render_template('tray/create.html', versions=versions)


def check_tray(request):
    name = request.form['name']
    version = request.form['version']
    information = request.form['information']

    if not name or name == "":
        return "You must enter a name."
    elif not version:
        return 'You must enter a version.'
    elif not information:
        return 'You must enter some information.'
    elif get_db().execute(
                'SELECT * FROM version WHERE id_version = ?', (version,)
        ).fetchone() is None:
        return 'You must select a valid version.'


def get_tray(id):
    tray = get_db().execute(
        'SELECT * FROM tray INNER JOIN version on tray.id_version = version.id_version WHERE id_tray = ?',
        (id,)
    ).fetchone()

    if tray is None:
        abort(404, "Tray id {0} doesn't exist.".format(id))

    return tray


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@security_required
def update(id):
    tray = get_tray(id)
    if request.method == 'POST':
        error = check_tray(request)
        actif = set_actif(request)

        db = get_db()
        if db.execute(
                'SELECT id_tray FROM tray WHERE name = ? AND id_tray != ?', (request.form['name'],id)
        ).fetchone() is not None:
            error = 'Tray {} is already registered.'.format(request.form['name'])

        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE tray SET name =?, id_version = ?, information = ?, actif = ? '
                'WHERE id_tray = ?',
                (request.form['name'], request.form['version'], request.form['information'], actif, id)
            )
            db.commit()
            return redirect(url_for('tray.listing'))
    versions = get_db().execute('SELECT * FROM version').fetchall()
    return render_template('tray/update.html', versions=versions, tray=tray)


@bp.route('/<int:id>/delete', methods=('POST',))
@security_required
def delete(id):
    get_tray(id)
    db = get_db()
    db.execute('UPDATE tray SET actif = 0 WHERE id_tray = ?', (id,))
    db.commit()
    return redirect(url_for('tray.listing'))


@bp.route('/connect', methods=('POST',))
def connect():
    name = request.form['name']
    if get_db().execute('SELECT * FROM tray WHERE name = ?', (name,)).fetchone() is not None:
        ip = request.form['ip']
        db = get_db()
        db.execute('UPDATE tray SET online = 1, ip = ?, timestamp = DATETIME("now") WHERE name = ?',
                   (ip, name)
                   )
        db.commit()
        return jsonify(success=True)
    return abort(400)


@bp.route('/data', methods=('POST',))
def data():
    error = None
    if not request.files:
        error = "You must select an image."
    else:
        if "data" in request.files and "image" in request.files:
            data = request.files["data"]
            filename = secure_filename(data.filename)
            image = request.files["image"]
            fimage = secure_filename(image.filename)
            if filename == "":
                error = "No Filename."
            if fimage == "":
                error = "No Filename."
            if error is None:
                ext = filename.rsplit(".", 1)[1]
                ext2 = fimage.rsplit(".", 1)[1]
                if ext not in ("txt", "csv"):
                    error = "Bad type of file"
                if ext2 not in ("png", "jpeg", "jpg"):
                    error = "Bad type of file"

                if error is None:
                    data.save(os.path.join(app.config["DATA_UPLOADS"], filename))
                    image.save(os.path.join(app.config["DATA_UPLOADS"], fimage))
                    return jsonify(success=True)
    return abort(404, "Error : " + str(error))





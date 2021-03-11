from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask import current_app as app


from lsg_web.auth import login_required
from lsg_web.db import get_db
import os
from datetime import date as dtdate

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/list')
def listing():
    db = get_db()
    users = db.execute(
        'SELECT *'
        ' FROM user ORDER BY id_user ASC'
    ).fetchall()
    return render_template('user/list.html', users=users)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if g.user['id_permission'] != 1:
        abort(403)

    if request.method == 'POST':
        print(request.form['birthdate'])
        name = request.form['name']
        mail = request.form['mail']
        password1 = request.form['password1']
        birthdate = request.form['birthdate']
        gender = request.form['gender']
        weight = request.form['weight']
        permission = request.form['permission']
        error = check_user(request)
        db = get_db()

        if db.execute(
                'SELECT id_user FROM user WHERE mail = ?', (mail,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(mail)

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO user (name, mail, password, birthdate, gender, weight, actif, id_permission,filename)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (name, mail, generate_password_hash(password1), birthdate, gender, weight, 1, permission, "tmp.png")
            )
            image = request.files["image"]
            tmp_id = db.execute(
                "SELECT last_insert_rowid()"
            ).fetchone()[0]
            ext = image.filename.rsplit(".", 1)[1]
            filename = str(tmp_id) + "." + ext
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
            db.execute("UPDATE user SET filename = ? WHERE id_user = ?",
                       (filename, tmp_id)
                       )
            db.commit()

            return redirect(url_for('user.listing'))

    return render_template('user/create.html')


def get_user(id, check_admin=True):
    user = get_db().execute(
        'SELECT * FROM user WHERE id_user = ?',
        (id,)
    ).fetchone()

    if user is None:
        abort(404, "User id {0} doesn't exist.".format(id))

    if check_admin and not user['id_user'] == g.user['id_user'] and not g.user['id_permission'] == 1:
        abort(403)

    return user


def check_user(request, update=False):
    error = None

    if not request.form['name']:
        error = 'Name is required.'
    elif not request.form['mail']:
        error = 'Mail is required.'
    elif not request.form['password1'] or not request.form['password2']:
        error = 'You must enter a password.'
    elif request.form['password1'] != request.form['password2']:
        error = 'The passwords must be the same.'
    elif not request.form['birthdate']:
        error = 'You must enter a birthdate.'
    elif not request.form['gender']:
        error = 'You must select a gender.'
    elif not request.form['weight']:
        error = 'You must enter a weight.'
    elif not request.files:
        error = "You must select an image."

    is_valid = True
    try:
        dtdate.fromisoformat(request.form['birthdate'])
    except ValueError:
        is_valid = False
    if not is_valid:
        error = 'You must enter a valid birthdate.'

    if not update:
        image = request.files["image"]
        filename = secure_filename(image.filename)
        if filename == "":
            error = "No Filename."
        ext = filename.rsplit(".", 1)[1]
        if not ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
            error = "Bad extension."

    return error


@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def update(id):
    user = get_user(id)

    if request.method == 'POST':
        error = ""
        if request.files["image"].filename == "":
            error = check_user(request, True)
        else:
            error = check_user(request)
        db = get_db()

        name = request.form['name']
        mail = request.form['mail']
        password1 = request.form['password1']
        birthdate = request.form['birthdate']
        gender = request.form['gender']
        weight = request.form['weight']
        actif = 0
        if 'actif' in request.form:
            actif = 1
        permission = 2
        if g.user['id_permission'] == 1:
            permission = request.form['permission']

        if db.execute(
                'SELECT id_user FROM user WHERE mail = ? AND id_user != ?', (mail, id)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(mail)

        if error is not None:
            flash(error)
        else:
            if request.files["image"].filename != "":
                image = request.files["image"]
                ext = image.filename.rsplit(".", 1)[1]
                filename = str(id) + "." + ext
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                db.execute(
                    'UPDATE user SET name = ?, mail = ?, password = ?, birthdate = ?, gender = ?, weight = ?, actif = ?, id_permission = ?, filename= ?'
                    ' WHERE id_user = ?',
                    (name, mail, generate_password_hash(password1), birthdate, gender, weight, actif, permission, filename, id)
                )
            else:
                db.execute(
                    'UPDATE user SET name = ?, mail = ?, password = ?, birthdate = ?, gender = ?, weight = ?, actif = ?, id_permission = ?'
                    ' WHERE id_user = ?',
                    (name, mail, generate_password_hash(password1), birthdate, gender, weight, actif, permission, id)
                )

            db.commit()
            return redirect(url_for('user.listing'))

    return render_template('user/update.html', user=user)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_user(id)
    db = get_db()
    db.execute('UPDATE user SET actif = 0 WHERE id_user = ?', (id,))
    db.commit()
    return redirect(url_for('user.listing'))
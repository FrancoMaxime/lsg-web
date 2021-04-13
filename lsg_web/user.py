from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask import current_app as app

from lsg_web.useful import set_actif
from lsg_web.auth import security_required
from lsg_web.db import get_db
from lsg_web.person import get_person
import os

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/list')
@security_required
def listing():
    db = get_db()
    users = db.execute(
        'SELECT *'
        ' FROM user INNER JOIN person ON user.id_person = person.id_person ORDER BY id_user ASC'
    ).fetchall()
    return render_template('user/list.html', users=users)


@bp.route('/create', methods=('GET', 'POST'))
@security_required
def create():
    if request.method == 'POST':
        error = check_user(request)
        db = get_db()
        mail = request.form['mail']
        if db.execute(
                'SELECT id_user FROM user WHERE mail = ?', (mail,)
        ).fetchone() is not None:
            error = 'User {} already registered.'.format(mail)

        if error is not None:
            flash(error)
        else:
            id_person = request.form['person']
            password1 = request.form['password1']
            permission = request.form['permission']
            filename = "simple_user.png"
            if permission == 1 or permission == '1':
                filename = "administrator.png"
            db.execute(
                'INSERT INTO user (id_person, mail, password, actif, id_permission, filename)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (id_person, mail, generate_password_hash(password1), 1, permission, filename)
            )
            if 'image' in request.files:
                image = request.files["image"]
                tmp_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
                if image.filename != "":
                    ext = image.filename.rsplit(".", 1)[1]
                    filename = str(tmp_id) + "." + ext
                    image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                    db.execute("UPDATE user SET filename = ? WHERE id_user = ?", (filename, tmp_id))
            db.commit()

            return redirect(url_for('user.listing'))
    persons = get_db().execute('SELECT * FROM person p LEFT JOIN user u ON p.id_person = u.id_person WHERE u.mail is NULL ORDER BY id_person ASC').fetchall()
    return render_template('user/create.html', persons=persons)


def get_user(id):
    user = get_db().execute(
        'SELECT * FROM user INNER JOIN person on user.id_person = person.id_person WHERE id_user = ?',
        (id,)
    ).fetchone()

    if user is None:
        abort(404, "User id {0} doesn't exist.".format(id))

    return user


def check_user(request):
    error = None
    if not request.form['person'] or request.form['person'] == "":
        error = "The account should be linked to a person."
    elif not request.form['mail']:
        error = 'Mail is required.'
    elif not request.form['password1'] or not request.form['password2']:
        error = 'You must enter a password.'
    elif request.form['password1'] != request.form['password2']:
        error = 'The passwords must be the same.'
    elif get_person(request.form['person']) is None:
        error = 'The person must exist.'

    if 'image' in request.files:
        image = request.files["image"]
        filename = secure_filename(image.filename)
        if filename != "":
            ext = filename.rsplit(".", 1)[1]
            if not ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
                error = "Bad extension."

    return error


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@security_required
def update(id):
    user = get_user(id)

    if request.method == 'POST':
        error = check_user(request)
        db = get_db()

        mail = request.form['mail']
        password1 = request.form['password1']
        actif = set_actif(request)
        permission = request.form['permission']

        if db.execute(
                'SELECT id_user FROM user WHERE mail = ? AND id_user != ?', (mail, id)
        ).fetchone() is not None:
            error = 'User {} already registered.'.format(mail)

        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE user SET mail = ?, password = ?, actif = ?, id_permission = ? '
                'WHERE id_user = ?',
                (mail, generate_password_hash(password1), actif, permission, id)
            )
            if 'image' in request.files:
                if request.files["image"].filename != "":
                    image = request.files["image"]
                    ext = image.filename.rsplit(".", 1)[1]
                    filename = str(id) + "." + ext
                    image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                    db.execute(
                        'UPDATE user SET  filename= ? WHERE id_user = ?',
                        (filename, id)
                    )

            db.commit()
            return redirect(url_for('user.listing'))
    persons = get_db().execute('SELECT * FROM person p LEFT JOIN user u ON p.id_person = u.id_person WHERE u.mail is NULL OR u.id_person = ? ORDER BY id_person ASC', (user['id_person'],)).fetchall()
    return render_template('user/update.html', user=user, persons=persons)


@bp.route('/<int:id>/delete', methods=('POST',))
@security_required
def delete(id):
    get_user(id)
    db = get_db()
    db.execute('UPDATE user SET actif = 0 WHERE id_user = ?', (id,))
    db.commit()
    return redirect(url_for('user.listing'))


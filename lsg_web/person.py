from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


from lsg_web.auth import login_required, security_required
from lsg_web.db import get_db
from lsg_web.useful import set_actif
from datetime import date as dtdate

bp = Blueprint('person', __name__, url_prefix='/person')


@bp.route('/list')
@login_required
def listing():
    db = get_db()
    persons = db.execute(
        'SELECT * FROM person ORDER BY id_person ASC'
    ).fetchall()
    return render_template('person/list.html', persons=persons)


@bp.route('/<int:id>/info', methods=('GET',))
@login_required
def info(id):
    db = get_db()
    person = get_person(id)
    meals = db.execute(
        'SELECT meal.information as mealinfo, menu.name as menuname, menu.information as menuinfo, meal.start as start,'
        ' meal.end as end, meal.id_meal as id_meal, meal.id_menu as id_menu '
        'FROM meal meal INNER JOIN menu menu ON meal.id_menu = menu.id_menu WHERE meal.id_candidate = ? '
        'ORDER BY meal.id_meal ASC', (id,)
    ).fetchall()
    return render_template('person/info.html', meals=meals, person=person)


@bp.route('/create', methods=('GET', 'POST'))
@security_required
def create():
    if request.method == 'POST':
        error = check_person(request)
        db = get_db()

        if error is not None:
            flash(error)
        else:
            name = request.form['name']
            birthdate = request.form['birthdate']
            gender = request.form['gender']
            weight = request.form['weight']
            db.execute(
                'INSERT INTO person (name, birthdate, gender, weight, actif)'
                ' VALUES (?, ?, ?, ?, ?)',
                (name, birthdate, gender, weight, 1)
            )
            db.commit()

            return redirect(url_for('person.listing'))

    return render_template('person/create.html')


def get_person(id,):
    person = get_db().execute(
        'SELECT * FROM person WHERE id_person = ?',
        (id,)
    ).fetchone()

    if person is None:
        abort(404, "Person id {0} doesn't exist.".format(id))

    return person


def check_person(request):
    error = None

    if not request.form['name']:
        error = 'Name is required.'
    elif not request.form['birthdate']:
        error = 'You must enter a birthdate.'
    elif not request.form['gender'] :
        error = 'You must select a gender.'
    elif not request.form['weight']:
        error = 'You must enter a weight.'

    is_valid = True
    try:
        dtdate.fromisoformat(request.form['birthdate'])
    except ValueError:
        is_valid = False
    if not is_valid:
        error = 'You must enter a valid birthdate.'
    return error


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@security_required
def update(id):
    person = get_person(id)

    if request.method == 'POST':
        error = check_person(request)
        db = get_db()

        if error is not None:
            flash(error)
        else:
            name = request.form['name']
            birthdate = request.form['birthdate']
            gender = request.form['gender']
            weight = request.form['weight']
            actif = set_actif(request)
            db.execute(
                'UPDATE person SET name = ?, birthdate = ?, gender = ?, weight = ?, actif = ?'
                ' WHERE id_person = ?',
                (name, birthdate, gender, weight, actif, id)
            )

            db.commit()
            return redirect(url_for('person.listing'))

    return render_template('person/update.html', person=person)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_person(id)
    db = get_db()
    db.execute('UPDATE person SET actif = 0 WHERE id_person = ?', (id,))
    db.commit()
    return redirect(url_for('person.listing'))
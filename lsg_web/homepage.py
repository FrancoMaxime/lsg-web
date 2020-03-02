from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from lsg_web.auth import login_required
from lsg_web.db import get_db

bp = Blueprint('index', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    meals = db.execute(
        'SELECT u.id_user as uid, id_meal, u.name as uname, m.name as mname, m.informations as minformations, t.name as tname '
        'FROM meal p JOIN user u ON p.id_user = u.id_user JOIN menu m ON m.id_menu = p.id_menu JOIN tray t ON t.id_tray = p.id_tray WHERE end is NULL ORDER BY p.id_meal ASC'
    ).fetchall()
    return render_template('index.html', meals=meals)
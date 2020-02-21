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
    meal = db.execute(
        'SELECT * FROM meal where id_user =(?)'
        ' ORDER BY start DESC LIMIT 1', (g.user['id_user'],)
    ).fetchall()
    return render_template('index.html', meal=meal)
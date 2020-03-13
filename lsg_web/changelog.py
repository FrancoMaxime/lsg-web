from flask import (
    Blueprint, render_template
)

from lsg_web.auth import login_required

bp = Blueprint('changelog', __name__)


@bp.route('/changelog')
@login_required
def consult():
    return render_template('changelog/changelog.html')
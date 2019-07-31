from flask import abort, Blueprint, flash, g, redirect, render_template, request, url_for
import random
from . import lslga_utils
from .db import get_db
from . import subsets

bp = Blueprint('viewlist', __name__, url_prefix='/list')

@bp.route('/all')
def list_all():
    
    db = get_db()

    inspections = db.execute(
        ("SELECT a.inspection_id, lslga_id, username, quality, feedback, created "
        "FROM inspection a LEFT JOIN user b ON a.user_id = b.id")
    ).fetchall()

    # Turn keys and inspections into normal python lists
    keys = inspections[0].keys() if len(inspections) > 0 else []
    inspections = [[item for item in row] for row in inspections]

    # Insert galaxy name into lists
    if len(keys) > 0:
        keys.insert(2, 'galaxy_name')
    for row in inspections:
        row.insert(2, lslga_utils.get_lslga_tablerow(row[1])['GALAXY'])

    return render_template('inspection-list.html', keys=keys, inspections=inspections)

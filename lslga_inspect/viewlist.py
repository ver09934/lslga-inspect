from flask import abort, Blueprint, flash, g, redirect, render_template, request, url_for
import random
from . import lslga_utils
from .db import get_db
from . import subsets

bp = Blueprint('viewlist', __name__, url_prefix='/list')

@bp.route('/all')
def list_all():
    
    db = get_db()

    # ----- All inspections -----

    inspections = db.execute(
        ("SELECT a.inspection_id, lslga_id, username, quality, feedback, subset, created "
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

    # ----- User inspections -----

    if g.user is not None:

        user_inspections = db.execute(
            ("SELECT a.inspection_id, lslga_id, username, quality, feedback, subset, created "
            "FROM inspection a LEFT JOIN user b ON a.user_id = b.id WHERE a.user_id = ?"),
            (g.user['id'],)
        ).fetchall()

        user_keys = user_inspections[0].keys() if len(user_inspections) > 0 else []
        user_inspections = [[item for item in row] for row in user_inspections]

        if len(user_keys) > 0:
            user_keys.insert(2, 'galaxy_name')
            user_keys.append('inspect_link')
        for row in user_inspections:
            row.insert(2, lslga_utils.get_lslga_tablerow(row[1])['GALAXY'])
            row.append('<a href="{}">{}</a>'.format(url_for('inspect.inspect_galaxy', catalog_raw=row[6], galaxy_id=row[1]),
                '{} ({})'.format(lslga_utils.get_lslga_tablerow(row[1])['GALAXY'], row[6])))
            # The above is a temporary solution

    else:

        user_keys = []
        user_inspections = []

    return render_template('inspection-list.html', keys=keys, inspections=inspections, user_keys=user_keys, user_inspections=user_inspections)

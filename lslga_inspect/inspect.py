from flask import abort, Blueprint, flash, g, redirect, render_template, request, Response, url_for
import random
from . import lslga_utils
from .db import get_db

bp = Blueprint('inspect', __name__)

# Other catalogs: UGC, PGC
catalog_match_strings = {
    'ngc': 'NGC',
    'sdss': 'SDSS',
    '2mas': '2MAS',
}
catalog_pretty_strings = {
    'all': '',
    'ngc': 'NGC',
    'sdss': 'SDSS',
    '2mas': '2MASS/2MASX',
}

@bp.route('/')
def tmp_function():
    return redirect(url_for('.index'))

@bp.route('/inspect')
def index():
    return render_template('catalog-list.html', pretty_strings=catalog_pretty_strings)

@bp.route('/inspect/list')
def list():
    
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

    return render_template('list.html', keys=keys, inspections=inspections)

@bp.route('/inspect/<string:catalog_raw>')
def inspect_catalog(catalog_raw):

    if catalog_raw == 'all':
        catalog = None
    elif catalog_raw not in catalog_match_strings:
        return abort(500, 'Catalog name not found.')
    else:
        catalog = catalog_match_strings[catalog_raw]

    t = lslga_utils.get_t()

    while True:

        length = length = len(t)
        rand_index = random.randint(0, length - 1)

        if catalog is not None:
            if t[rand_index]['GALAXY'][:len(catalog)] == catalog:
                if lslga_utils.test_footprint(rand_index):
                    break
        else:
            if lslga_utils.test_footprint(rand_index):
                break
    
    rand_id = lslga_utils.get_lslga_id(rand_index)
    return redirect(url_for('.inspect_galaxy', catalog_raw=catalog_raw, galaxy_id=rand_id))

@bp.route('/inspect/<string:catalog_raw>/<int:galaxy_id>', methods=('GET', 'POST'))
def inspect_galaxy(catalog_raw, galaxy_id):

    if request.method == 'POST':

        if g.user is None:
            flash("User must be logged in to submit information!")
        else:

            db = get_db()

            existing_inspection = db.execute(
                'SELECT * FROM inspection WHERE user_id = ? AND lslga_id = ?',
                (g.user['id'], galaxy_id)
            ).fetchone()

            if existing_inspection is not None:
                db.execute(
                    "UPDATE inspection SET quality = ?, feedback = ? WHERE user_id = ? AND lslga_id = ?",
                    (request.form['quality'], None if request.form['feedback'] == '' else request.form['feedback'], g.user['id'], galaxy_id)
                )
            else:
                db.execute(
                    "INSERT INTO inspection (user_id, lslga_id, quality, feedback) VALUES (?, ?, ?, ?)",
                    (g.user['id'], galaxy_id, request.form['quality'], None if request.form['feedback'] == '' else request.form['feedback'])
                )

            db.commit()

            return redirect(url_for('.inspect_catalog', catalog_raw=catalog_raw))

    if catalog_raw != 'all' and catalog_raw not in catalog_match_strings:
        return abort(500, 'Catalog name not found.')
        
    galaxy_info = lslga_utils.get_lslga_tablerow(galaxy_id)

    viewer_link = (
        "http://legacysurvey.org/viewer"
        "?ra={:.7f}"
        "&dec={:.7f}"
        "&zoom=14"
        "&lslga"
    ).format(galaxy_info['RA'], galaxy_info['DEC'])

    inspection_options = {
        'good': 'Good',
        'bad-ellipse': 'Ellipse wrong size/shape',
        'spurious-src': 'Spurious source (star/smaller galaxy)',
        'lsb-resolved': 'Resolved low surface brightness galaxy',
        'bad-mask': 'Galaxy masked too aggressively'
    }

    db = get_db()

    success = False

    if g.user is not None:

        existing_inspection = db.execute(
            'SELECT * FROM inspection WHERE user_id = ? AND lslga_id = ?',
            (g.user['id'], galaxy_id)
        ).fetchone()

        if existing_inspection is not None:

            checked_option = existing_inspection['quality']
            load_text = '' if existing_inspection['feedback'] == None else existing_inspection['feedback']
            submit_button = 'Update'

            success = True

    if not success:

        checked_option = 'good'
        load_text = ''
        submit_button = 'Submit'
    
    return render_template(
        "inspect.html",
        catalog_raw=catalog_raw,
        catalog_pretty=catalog_pretty_strings[catalog_raw],
        id=galaxy_id,
        info=galaxy_info,
        viewer_link = viewer_link,
        inspection_options=inspection_options,
        checked_option=checked_option,
        load_text=load_text,
        submit_button=submit_button
    )

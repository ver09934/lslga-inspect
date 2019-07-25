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
    
    '''
    inspections = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    '''

    inspections = db.execute(
        "SELECT * FROM inspection"
    ).fetchall()

    keys = inspections[0].keys() if len(inspections) > 0 else []

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

    # Should maybe cache the bad list somehow
    while True:

        length = len(t)
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
            # print('-'*60 + "\nUser is not logged in\n" + '-'*60)
            flash("User must be logged in to submit information!")
            # abort(500, 'User must be logged in to submit information.')
        else:
            # print('-'*60)
            # print(
            #     "Here is the quality for {} submitted by {}: {}"
            #     .format(galaxy_id, g.user['username'], request.form['quality'])
            # )
            # print('-'*60)

            # TODO: Check if inspection already exists, and if so, replace it
            # instead of creating a new entry

            galaxy_name = lslga_utils.get_lslga_tablerow(galaxy_id)['GALAXY']
            # g.user['id']

            db = get_db()

            db.execute(
                "INSERT OR IGNORE INTO galaxy (lslga_id, galaxy_name) VALUES (?, ?);",
                (galaxy_id, galaxy_name)
            )

            db.execute(
                "INSERT INTO inspection (lslga_id, user_id, quality) VALUES (?, ?, ?)",
                (galaxy_id, g.user['id'], request.form['quality'])
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

    return render_template(
        "inspect.html",
        catalog_raw=catalog_raw,
        catalog_pretty=catalog_pretty_strings[catalog_raw],
        id=galaxy_id,
        info=galaxy_info,
        viewer_link = viewer_link
    )

from flask import Blueprint, render_template, redirect, url_for, request, abort, Response, current_app
import random
from .. import lslgautils

bp = Blueprint('inspect', __name__)

@bp.route('/')
def inspect():
    print(current_app.config['FITS_PATH'])
    return render_template('index.html', pretty_strings=catalog_pretty_strings)

@bp.route('/inspect/<string:catalog_raw>')
def inspect_catalog(catalog_raw):

    if catalog_raw == 'all':
        catalog = None
    elif catalog_raw not in catalog_match_strings:
        error_msg = 'Catalog name not found.'
        abort(Response(render_template('500.html', error_msg=error_msg), 500))
    else:
        catalog = catalog_match_strings[catalog_raw]

    while True:

        length = len(lslgautils.t)
        rand_index = random.randint(0, length - 1)

        if catalog is not None:
            if lslgautils.t[rand_index]['GALAXY'][:len(catalog)] == catalog:
                if lslgautils.test_footprint(rand_index):
                    break
        else:
            if lslgautils.test_footprint(rand_index):
                break
    
    return redirect(url_for('.inspect_galaxy', catalog_raw=catalog_raw, galaxy_index=rand_index))

@bp.route('/inspect/<string:catalog_raw>/<int:galaxy_index>')
def inspect_galaxy(catalog_raw, galaxy_index):

    if catalog_raw != 'all' and catalog_raw not in catalog_match_strings:
        error_msg = 'Catalog name not found.'
        abort(Response(render_template('500.html', error_msg=error_msg), 500))

    galaxy_info = lslgautils.get_lslga_tablerow(galaxy_index)

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
        rand=galaxy_index,
        info=galaxy_info,
        viewer_link = viewer_link
    )

# Other catalogs: UGC?

catalog_match_strings = {
    'ngc': 'NGC',
    'sdss': 'SDSS',
    '2mas': '2MAS',
    # 'pgc': 'PGC'
}

catalog_pretty_strings = {
    'all': '',
    'ngc': 'NGC',
    'sdss': 'SDSS',
    '2mas': '2MASS/2MASX',
    # 'pgc': 'PGC'
}

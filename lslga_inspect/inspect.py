from flask import abort, Blueprint, redirect, render_template, request, Response, url_for
import random
from . import lslga_utils

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

@bp.route('/inspect/<string:catalog_raw>/<int:galaxy_id>')
def inspect_galaxy(catalog_raw, galaxy_id):

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

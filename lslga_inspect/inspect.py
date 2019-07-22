from flask import Blueprint, url_for, redirect, render_template, request, abort, Response
from . import lslga_utils
import random

bp = Blueprint('inspect', __name__)

# TODO: return abort(500, 'This is the custom error message to be displayed.')

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
def index():
    return redirect(url_for('.inspect'))

@bp.route('/inspect')
def inspect():
    return render_template('catalog-list.html', pretty_strings=catalog_pretty_strings)

@bp.route('/inspect/<string:catalog_raw>')
def inspect_catalog(catalog_raw):

    if catalog_raw == 'all':
        catalog = None
    elif catalog_raw not in catalog_match_strings:
        error_msg = 'Catalog name not found.'
        abort(Response(render_template('500.html', error_msg=error_msg), 500))
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
    
    return redirect(url_for('.inspect_galaxy', catalog_raw=catalog_raw, galaxy_index=rand_index))

@bp.route('/inspect/<string:catalog_raw>/<int:galaxy_index>')
def inspect_galaxy(catalog_raw, galaxy_index):

    if catalog_raw != 'all' and catalog_raw not in catalog_match_strings:
        error_msg = 'Catalog name not found.'
        abort(Response(render_template('500.html', error_msg=error_msg), 500))

    galaxy_info = lslga_utils.get_lslga_tablerow(galaxy_index)

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

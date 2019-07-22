from flask import abort, Blueprint, render_template, request, Response
import requests
from PIL import Image
from io import BytesIO
from . import lslga_utils

bp = Blueprint('image', __name__)

@bp.route('/jpeg-cutout')
def jpeg_cutout():

    args = request.args

    # Throw HTTP 500 errors for specific bad URL arguments
    if not ('ra' in args and 'dec' in args):
        return abort(500, 'The ra and/or dec URL args were not passed.')
    if args['ra'] == '' or args['dec'] == '':
        return abort(500, 'The ra and/or dec URL args were empty.')
    if 'zoom' in args:
        return abort(500, 'Please use pixscale instead of zoom.')

    ra = float(args['ra'])
    dec = float(args['dec'])
    
    default_pixscale = 0.262
    if 'pixscale' in args:
        pixscale = float(args['pixscale'])
    else:
        pixscale = default_pixscale

    url = 'http://legacysurvey.org/viewer/jpeg-cutout'

    for i, (key, value) in enumerate(args.items()):
        prefix = '?' if i == 0 else '&'
        url += "{}{}={}".format(prefix, key, value)

    r = requests.get(url)
    try:
        img = Image.open(BytesIO(r.content))
    except:
        return abort(500, 'The received image could not be read.')

    lslga_utils.draw_all_ellipses(img, ra, dec, pixscale)

    return lslga_utils.get_img_response(img)

@bp.route('/lslga')
def lslga():
    
    args = request.args

    if 'num' in args:
        lslga_index = int(args['num'])
    else:
        lslga_index = 0
    
    if 'layer' in args:
        layer = str(args['layer'])
    else:
        layer = "dr8"

    rendered = lslga_utils.render_galaxy_img(lslga_index, layer=layer)

    if rendered is None:
        return abort(500, 'The LSLGA image could not be rendered (likely not in survey footprint).')
    else:
        galaxy_img, pixscale = rendered
    
    galaxy_info = lslga_utils.get_lslga_tablerow(lslga_index)
    GALAXY = galaxy_info['GALAXY']

    lslga_utils.draw_scalebar(galaxy_img, pixscale, GALAXY)
    lslga_utils.draw_galaxyname(galaxy_img, GALAXY)
    
    if 'annotation' in args:
        annotation = str(args['annotation'])
        if annotation != '':
            lslga_utils.draw_annotation(galaxy_img, annotation)

    return lslga_utils.get_img_response(galaxy_img)

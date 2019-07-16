from flask import Flask, make_response, render_template, request, abort, Response
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from astropy.table import Table
import numpy as np
import random
import lslgautils

app = Flask(__name__)

@app.route('/')
def index():
    test_url = "/jpeg-cutout?ra=352.6064&dec=0.1568&pixscale=0.3&layer=dr8&width=500&height=500"
    return render_template('index.html', test_url=test_url)

@app.route('/jpeg-cutout')
def jpeg_cutout():

    url = 'http://legacysurvey.org/viewer/jpeg-cutout'

    args = request.args

    error_str = "<!DOCTYPE HTML><title>500 Internal Server Error</title><h1>Internal Server Error</h1><p>{}</p>"

    # Throw HTTP 500 error if ra/dec are nonexistent/empty
    if not ('ra' in args and 'dec' in args):
        abort(Response(error_str.format("At least one of the <code>ra</code> and <code>dec</code> URL arguments was not passed.")))
    if args['ra'] == '' or args['dec'] == '':
        abort(Response(error_str.format("At least one of the <code>ra</code> and <code>dec</code> URL arguments was empty.")))

    ra = float(args['ra'])
    dec = float(args['dec'])

    # Throw HTTP 500 error if zoom isused
    if 'zoom' in args:
        abort(Response(error_str.format("Please use <code>pixscale</code> instead of <code>zoom</code>.")))
    
    default_pixscale = 0.262
    if 'pixscale' in args:
        if args['pixscale'] == '':
            pixscale = default_pixscale
        else:
            pixscale = float(args['pixscale'])
    else:
        pixscale = default_pixscale

    # Would be easy to add new url args here
    for i, (key, value) in enumerate(args.items()):
        prefix = '?' if i == 0 else '&'
        url += "{}{}={}".format(prefix, key, value)
            
    r = requests.get(url)
    img = Image.open(BytesIO(r.content))

    lslgautils.draw_all_ellipses(img, ra, dec, pixscale)

    return lslgautils.get_img_response(img)

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/lslga')
def lslga():
    
    if 'num' in request.args:
        lslga_index = int(request.args['num'])
    else:
        lslga_index = 0
    
    if 'layer' in request.args:
        layer = str(request.args['layer'])
    else:
        layer = "dr8"

    rendered = lslgautils.render_galaxy_img(lslga_index, layer=layer)

    if rendered is None:
        # print('-'*40 + '\n' + 'GALAXY {} COULD NOT BE RENDERED'.format(lslga_index) + '\n' + '-'*40)
        return "The galaxy image could not be rendered."
    else:
        galaxy_img, pixscale = rendered
    
    galaxy_info = lslgautils.get_lslga_tablerow(lslga_index)
    GALAXY = galaxy_info['GALAXY']

    lslgautils.draw_scalebar(galaxy_img, pixscale, GALAXY)

    return lslgautils.get_img_response(galaxy_img)

# TODO: Don't show duplicates for one session... kind of hard
# Just only show each up to 3 times until database cleared?

@app.route('/inspect')
def inspect():

    length = len(lslgautils.t)
    rand_index = random.randint(0, length - 1)

    galaxy_info = lslgautils.get_lslga_tablerow(rand_index)
    GALAXY = galaxy_info['GALAXY']

    return render_template("inspect.html", rand=rand_index, name=GALAXY)

if __name__ == "__main__":
    app.run(debug=True)

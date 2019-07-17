from flask import Flask, make_response, render_template, request, abort, Response, redirect, url_for
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
    test_urls = [
        '/gallery',
        '/inspect',
        '/test',
        '/jpeg-cutout',
        '/lslga'
    ]
    test_images = [
        "/jpeg-cutout?ra=352.6064&dec=0.1568&pixscale=0.2&layer=dr8&width=500&height=500",
        "/jpeg-cutout?ra=139.843&dec=33.743&pixscale=0.2&layer=dr8&width=500&height=500",
        "/jpeg-cutout?ra=228.385&dec=5.437&pixscale=0.3&layer=dr8&width=500&height=500"
    ]
    return render_template('index.html', test_urls=test_urls, test_images=test_images)

@app.route('/jpeg-cutout')
def jpeg_cutout():

    args = request.args

    # Throw HTTP 500 errors for specific bad URL arguments
    if not ('ra' in args and 'dec' in args):
        error_msg = 'The <code>ra</code> and/or <code>dec</code> URL args were not passed.'
        abort(Response(render_template('500.html', error_msg=error_msg), 500))
    if args['ra'] == '' or args['dec'] == '':
        error_msg = 'The <code>ra</code> and/or <code>dec</code> URL args were empty.'
        abort(Response(render_template('500.html', error_msg=error_msg), 500))
    if 'zoom' in args:
        error_msg = 'Please use <code>pixscale</code> instead of <code>zoom</code>.'
        abort(Response(render_template('500.html', error_msg=error_msg), 500))

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
        error_msg = 'The received image could not be read.'
        abort(Response(render_template('500.html', error_msg=error_msg), 500))

    lslgautils.draw_all_ellipses(img, ra, dec, pixscale)

    return lslgautils.get_img_response(img)

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/lslga')
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

    rendered = lslgautils.render_galaxy_img(lslga_index, layer=layer)

    if rendered is None:
        error_msg = 'The LSLGA image could not be rendered (likely not in survey footprint).'
        abort(Response(render_template('500.html', error_msg=error_msg), 500))
    else:
        galaxy_img, pixscale = rendered
    
    galaxy_info = lslgautils.get_lslga_tablerow(lslga_index)
    GALAXY = galaxy_info['GALAXY']

    lslgautils.draw_scalebar(galaxy_img, pixscale, GALAXY)
    lslgautils.draw_galaxyname(galaxy_img, GALAXY)
    
    if 'annotation' in args:
        annotation = str(args['annotation'])
        if annotation != '':
            lslgautils.draw_annotation(galaxy_img, annotation)

    return lslgautils.get_img_response(galaxy_img)

# TODO: Might be better to have each galaxy have sub-url, so one could go back to them?
@app.route('/inspect')
def inspect():

    args = request.args

    catalog = None
    if 'sdss' in args:
        catalog = 'SDSS'
    elif 'ngc' in args:
        catalog = "NGC"

    # Should maybe cache the bad list somehow
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

    galaxy_info = lslgautils.get_lslga_tablerow(rand_index)

    return render_template("inspect.html", rand=rand_index, info=galaxy_info)

@app.route('/test')
def toast():

    return render_template('test.html', pretty_strings=catalog_pretty_strings)

@app.route('/test/<string:catalog_raw>')
def test(catalog_raw):

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
    
    return redirect(url_for('test2', catalog_raw=catalog_raw, galaxy_index=rand_index))

@app.route('/test/<string:catalog_raw>/<int:galaxy_index>')
def test2(catalog_raw, galaxy_index):

    if catalog_raw != 'all' and catalog_raw not in catalog_match_strings:
        error_msg = 'Catalog name not found.'
        abort(Response(render_template('500.html', error_msg=error_msg), 500))

    galaxy_info = lslgautils.get_lslga_tablerow(galaxy_index)

    return render_template(
        "test-inspect.html",
        catalog_raw=catalog_raw,
        catalog_pretty=catalog_pretty_strings[catalog_raw],
        rand=galaxy_index,
        info=galaxy_info
    )

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

if __name__ == "__main__":
    app.run(debug=True)

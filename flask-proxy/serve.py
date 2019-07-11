from flask import Flask, make_response, render_template, request, abort, Response
import requests
from PIL import Image, ImageDraw
from io import BytesIO
import os
from astropy.table import Table
import numpy as np

app = Flask(__name__)

@app.route('/')
def hello():
    test_label = "Test image"
    test_url = "/jpeg-cutout?ra=352.6064&dec=0.1568&pixscale=0.3&layer=dr8&width=500&height=500"
    return render_template('index.html', test_label=test_label, test_url=test_url)

@app.route('/jpeg-cutout')
def test():
        
    url = 'http://legacysurvey.org/viewer/jpeg-cutout'
    
    # Professional debugging
    mystr = '-'*60
    def fancy_print(thing):
        print("{mystr}\n{}\n{mystr}".format(thing, mystr=mystr))
    def long_print():
        print(mystr)

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

    draw_ellipses(img, ra, dec, pixscale)

    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)

    response = make_response(img_io.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'
    return response

# Using the legacysurvey.org's json query catalog
def draw_ellipses(img, ra, dec, pixscale):

    width, height = img.size

    ralo = ra - ((width / 2) * pixscale / 3600)
    rahi = ra + ((width / 2) * pixscale / 3600)
    declo = dec - ((height / 2) * pixscale / 3600)
    dechi = dec + ((height / 2) * pixscale / 3600)

    json_url = ('http://legacysurvey.org/viewer/lslga/1/cat.json'
        '?ralo={}'
        '&rahi={}'
        '&declo={}'
        '&dechi={}'
    ).format(ralo, rahi, declo, dechi)
    
    r = requests.get(json_url).json()

    for i in range(len(r['rd'])):

        RA, DEC = r['rd'][i]
        RAD = r['radiusArcsec'][i]
        AB = r['abRatio'][i]
        PA = r['posAngle'][i]

        PA = 90 - PA

        major_axis_arcsec = RAD * 2
        minor_axis_arcsec = major_axis_arcsec * AB

        overlay_height = int(major_axis_arcsec / pixscale)
        overlay_width = int(minor_axis_arcsec / pixscale)

        overlay = Image.new('RGBA', (overlay_width, overlay_height))
        draw = ImageDraw.ImageDraw(overlay)
        box_corners = (0, 0, overlay_width, overlay_height)
        draw.ellipse(box_corners, fill=None, outline=(0, 0, 255), width=3)

        rotated = overlay.rotate(PA, expand=True)
        rotated_width, rotated_height = rotated.size

        pix_from_left = (rahi - RA) * 3600 / pixscale
        pix_from_top = (dechi - DEC) * 3600 / pixscale

        paste_shift_x = int(pix_from_left - rotated_width / 2)
        paste_shift_y = int(pix_from_top - rotated_height / 2)

        img.paste(rotated, (paste_shift_x, paste_shift_y), rotated)

# Using a local FITS catalog
def draw_ellipses_alt(img, ra, dec, pixscale):
    
    catalog_path = '../data/LSLGA-v2.0.fits'
    catalog_path = os.path.expanduser(catalog_path)
    t = Table.read(catalog_path)
    
    width, height = img.size

    ralo = ra - ((width / 2) * pixscale / 3600)
    rahi = ra + ((width / 2) * pixscale / 3600)
    declo = dec - ((height / 2) * pixscale / 3600)
    dechi = dec + ((height / 2) * pixscale / 3600)

    galaxies = []
    for galaxy in t:
        RA = galaxy['RA']
        DEC = galaxy['DEC']
        if RA > ralo and RA < rahi and DEC > declo and DEC < dechi:
            galaxies.append(galaxy)

    for galaxy in galaxies:

        print("Rendering {}".format(galaxy['GALAXY']))

        RA = galaxy['RA']
        DEC = galaxy['DEC']

        PA = galaxy['PA']
        D25 = galaxy['D25']
        BA = galaxy['BA']

        if np.isnan(PA):
            PA = 0
        if np.isnan(BA):
            BA = 1
        if np.isnan(D25):
            continue

        major_axis_arcsec = D25 * 60
        minor_axis_arcsec = major_axis_arcsec * BA

        overlay_height = int(major_axis_arcsec / pixscale)
        overlay_width = int(minor_axis_arcsec / pixscale)

        overlay = Image.new('RGBA', (overlay_width, overlay_height))
        draw = ImageDraw.ImageDraw(overlay)
        box_corners = (0, 0, overlay_width, overlay_height)
        draw.ellipse(box_corners, fill=None, outline=(0, 0, 255), width=3)

        rotated = overlay.rotate(PA, expand=True)
        rotated_width, rotated_height = rotated.size

        pix_from_left = (rahi - RA) * 3600 / pixscale
        pix_from_top = (dechi - DEC) * 3600 / pixscale

        paste_shift_x = int(pix_from_left - rotated_width / 2)
        paste_shift_y = int(pix_from_top - rotated_height / 2)

        img.paste(rotated, (paste_shift_x, paste_shift_y), rotated)

if __name__ == "__main__":
    app.run(debug=True)

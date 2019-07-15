from flask import Flask, make_response, render_template, request, abort, Response
import requests
from PIL import Image, ImageDraw, ImageFont
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

@app.route('/gallery')
def test_gallery():

    # return render_template('gallery.html')

    # Bad, because all the images are accessed twice
    # Also, code duplication is bad --> methodization
    catalog_path = '../data/LSLGA-v2.0.fits'
    catalog_path = os.path.expanduser(catalog_path)
    t = Table.read(catalog_path)

    t = t[:40]

    good_rows = []

    for i, galaxy in enumerate(t):

    # -------------------------------------------------------------------------------

        GALAXY = galaxy['GALAXY']

        RA = galaxy['RA']
        DEC = galaxy['DEC']

        PA = galaxy['PA'] # position angle (positive from north to east) [degrees]
        D25 = galaxy['D25'] # diameter in arcminutes
        BA = galaxy['BA'] # minor-to-major axis ratio

        # TODO: Determine whether these instances should just be discarded
        # assert np.isnan(PA)
        if np.isnan(PA):
            PA = 0 # 90?

        major_axis_arcsec = D25 * 60
        minor_axis_arcsec = major_axis_arcsec * BA

        semimajor_axis_arcsec = major_axis_arcsec / 2
        semiminor_axis_arcsec = minor_axis_arcsec / 2

        # Set width or height to None to have that dimension sized for aspect ratio of galaxy
        img_width = 500 # pixels
        img_height = 500 # pixels

        assert img_width is not None or img_height is not None

        img_width = int(np.round(img_width, 0)) if img_width is not None else None
        img_height = int(np.round(img_height, 0)) if img_height is not None else None

        # Determine how to frame the galaxy (not needed on cutout server)
        hspan_max = np.maximum(
            major_axis_arcsec * np.absolute(np.sin(np.radians(PA))),
            minor_axis_arcsec * np.absolute(np.cos(np.radians(PA)))
        )
        vspan_max = np.maximum(
            major_axis_arcsec * np.absolute(np.cos(np.radians(PA))),
            minor_axis_arcsec * np.absolute(np.sin(np.radians(PA)))
        )

        # A float >= 1, how much larger the image is than the galaxy
        dimension_conservatism = 3

        hspan_max *= dimension_conservatism
        vspan_max *= dimension_conservatism

        if img_width is None and img_height is not None:
            img_width = int(np.round(img_height * (hspan_max / vspan_max), 0))
            pixscale = vspan_max / img_height
        elif img_height is None and img_width is not None:
            img_height = int(np.round(img_width * (vspan_max / hspan_max), 0))
            pixscale = hspan_max / img_width
        else:
            # Compare aspect ratios
            if (hspan_max / vspan_max) > (img_width / img_height):
                pixscale = hspan_max / img_width
            else:
                pixscale = vspan_max / img_height

        # Set pixscale manually
        # pixscale = 0.8 # arcseconds/pixel, default 0.262 arcsec/pix

        major_axis_pix = major_axis_arcsec / pixscale
        minor_axis_pix = minor_axis_arcsec / pixscale

        url = (
            "http://legacysurvey.org/viewer/jpeg-cutout"
            "?ra={:.7f}"
            "&dec={:.7f}"
            "&layer=decals-dr7"
            "&pixscale={:.6f}"
            "&width={:.0f}"
            "&height={:.0f}"
        ).format(RA, DEC, pixscale, img_width, img_height)

        r = requests.get(url)

        img = Image.open(BytesIO(r.content))

        # draw_ellipses(img, RA, DEC, pixscale)

        ext = img.convert('L').getextrema()
        if ext[0] != ext[1]:
            good_rows.append(i)

    # -------------------------------------------------------------------------------

    return render_template('gallery.html', good_rows=good_rows)

@app.route('/lslga')
def lslga():
    
    if 'num' in request.args:
        lslga_num = int(request.args['num'])
    else:
        lslga_num = 0

    catalog_path = '../data/LSLGA-v2.0.fits'
    catalog_path = os.path.expanduser(catalog_path)
    t = Table.read(catalog_path)

    # TODO: This is not a good system
    galaxy = t[lslga_num]

    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    GALAXY = galaxy['GALAXY']

    RA = galaxy['RA']
    DEC = galaxy['DEC']

    PA = galaxy['PA'] # position angle (positive from north to east) [degrees]
    D25 = galaxy['D25'] # diameter in arcminutes
    BA = galaxy['BA'] # minor-to-major axis ratio

    print("GALAXY: {}".format(GALAXY))
    print("D25: {} arcmin".format(D25))
    print("PA: {}".format(PA))

    # TODO: Determine whether these instances should just be discarded
    # assert np.isnan(PA)
    if np.isnan(PA):
        PA = 0 # 90?

    major_axis_arcsec = D25 * 60
    minor_axis_arcsec = major_axis_arcsec * BA

    semimajor_axis_arcsec = major_axis_arcsec / 2
    semiminor_axis_arcsec = minor_axis_arcsec / 2

    # Set width or height to None to have that dimension sized for aspect ratio of galaxy
    img_width = 500 # pixels
    img_height = 500 # pixels

    assert img_width is not None or img_height is not None

    img_width = int(np.round(img_width, 0)) if img_width is not None else None
    img_height = int(np.round(img_height, 0)) if img_height is not None else None

    # Determine how to frame the galaxy (not needed on cutout server)
    hspan_max = np.maximum(
        major_axis_arcsec * np.absolute(np.sin(np.radians(PA))),
        minor_axis_arcsec * np.absolute(np.cos(np.radians(PA)))
    )
    vspan_max = np.maximum(
        major_axis_arcsec * np.absolute(np.cos(np.radians(PA))),
        minor_axis_arcsec * np.absolute(np.sin(np.radians(PA)))
    )

    # A float >= 1, how much larger the image is than the galaxy
    dimension_conservatism = 3

    hspan_max *= dimension_conservatism
    vspan_max *= dimension_conservatism

    if img_width is None and img_height is not None:
        img_width = int(np.round(img_height * (hspan_max / vspan_max), 0))
        pixscale = vspan_max / img_height
    elif img_height is None and img_width is not None:
        img_height = int(np.round(img_width * (vspan_max / hspan_max), 0))
        pixscale = hspan_max / img_width
    else:
        # Compare aspect ratios
        if (hspan_max / vspan_max) > (img_width / img_height):
            pixscale = hspan_max / img_width
        else:
            pixscale = vspan_max / img_height

    # Set pixscale manually
    # pixscale = 0.8 # arcseconds/pixel, default 0.262 arcsec/pix

    major_axis_pix = major_axis_arcsec / pixscale
    minor_axis_pix = minor_axis_arcsec / pixscale

    url = (
        "http://legacysurvey.org/viewer/jpeg-cutout"
        "?ra={:.7f}"
        "&dec={:.7f}"
        "&layer=decals-dr7"
        "&pixscale={:.6f}"
        "&width={:.0f}"
        "&height={:.0f}"
    ).format(RA, DEC, pixscale, img_width, img_height)

    r = requests.get(url)

    img = Image.open(BytesIO(r.content))

    # draw_ellipses(img, RA, DEC, pixscale)

    ext = img.convert('L').getextrema()
    if ext[0] == ext[1]:
        return "GALAXY NOT IN FOOTPRINT!"

    overlay_width = int(np.round(minor_axis_pix, 0))
    overlay_height = int(np.round(major_axis_pix, 0))

    overlay = Image.new('RGBA', (overlay_width, overlay_height))
    draw = ImageDraw.ImageDraw(overlay)
    box_corners = (0, 0, overlay_width, overlay_height)
    draw.ellipse(box_corners, fill=None, outline=(0, 0, 255), width=3)

    # Need expand=True, or else the overlay gets clipped when rotating
    rotated = overlay.rotate(PA, expand=True)

    rotated_width = rotated.size[0]
    rotated_height = rotated.size[1]

    paste_shift_x = int(np.round(img_width/2 - rotated_width/2, 0))
    paste_shift_y = int(np.round(img_height/2 - rotated_height/2, 0))

    img.paste(rotated, (paste_shift_x, paste_shift_y), rotated)

    draw = ImageDraw.ImageDraw(img)

    # ------------------------------------------------------------------------------------------------------------------------

    width = img_width
    height = img_height
    pix_scale = pixscale

    # --------------

    bar_offset = 15
    bar_height = 3

    bar_width_increment = 15
    desired_width_fraction = 1/8

    max_bar_width_arcsec = (img.size[0] - 2 * bar_offset) * pix_scale
    desired_bar_width_arcsec = max_bar_width_arcsec * desired_width_fraction

    while True:
        
        bar_width_arcsec = 0
        
        while bar_width_arcsec < desired_bar_width_arcsec:
            bar_width_arcsec += bar_width_increment
        # bar_width_arcsec -= bar_width_increment

        if bar_width_arcsec > max_bar_width_arcsec: # An emperical factor: max_bar_width_arcsec * 0.9
            # bar_width_increment *= 0.5
            bar_width_increment = int(bar_width_increment * 0.5)
        else:
            break

    # bar_width_arcsec = 60 # Set manually

    bar_width_pix = int(np.round(bar_width_arcsec / pix_scale, 0))

    print("Bar width: {}\nBar height: {}".format(bar_width_pix, bar_height))

    coords = (
        width - bar_offset,
        height - bar_offset, 
        width - bar_offset - (bar_width_pix - 1),
        height - bar_offset - (bar_height - 1)
    )

    draw.rectangle(coords, fill=(255, 255, 255), outline=None, width=0)

    if bar_width_arcsec % 1 == 0:
        bar_width_arcsec = int(bar_width_arcsec)

    scale_label_digits = str(bar_width_arcsec)
    scale_label_units = '"'

    '''
    bar_width_arcmin = bar_width_arcsec / 60
    if bar_width_arcmin % 1 == 0:
        scale_label_digits = str(int(bar_width_arcmin))
        scale_label_units = "'"
    elif bar_width_arcmin % 0.5 == 0:
        scale_label_digits = str(bar_width_arcmin)
        scale_label_units = "'"
    '''

    scale_label = "{}{}".format(scale_label_digits, scale_label_units)
    # font = ImageFont.load_default()
    mono_font = ImageFont.truetype(font="FreeMono", size=14)
    sans_font = ImageFont.truetype(font="FreeSans", size=14)
    serif_font = ImageFont.truetype(font="FreeSerif", size=14)

    scale_label_font = mono_font

    scale_label_width, scale_label_height = draw.textsize(scale_label, font=scale_label_font)
    scale_label_digits_width, _ = draw.textsize(scale_label_digits, font=scale_label_font)

    vert_offset = 4

    font_coords = (
        # width - bar_offset - scale_label_width,
        # width - bar_offset - (bar_width_pix)/2 - (scale_label_width)/2,
        width - bar_offset - (bar_width_pix)/2 - (scale_label_digits_width)/2,
        # width - bar_offset - bar_width_pix
        height - bar_offset - bar_height - scale_label_height - vert_offset
    )

    draw.text(
        font_coords,
        scale_label,
        font=scale_label_font,
        fill=(255, 255, 255)
    )

    galaxy_label = GALAXY
    galaxy_label_offset = 15
    galaxy_label_font = serif_font

    draw.text(
        (galaxy_label_offset, galaxy_label_offset),
        galaxy_label,
        font=galaxy_label_font,
        fill=(255, 255, 255)
    )

    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)

    response = make_response(img_io.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'
    return response
    
    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


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

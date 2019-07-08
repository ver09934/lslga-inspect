from astropy.table import Table
import os
import sys
import wget
from PIL import Image, ImageDraw

catalog_path = 'data/LSLGA-v2.0.fits'
t = Table.read(catalog_path)

test_galaxy = None

# Obtain a test galaxy
catalog = 'NGC'
galaxy_num = 19 # 3, 5, 6, 10, 14, 18!, 19
counter = 0
for i, row in enumerate(t):
    if row['GALAXY'][0:len(catalog)] == catalog:
        counter += 1
        if counter == galaxy_num:
            test_galaxy = row
            break

if test_galaxy is not None:

    GALAXY = test_galaxy['GALAXY']

    RA = test_galaxy['RA']
    DEC = test_galaxy['DEC']

    PA = test_galaxy['PA'] # position angle (positive from north to east) [degrees]
    D25 = test_galaxy['D25'] # diameter in arcminutes
    BA = test_galaxy['BA'] # minor-to-major axis ratio

    img_width = 500
    img_height = 500

    # TODO: Must insure that entire galaxy is contained in image width
    # TODO: Consider how this must differ if it is to be run on a the server
        # must obey all request parameters (could result in cut-off ellipse)
    # scale so diameter of galaxy is 50% of image width
    pix_scale = 1.5 # arcseconds/pixel, default 0.262 arcsec/pix

    diameter_arcsec = D25 * 60
    diameter_pix = diameter_arcsec / pix_scale

    semimajor_axis_length = diameter_pix / 2
    semiminor_axis_length = semimajor_axis_length * BA

    box_tl_x = (img_width / 2) - semiminor_axis_length
    box_tl_y = (img_height / 2) - semimajor_axis_length

    box_br_x = (img_width / 2) + semiminor_axis_length
    box_br_y = (img_height / 2) + semimajor_axis_length

    img_url = (
        "http://legacysurvey.org/viewer/jpeg-cutout"
        "?ra={:.4f}"
        "&dec={:.4f}"
        "&layer=decals-dr7"
        "&pixscale={}"
        "&width={:.0f}"
        "&height={:.0f}"
    ).format(RA, DEC, pix_scale, img_width, img_height)

    img_path = wget.download(img_url, 'tmp/{}.jpg'.format(GALAXY))
    print()

    print("GALAXY: {}".format(GALAXY))
    print("PA: {}".format(PA))

    img = Image.open(img_path)
    draw = ImageDraw.ImageDraw(img)

    box_corners = ((box_tl_x, box_tl_y), (box_br_x, box_br_y))
    draw.ellipse(box_corners, fill=None, outline=(0, 0, 255), width=2)

    img.save(img_path)

    img.show()

# https://github.com/legacysurvey/decals-web/blob/master/map/views.py
# See get_tile, maybe (render_into_wcs, create_scaled_image)

# https://github.com/moustakas/legacyhalos/blob/master/py/legacyhalos/html.py
# See addbar, for adding a scale bar

# TODO: Examine the galaxy zoo system and how this will integrate...
# TODO: For the dependencies build:
    # put into /usr/share (default for astrometry.net, for example)
    # could also put other stuff into the conda environment (using --prefix=/path/to/dir, for example)
    # Just make a nice, clean conda environment, not located in the directory or anything...
    # Keep the checked out code separate from the libs
# NOTE: ipython

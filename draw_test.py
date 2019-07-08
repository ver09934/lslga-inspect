from astropy.table import Table
import os
import sys
import wget
from PIL import Image, ImageDraw

catalog_path = 'data/LSLGA-v2.0.fits'
out_dir = 'tmp'

# Do some handling for relative paths, etc.
out_dir = os.path.expanduser(out_dir)
if out_dir.endswith('/'):
    out_dir  = out_dir[:-1]
if not os.path.exists(out_dir):
    os.mkdir(out_dir)
catalog_path = os.path.expanduser(catalog_path)

# Read in LSLGA catalog
t = Table.read(catalog_path)

# Obtain a test galaxy
test_galaxy = None
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

    print("GALAXY: {}".format(GALAXY))
    print("D25: {} arcmin".format(D25))
    print("PA: {}".format(PA))

    # TODO: Insure all rounding is only done at the last possible moment

    img_width = 500
    img_height = 500

    # TODO: Must insure that entire galaxy is contained in image width
    # TODO: Consider how this must differ if it is to be run on a the server
        # must obey all request parameters (could result in cut-off ellipse)
    # scale so diameter of galaxy is 50% of image width
    pix_scale = 0.8 # arcseconds/pixel, default 0.262 arcsec/pix

    diameter_arcsec = D25 * 60
    diameter_pix = diameter_arcsec / pix_scale

    semimajor_axis_length = diameter_pix / 2
    semiminor_axis_length = semimajor_axis_length * BA

    '''
    box_tl_x = int((img_width / 2) - semiminor_axis_length)
    box_tl_y = int((img_height / 2) - semimajor_axis_length)

    box_br_x = int((img_width / 2) + semiminor_axis_length)
    box_br_y = int((img_height / 2) + semimajor_axis_length)
    '''

    img_url = (
        "http://legacysurvey.org/viewer/jpeg-cutout"
        "?ra={:.4f}"
        "&dec={:.4f}"
        "&layer=decals-dr7"
        "&pixscale={}"
        "&width={:.0f}"
        "&height={:.0f}"
    ).format(RA, DEC, pix_scale, img_width, img_height)

    img_path = wget.download(img_url, '{}/{}.jpg'.format(out_dir, GALAXY))
    print()

    # IMPRECISION STARTS HERE

    overlay_width = int(2 * semiminor_axis_length)
    overlay_height = int(2 * semimajor_axis_length)

    overlay = Image.new('RGBA', (overlay_width, overlay_height))
    draw = ImageDraw.ImageDraw(overlay)

    box_corners = ((0, 0), (overlay_width, overlay_height))
    draw.ellipse(box_corners, fill=None, outline=(0, 0, 255), width=2) # Make thicker to test edge cutting
    
    tmp_width = 3
    
    fill_tmp = (0, 255, 0)
    # Edges
    draw.line((0, 0, 0, overlay.size[1]), fill=fill_tmp, width=tmp_width)
    draw.line((0, 0, overlay.size[0], 0), fill=fill_tmp, width=tmp_width)
    draw.line((0, overlay.size[1], overlay.size[0], overlay.size[1]), fill=fill_tmp, width=tmp_width)
    draw.line((overlay.size[0], 0, overlay.size[0], overlay.size[1]), fill=fill_tmp, width=tmp_width)
    # Diagonals
    '''
    draw.line((0, 0) + overlay.size, fill=fill_tmp, width=tmp_width)
    draw.line((0, overlay.size[1], overlay.size[0], 0), fill=fill_tmp, width=tmp_width)
    '''
    draw.line((overlay.size[0]/2, 0, overlay.size[0]/2, overlay.size[1]), fill=fill_tmp, width=tmp_width)
    draw.line((0, overlay.size[1]/2, overlay.size[0], overlay.size[1]/2), fill=fill_tmp, width=tmp_width)

    # TODO: First arg is angle (PA)
    # TODO: Determine what expand=True does...
    test_angle = 30
    rotated = overlay.rotate(test_angle, expand=True)

    draw = ImageDraw.ImageDraw(rotated)
    fill_tmp = (255, 0, 0)
    draw.line((0, 0, 0, rotated.size[1]), fill=fill_tmp, width=tmp_width)
    draw.line((0, 0, rotated.size[0], 0), fill=fill_tmp, width=tmp_width)
    draw.line((0, rotated.size[1], rotated.size[0], rotated.size[1]), fill=fill_tmp, width=tmp_width)
    draw.line((rotated.size[0], 0, rotated.size[0], rotated.size[1]), fill=fill_tmp, width=tmp_width)
    # Diagonals
    '''
    draw.line((0, 0) + rotated.size, fill=fill_tmp, width=tmp_width)
    draw.line((0, rotated.size[1], rotated.size[0], 0), fill=fill_tmp, width=tmp_width)
    '''
    draw.line((rotated.size[0]/2, 0, rotated.size[0]/2, rotated.size[1]), fill=fill_tmp, width=tmp_width)
    draw.line((0, rotated.size[1]/2, rotated.size[0], rotated.size[1]/2), fill=fill_tmp, width=tmp_width)

    new_bounding_box_width = rotated.size[0]
    new_bounding_box_height = rotated.size[1]
    # x, y diff created by correction for galaxy rotation
    print(new_bounding_box_width - 2*semiminor_axis_length, new_bounding_box_height - 2*semimajor_axis_length)

    paste_shift_x = int(img_width/2 - new_bounding_box_width/2)
    paste_shift_y = int(img_height/2 - new_bounding_box_height/2)

    img = Image.open(img_path)
    img.paste(rotated, (paste_shift_x, paste_shift_y), rotated)

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

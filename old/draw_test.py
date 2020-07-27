from astropy.table import Table
import os
import sys
import wget
from PIL import Image, ImageDraw
import numpy as np

catalog_path = '../data/LSLGA-v2.0.fits'
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
galaxy_num = 19
# Tests: 3, 5, 6, 10, 14, 18, 19
# Interesting: 33, 42, 49, 73, 75
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
    dimension_conservatism = 2

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

    img_url = (
        "http://legacysurvey.org/viewer/jpeg-cutout"
        "?ra={:.7f}"
        "&dec={:.7f}"
        "&layer=decals-dr7"
        "&pixscale={:.6f}"
        "&width={:.0f}"
        "&height={:.0f}"
    ).format(RA, DEC, pixscale, img_width, img_height)

    # print(img_url) # Cutout server URL
    # print(img_url.replace('/jpeg-cutout', '') + '&lslga') # Viewer URL

    img_path = wget.download(img_url, '{}/{}.jpg'.format(out_dir, GALAXY))
    print()

    # TODO: assert that image is not empty / has requested dimensions
    # Some options for checking (after img has been created):
        # assert img.size == (img_width, img_height)
        # assert img.convert('L').getextrema() != (36, 36)
        # ext = img.convert('L').getextrema(); assert ext[0] != ext[1]

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

    img = Image.open(img_path)
    img.paste(rotated, (paste_shift_x, paste_shift_y), rotated)

    img.save(img_path)
    img.show()

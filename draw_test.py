from astropy.table import Table
import os
import sys
import wget
from PIL import Image, ImageDraw
import numpy as np

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

    # TODO: Determine whether these instances should just be discarded
    # assert np.isnan(PA)
    if np.isnan(PA):
        PA = 0

    print("GALAXY: {}".format(GALAXY))
    print("D25: {} arcmin".format(D25))
    print("PA: {}".format(PA))

    major_axis_arcsec = D25 * 60
    minor_axis_arcsec = major_axis_arcsec * BA

    semimajor_axis_arcsec = major_axis_arcsec / 2
    semiminor_axis_arcsec = minor_axis_arcsec / 2

    # TODO: Option to set dimensions manually or set frame w/ same aspect ratio as galaxy - set max_dim or min_dim
    img_width = 500 # pixels
    img_height = 500 # pixels

    # TODO: Determine if a modified version of PA should be used for these calculations
    # i.e. PA = PA if PA < 90 else 180 - PA

    # Determine how to frame the galaxy (not needed on cutout server)
    vspan_max = np.maximum(
        major_axis_arcsec * np.absolute(np.cos(np.radians(PA))),
        minor_axis_arcsec * np.absolute(np.sin(np.radians(PA)))
    )
    hspan_max = np.maximum(
        major_axis_arcsec * np.absolute(np.sin(np.radians(PA))),
        minor_axis_arcsec * np.absolute(np.cos(np.radians(PA)))
    )

    dimension_conservatism = 2

    vspan_max *= dimension_conservatism
    hspan_max *= dimension_conservatism

    # Compare aspect ratios
    if (hspan_max / vspan_max) > (img_width / img_height):
        pix_scale = hspan_max / img_width
    else:
        pix_scale = vspan_max / img_height

    # pix_scale = 0.8 # arcseconds/pixel, default 0.262 arcsec/pix

    major_axis_pix = major_axis_arcsec / pix_scale
    minor_axis_pix = minor_axis_arcsec / pix_scale

    # TODO: Insure all rounding is only done at the last possible moment

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

    overlay_width = int(minor_axis_pix)
    overlay_height = int(major_axis_pix)

    overlay = Image.new('RGBA', (overlay_width, overlay_height))
    draw = ImageDraw.ImageDraw(overlay)
    box_corners = ((0, 0), (overlay_width, overlay_height))
    draw.ellipse(box_corners, fill=None, outline=(0, 0, 255), width=2)
    # TODO: Make line thicker to test edge cutting

    # TODO: Determine what expand=True does...
    rotated = overlay.rotate(PA, expand=True)

    rotated_width = rotated.size[0]
    rotated_height = rotated.size[1]

    paste_shift_x = int(img_width/2 - rotated_width/2)
    paste_shift_y = int(img_height/2 - rotated_height/2)

    img = Image.open(img_path)
    img.paste(rotated, (paste_shift_x, paste_shift_y), rotated)

    img.save(img_path)
    img.show()

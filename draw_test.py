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

    img_width = 500
    img_height = 500

    pix_scale = 0.8 # arcseconds/pixel, default 0.262 arcsec/pix

    diameter_arcsec = D25 * 60
    diameter_pix = diameter_arcsec / pix_scale

    semimajor_axis_length = diameter_pix / 2
    semiminor_axis_length = semimajor_axis_length * BA

    # TODO: Insure all rounding is only done at the last possible moment
    # TODO: For galaxy zoo catalog, must insure galaxy is conservatively contained in frame 

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

    # NOTE: IMPRECISION STARTS HERE

    overlay_width = int(2 * semiminor_axis_length)
    overlay_height = int(2 * semimajor_axis_length)

    overlay = Image.new('RGBA', (overlay_width, overlay_height))
    draw = ImageDraw.ImageDraw(overlay)

    box_corners = ((0, 0), (overlay_width, overlay_height))
    draw.ellipse(box_corners, fill=None, outline=(0, 0, 255), width=2) # Make thicker to test edge cutting

    # TODO: Determine what expand=True does...
    rotated = overlay.rotate(PA, expand=True)

    new_bounding_box_width = rotated.size[0]
    new_bounding_box_height = rotated.size[1]

    paste_shift_x = int(img_width/2 - new_bounding_box_width/2)
    paste_shift_y = int(img_height/2 - new_bounding_box_height/2)

    img = Image.open(img_path)
    img.paste(rotated, (paste_shift_x, paste_shift_y), rotated)

    img.save(img_path)

    img.show()

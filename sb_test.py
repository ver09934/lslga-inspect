from astropy.table import Table
import wget
from PIL import Image, ImageDraw, ImageFont
import numpy as np

out_dir = 'tmp'
t = Table.read('data/LSLGA-v2.0.fits')

catalog = 'NGC'
galaxy_num = 19
counter = 0
for i, row in enumerate(t):
    if row['GALAXY'][0:len(catalog)] == catalog:
        counter += 1
        if counter == galaxy_num:
            galaxy = row
            break

GALAXY = galaxy['GALAXY']
print("GALAXY: {}".format(GALAXY))

RA = galaxy['RA']
DEC = galaxy['DEC']

width = 500
height = 500

pix_scale = 0.8

img_url = (
    "http://legacysurvey.org/viewer/jpeg-cutout"
    "?ra={:.7f}"
    "&dec={:.7f}"
    "&layer=decals-dr7"
    "&pixscale={:.6f}"
    "&width={:.0f}"
    "&height={:.0f}"
).format(RA, DEC, pix_scale, width, height)

img_path = wget.download(img_url, '{}/{}.jpg'.format(out_dir, GALAXY))
print()

img = Image.open(img_path)
draw = ImageDraw.ImageDraw(img)

bar_offset = 15
bar_height = 3
bar_width_arcsec = 60
bar_width_pix = int(np.round(bar_width_arcsec / pix_scale, 0))

print("Bar width: {}\nBar height: {}".format(bar_width_pix, bar_height))

coords = (
    width - bar_offset,
    height - bar_offset, 
    width - bar_offset - (bar_width_pix - 1),
    height - bar_offset - (bar_height - 1)
)

draw.rectangle(coords, fill=(255, 255, 255), outline=None, width=0)

est_width = 0
est_height = 0

horiz_offset = 0
vert_offset = 0

font_coords = (
    width - bar_offset - est_width - horiz_offset,
    height - bar_offset - bar_height - est_height - vert_offset
)

# font=ImageFont.load_default()
draw.text(
    font_coords,
    "{}{}".format(str(bar_width_arcsec), '"'),
    font=ImageFont.truetype(font="FreeMono", size=14),
    fill=(0, 255, 00)
)

img.save(img_path)
img.show()

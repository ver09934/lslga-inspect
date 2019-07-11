from astropy.table import Table
import wget
from PIL import Image, ImageDraw

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

img.save(img_path)
img.show()

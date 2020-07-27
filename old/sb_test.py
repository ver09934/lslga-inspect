from astropy.table import Table
import wget
from PIL import Image, ImageDraw, ImageFont
import numpy as np

out_dir = 'tmp'
t = Table.read('../data/LSLGA-v2.0.fits')

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

bar_width_increment = 60
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

img.save(img_path)
img.show()

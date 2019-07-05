from astropy.table import Table
import numpy as np
import os
import sys

if len(sys.argv) != 2:
    print("Must pass path to LSLGA FITS file")
    exit(1)

catalog_path = sys.argv[1]
catalog_path = os.path.expanduser(catalog_path)
t = Table.read(catalog_path)

# Test with first several rows
t = t[:40]

indices_to_remove = []

for i, row in enumerate(t, 0):

    # Remove galaxies not in DESI footprint
    if not row['IN_DESI']:
        indices_to_remove.append(i)

    # Remove galaxies with DEC above dr7 foorprint
    dec = row['DEC']
    if dec > 30 or dec < 0:
        indices_to_remove.append(i)

# Remove list duplicates and sort in reverse orderu
indices_to_remove = list(set(indices_to_remove))
indices_to_remove.sort(reverse = True)

# Run in reverse so indices not affected by removal
for i in indices_to_remove:
    t.remove_row(i)

print(len(t))

# Generate URLs
for ra, dec in t['RA','DEC']:
    print("http://legacysurvey.org/viewer/jpeg-cutout?ra={:.4f}&dec={:.4f}&zoom=13&layer=decals-dr7".format(ra, dec))

url_list = [
    "http://legacysurvey.org/viewer/jpeg-cutout?ra={:.4f}&dec={:.4f}&zoom=13&layer=decals-dr7".format(ra, dec)
    for ra, dec in t['RA', 'DEC']
]

# for line in $(python3 read.py); do wget $line; done

from astropy.table import Table
import numpy as np
import os
import sys

# assert len(sys.argv) == 2
# catalog_path = os.path.expanduser(sys.argv[1])
catalog_path = '../data/LSLGA-v2.0.fits'

def main():
    
    t = Table.read(catalog_path)

    # test with first several rows
    # t = t[:40]

    # filter_survey_footprint(t)
    # filter_survey_footprint_alt(t)
    # gen_urls(t)
    # filter_radec(t)
    # test_pa_range(t)
    # test_id_order(t)
    testing(t)

def filter_survey_footprint(t):    

    indices_to_remove = []

    for i, row in enumerate(t):
    
        # Remove galaxies not in DESI footprint
        if not row['IN_DESI']:
            indices_to_remove.append(i)

        # Remove galaxies with DEC above dr7 foorprint
        dec = row['DEC']
        if dec > 30 or dec < 0:
            indices_to_remove.append(i)

    # Remove list duplicates and sort in reverse order
    indices_to_remove = list(set(indices_to_remove))
    indices_to_remove.sort(reverse = True)

    # Run in reverse so indices not affected by removal
    for i in indices_to_remove:
        t.remove_row(i)

    print(len(t))

def filter_survey_footprint_alt(t):

    def in_footprint(ra, dec):
        return dec < 30 and dec > 0

    good_indices = []

    for counter, row in enumerate(t, 0):

        IN_DESI = row['IN_DESI']
        RA = row['RA']
        DEC = row['DEC']

        if IN_DESI and in_footprint(RA, DEC):
            good_indices.append(counter)
    
    # Now do whatever iter is needed, only accessing the good indices
        
    print(len(good_indices))

def gen_urls(t):

    # Generate URLs
    for ra, dec in t['RA', 'DEC']:

        url = ("http://legacysurvey.org/viewer/jpeg-cutout"
            "?ra={:.7f}"
            "&dec={:.7f}"
            "&zoom=13"
            "&layer=decals-dr7"
        ).format(ra, dec)

        print(url)
        print(url.replace('/jpeg-cutout', '') + '&lslga')

def filter_radec(t):

    ralo = 228.36846888888888
    rahi = 228.40573111111112
    declo = 5.415868888888888
    dechi = 5.453131111111111

    for row in t:

        RA = row['RA']
        DEC = row['DEC']

        if RA > ralo and RA < rahi and DEC > declo and DEC < dechi:
            print("GALAXY: {} PA: {}".format(row['GALAXY'], row['PA']))

def test_pa_range(t):

    print("Testing >= 180 / <= 0")
    for row in t:
        if float(row['PA']) >= 180 or float(row['PA']) <= 0:
            print("PA: {} GALAXY: {}".format(row['PA'], row['GALAXY']))

    print("Testing > 180 / < 0")
    for row in t:
        if float(row['PA']) > 180 or float(row['PA'] < 0):
            print("PA: {} GALAXY: {}".format(row['PA'], row['GALAXY']))

def test_id_order(t):

    for row in t:
        print(row['LSLGA_ID'])

def testing(t):

    t = t[:40]
    print(t.info)

if __name__ == '__main__':
    main()
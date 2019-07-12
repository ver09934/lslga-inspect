from astropy.table import Table
import numpy as np
import os
import sys

catalog_path = 'data/LSLGA-v2.0.fits'

def main():
    
    t = Table.read(catalog_path)

    good_indices = []

    for counter, row in enumerate(t, 0):

        IN_DESI = row['IN_DESI']
        RA = row['RA']
        DEC = row['DEC']

        if IN_DESI and in_footprint(RA, DEC):
            good_indices.append(counter)
        
    print(len(good_indices))

def in_footprint(ra, dec):
    return dec < 30 and dec > 0

if __name__ == '__main__':
    main()

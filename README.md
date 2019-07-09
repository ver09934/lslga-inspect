# lslga-inspect
Inspecting large galaxies in the [Legacy Surveys](http://legacysurvey.org/), using the [Legacy Survey Large Galaxy Atlas](https://github.com/moustakas/LSLGA).

## Data
The files used can be obtained as follows:
```bash
$ mkdir data && cd data # The data directory is gitignored
$ wget http://www.sos.siena.edu/~jmoustakas/tmp/LSLGA-v2.0.fits
$ wget http://www.sos.siena.edu/~jmoustakas/tmp/README
```

## Dependencies
An environment can be created with Anaconda:
```bash
$ conda create --name lslga-inspect python=3 numpy astropy pillow wget
$ conda activate lslga-inspect
```

<!---
TODO:
- May want to add a requirements.txt file instead of listing packages
- Building deps
    - put into /usr/share (default for astrometry.net, for example)
    - could also put other stuff into the conda environment (using --prefix=/path/to/dir, for example)
    - Just make a nice, clean conda environment, not located in the directory or anything...
    - Keep the checked out code separate from the libs
- Rendering ellipses on server
    - https://github.com/legacysurvey/decals-web/blob/master/map/views.py
    - See get_tile, maybe (render_into_wcs, create_scaled_image)
- Rendering scale bar
    - https://github.com/moustakas/legacyhalos/blob/master/py/legacyhalos/html.py
    - See addbar, for adding a scale bar
    - May want to add text as well
- Examine the galaxy zoo system and how this will integrate...
    - Look into SSL/TLS issue...
--->

# lslga-inspect
Inspecting large galaxies in the [Legacy Surveys](http://legacysurvey.org/), using the [Legacy Survey Large Galaxy Atlas](https://github.com/moustakas/LSLGA).

## Data
The files used can be obtained as follows:
```bash
$ mkdir data && cd data # The data directory is gitignored
$ wget http://www.sos.siena.edu/~jmoustakas/tmp/LSLGA-v2.0.fits
$ wget http://www.sos.siena.edu/~jmoustakas/tmp/README
```

# flask-proxy
A flask application that grabs cutout images from the legacysurvey server and draws LSLGA galaxies on them.

## Dependencies
An environment can be created with Anaconda:
```bash
$ conda create --name lslga-inspect python=3 numpy astropy pillow wget flask requests
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

<!---
New TODO:
- In read.py, methodize all the separate little tests
    - perhaps pass the table object in
    - Make a main method
    - This will reduce the amount of commented stuff and make it easier to re-run tests
- Features to add to draw_test.py (should also focus on further methodizing this file, perhaps on a separate branch)
    - May want to include some of the things written for the decals-web annotator
    - May want to break the different methods into separate files
    - Should rename some of the now-more-developed files to give a better indication of what they do
- Make the decals-web annotator use the URL arguments
--->

<!---
TODO:
- Have two separate methods for getting the LSLGA info:
    - Using the LSLGA fits catalog
    - Using the legacysurvey.org/viewer/lslga/1/cat/json?ralo=... service
    - Each return the same data format for simplicity of switching, or something like that

# FLASK_APP=test.py FLASK_ENV=development FLASK_DEBUG=1 flask run
# while true; do python3 serve.py; sleep 1; done

TODO: For large images, there is a lot of error!
This needs to be fixed, unless we will only ever be using relatively zoomed-in images
--->

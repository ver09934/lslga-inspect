# lslga-inspect
A tool to allow for the visual inspection of large galaxies in the [Legacy Surveys](http://legacysurvey.org/), using the [Legacy Survey Large Galaxy Atlas](https://github.com/moustakas/LSLGA) to provide a list of galaxies with coordinates and other information, and using the [DECaLS-web](https://github.com/legacysurvey/decals-web) jpeg cutout server to provide imagery. The flask application displays the images to a user and draws ellipses for the LSLGA galaxies on them.

## Data
The catalog can be built using the code found in the [LSLGA repository](https://github.com/moustakas/LSLGA), but it can also be obtained (at least for the time being) as follows:
```bash
$ mkdir -p instance && cd instance
$ wget http://www.sos.siena.edu/~jmoustakas/tmp/LSLGA-v2.0.fits
```

## Dependencies
An environment with all the neccesary dependencies can be created with Anaconda:
```bash
$ conda create --name lslga-inspect python=3 numpy astropy pillow flask requests sqlite3
$ conda activate lslga-inspect
```

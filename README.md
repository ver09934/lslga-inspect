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
$ conda create --name lslga-inspect python=3 astropy wget Pillow
```
<!---
TODO: May want to add a requirements.txt file instead of listing packages
--->
# lslga-inspect
A tool to allow for the visual inspection of large galaxies in the [Legacy Surveys](http://legacysurvey.org/), using the [Legacy Survey Large Galaxy Atlas](https://github.com/moustakas/LSLGA) to provide a list of galaxies with coordinates and other information, and using the [DECaLS-web](https://github.com/legacysurvey/decals-web) jpeg cutout server to provide imagery. The flask application displays the images to a user and draws ellipses for the LSLGA galaxies on them. The user can submit whether there are any problems with the image and ellipse, and their response is recorded and stored in a SQLite database.

## Data
The catalog can be built using the code found in the [LSLGA repository](https://github.com/moustakas/LSLGA), but it can also be obtained (at least for the time being) as follows:
```bash
$ mkdir -p instance && cd instance
$ wget http://www.sos.siena.edu/~jmoustakas/tmp/LSLGA-v2.0.fits
```

## Dependencies
An environment with the neccesary dependencies can be created with Anaconda:
```bash
$ conda create --name lslga-inspect python=3 numpy astropy pillow flask requests
$ conda activate lslga-inspect
```
<!--- sqlite3 is generally included in python by default --->

## Running (Development)
```bash
$ export FLASK_APP=lslga_inspect
$ export FLASK_ENV=development
$ flask init-db
$ flask run
```

## Running (Production)
The application can be run using `apache2` with `mod_wsgi`. On Ubuntu/Debian systems, the neccesary packages can be installed by running
```bash
$ sudo apt install apache2 libapache2-mod-wsgi-py3
```

<!--- Is `apache2-dev` needed? --->

An example virtualhost file (using a virtual environment) is shown below.
```apache
<VirtualHost *:80>
    ServerName example.com
    # Don't include the python-home option if packages are installed globally
    WSGIDaemonProcess lslga_inspect python-home=/path/to/venv
    WSGIScriptAlias / /path/to/lslga-inspect/lslga_inspect.wsgi
    <Directory /path/to/lslga-inspect>
        WSGIProcessGroup lslga_inspect
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
        Order deny,allow
        Allow from all
    </Directory>
    LogLevel warn
    ErrorLog ${APACHE_LOG_DIR}/lslga-error.log
    CustomLog ${APACHE_LOG_DIR}/lslga-access.log combined
</VirtualHost>
```

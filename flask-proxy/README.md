# flask-proxy
A flask application that grabs cutout images from the legacysurvey server and draws LSLGA galaxies on them.

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
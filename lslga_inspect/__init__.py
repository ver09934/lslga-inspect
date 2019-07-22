from flask import Flask

def create_app():
    
    app = Flask(__name__, instance_relative_config=True)

    # TODO: Examine config options,
    # perhaps add default config=None arg to create_app
    # https://hackersandslackers.com/configuring-your-flask-application/

    app.config.from_pyfile('config.cfg')

    from . import inspect, image

    app.register_blueprint(inspect.bp)
    app.register_blueprint(image.bp)

    return app

# To run (dev): FLASK_APP=lslga_inspect FLASK_ENV=development flask run
# TODO: Update README with newest flask application info
# TODO: Add docstrings
# TODO: Remove TODOs from README
# TODO: Figure out how to use base templates in Jinja
# TODO: Incorporate changes from decals-web into these image methods
# TODO: Run 'ag TODO' and complete all TODOs
# TODO: Remove unneeded imports
# TODO: Use LSLGA_ID in URLs instead of FITS table index
# TODO: Use a visible section in README for TODOs
# TODO: Transfer ownership to legacysurvey as requested by Dr. Moustakas
# TODO: Put flask imports in alphabetical order
# TODO: Figure out a better way to do things than returning None and HTTP errors
# TODO: Check handling of if PA, BA, D25, etc. are NaN

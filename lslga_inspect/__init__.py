from flask import Flask
import os

def create_app():
    
    app = Flask(__name__, instance_relative_config=True)

    # TODO: Examine config options,
    # perhaps add default config=None arg to create_app
    # https://hackersandslackers.com/configuring-your-flask-application/

    app.config.from_pyfile('config.cfg')

    from . import lslga_utils
    lslga_utils.init_t(app)

    from . import inspect, image
    app.register_blueprint(inspect.bp)
    app.register_blueprint(image.bp)

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    from . import db
    db.init_app(app)

    from . import user
    app.register_blueprint(user.bp)

    return app

# export FLASK_APP=lslga_inspect && export FLASK_ENV=development
# To run (dev): FLASK_APP=lslga_inspect FLASK_ENV=development flask run

# TODO: Run 'ag TODO' and complete all TODOs
# TODO: Figure out how to use base templates in Jinja
# TODO: Transfer ownership to legacysurvey as requested by Dr. Moustakas
# TODO: Add docstrings
# TODO: Figure out a better way to do things than returning None and HTTP errors
# TODO: Make drawing look better by sampling larger and downscaling?
# https://stackoverflow.com/questions/16640338/python3-pil-pillow-draw-pieslice-bad-arc

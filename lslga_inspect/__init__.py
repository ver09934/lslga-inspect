from flask import Flask
import os

def create_app():
    
    app = Flask(__name__, instance_relative_config=True)

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

# ------------------------- TODO: Move these TODOs into README -------------------------

# --- /lslga_inspect/__init__.py ---
# TODO: Examine config options, perhaps add default config=None arg to create_app
    # More info: https://hackersandslackers.com/configuring-your-flask-application/

# --- /lslga_inspect/lslga_utils.py ---
# TODO: Fixed margin instead of ratio for LSLGA images
# TODO: See the method 'query_lslga_radecbox' to get a better way to find overlapping galaxies
    # https://github.com/legacysurvey/decals-web/blob/master/map/cats.py
# TODO: Perhaps just do away with pixscale option entirely...
    # Then, just make dimconservatism options more flexible

# --- /lslga_inspect/inspect.py ---
# TODO: In redirect after form submission, do something better than the current solution?
# TODO: Add options for ordered or unordered, with a back arrow in both cases...
# TODO: Might as well record the subset identifier string in database when an inspection is made...
# TODO: Have the 'set complete' page display a list of links to all inspected galaxies
    # Figure out how to handle forwards/backwards buttons and update button when the
    # user goes back to a galaxy from here...
    # Should also make an improved inspection list page for the user, related/same page as this
    # Also need to make an easy way to get the inspection data (download as a JSON/CSV/FITS file?)
# TODO: Add forwards/backwards buttons based on chronology of current set

# --- general ---
# TODO: Transfer ownership to legacysurvey as requested by Dr. Moustakas
# TODO: Figure out a better way to do things than returning None and HTTP errors
# TODO: Make drawing look better by sampling larger and downscaling?
    # https://stackoverflow.com/questions/16640338/python3-pil-pillow-draw-pieslice-bad-arc
# TODO: Have backwards and forwards arrow to navigate through user's history
# TODO: Have a counter to show how far through the set the user is...
# TODO: Cleanup, comment, and add docstrings (use functools wraps for any annotations)
    # Particularly in /lslga_inspect/user.py
# Investigate requirements file options
    # conda env export > environment.yml, conda env create -f environment.yml (see conda docs)
    # https://tdhopper.com/blog/my-python-environment-workflow-with-conda/
# TODO: Complete the meta-TODO in the heading (that makes this TODO a meta-meta-TODO)
    # TODO: Continue making increasingly meta TODOs until someone finds out and gets angry

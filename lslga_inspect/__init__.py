from flask import Flask

def create_app(config=None):
    
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile('config.cfg')

    from . import users, inspect, image

    users.init_app(app)
    inspect.init_app(app)
    image.init_app(app)

    return app

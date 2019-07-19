from . import routes

def init_app(app):
    app.register_blueprint(routes.bp)

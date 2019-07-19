from flask import Blueprint

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/adduser')
def register():
    return 'This is the auth page.'

@bp.route('/login')
def login():
    return 'This is the login page.'

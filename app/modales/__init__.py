from flask import Blueprint

blueprint = Blueprint(
    'modales_blueprint',
    __name__,
    url_prefix='/modales',
    template_folder='templates',
    static_folder='static'
)

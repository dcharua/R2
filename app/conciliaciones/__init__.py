from flask import Blueprint

blueprint = Blueprint(
    'conciliacion_blueprint',
    __name__,
    url_prefix='/conciliaciones',
    template_folder='templates',
    static_folder='static'
)

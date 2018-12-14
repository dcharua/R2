from flask import Blueprint

blueprint = Blueprint(
    'ingresos_blueprint',
    __name__,
    url_prefix='/ingresos',
    template_folder='templates',
    static_folder='static'
)

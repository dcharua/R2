from flask import Blueprint

blueprint = Blueprint(
    'nomina_blueprint',
    __name__,
    url_prefix='/nomina',
    template_folder='templates',
    static_folder='static'
)

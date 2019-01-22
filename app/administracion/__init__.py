from flask import Blueprint

blueprint = Blueprint(
    'administracion_blueprint',
    __name__,
    url_prefix='/administracion',
    template_folder='templates',
    static_folder='static'
)

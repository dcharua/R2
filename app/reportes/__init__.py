from flask import Blueprint

blueprint = Blueprint(
    'egresos_blueprint',
    __name__,
    url_prefix='/egresos',
    template_folder='templates',
    static_folder='static'
)

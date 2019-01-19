from app.modales import blueprint
from flask import render_template, request
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager



@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')
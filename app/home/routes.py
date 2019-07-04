from app.home import blueprint
from flask import render_template
from flask_login import login_required
import pandas as pd

import pyodbc


@blueprint.route('/index')
@login_required
def index():
    #df = connect_mysql()
    #df.to_csv('tst.csv',sep=',')
    return render_template('index.html')


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')

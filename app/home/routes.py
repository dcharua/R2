from app.home import blueprint
from flask import render_template
from flask_login import login_required
import pandas as pd

import pyodbc

def connect_mysql():

    driver = '/usr/local/lib/libmsodbcsql.13.dylib'
    driver = '{ODBC Driver 13 for SQL Server}'
    
    cnxn = pyodbc.connect(
                          "Server=shoesclothing.net;"
                          "Database=Gez_pruebas;"
                          "uid={user_id};pwd={password}")
    
    
    df = pd.read_sql_query('select TOP 5 * from mov_vtasdevcli', cnxn)
    return df

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

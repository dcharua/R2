from flask import Flask, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from logging import basicConfig, DEBUG, getLogger, StreamHandler
from os import path, environ
import pandas as pd
import pymysql
import pyodbc


db = SQLAlchemy()
login_manager = LoginManager()



def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('base', 'home', 'ingresos', 'egresos', 'conciliaciones', 'nomina','administracion', 'modales'):
        module = import_module('app.{}.routes'.format(module_name))

        app.register_blueprint(module.blueprint)


    con=pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com;database=gez_pruebas;uid=gezsa001;pwd=gez9105ru2")    
    cur=con.cursor()   
    cur.execute("select * from colores where coldescripcion like '%NEGR%' ORDER BY COLNUMERO") 
#    for row in cur:
#        print(row.colnumero,row.coldescripcion)


def configure_database(app):
    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def configure_logs(app):
    basicConfig(filename='error.log', level=DEBUG)
    logger = getLogger()
    logger.addHandler(StreamHandler())


def create_app(config):
    app = Flask(__name__, static_folder='base/static')
    #app.config.from_object(config)
    app.config.from_mapping(
        SECRET_KEY=environ.get('KEY'),
        DEBUG=True,
        LOGIN_DISABLED = True,
        #SQLALCHEMY_DATABASE_URI ="mysql+pymysql://%s:%s@%s/%s" %(environ.get('DB_USER'), environ.get('DB_PASSWORD'), environ.get('DB_ADDRESS'), environ.get('DB_NAME'))
    )
    #print('app/__init__.py heree')
    #print(str(app))
    db = SQLAlchemy()
    login_manager = LoginManager()
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app

from flask import Flask, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from logging import basicConfig, DEBUG, getLogger, StreamHandler
from os import path, environ
import os
import pandas as pd
import pymysql
import pyodbc
import urllib
import sqlalchemy

db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('base', 'home', 'ingresos', 'egresos', 'conciliaciones', 'nomina','administracion', 'modales'):
        module = import_module('app.{}.routes'.format(module_name))

        app.register_blueprint(module.blueprint)



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
    app.config.from_object(config)
    app.config.from_mapping(
    #SECRET_KEY=environ.get('KEY'),

    SECRET_KEY = os.urandom(32),
    DEBUG=True,
    LOGIN_DISABLED = True,
    SQLALCHEMY_TRACK_MODIFICATIONS = True,
    #SQLALCHEMY_DATABASE_URI ="mssql+pyodbc://%s:%s@%s/%s?driver=ODBC+Driver+17+for+SQL+Server" %(environ.get('DB_USER'), environ.get('DB_PASSWORD'), environ.get('DB_ADDRESS'), environ.get('DB_NAME'))
    #SQLALCHEMY_DATABASE_URI ="mysql+pymysql://%s:%s@%s/%s" %(environ.get('DB_USER'), environ.get('DB_PASSWORD'), environ.get('DB_ADDRESS'), environ.get('DB_NAME'))
    # Para Adrian
    SQLALCHEMY_DATABASE_URI ="mysql+pymysql://%s:%s@%s/%s" %('root','Adri*83224647', 'localhost','R2')

        
    )

    db = SQLAlchemy(app)
    login_manager = LoginManager()
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    
    return app

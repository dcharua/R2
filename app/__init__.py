from flask import Flask, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from logging import basicConfig, DEBUG, getLogger, StreamHandler
from os import path, environ
import pandas as pd
import pymysql

db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('base', 'home', 'ingresos', 'egresos', 'conciliaciones', 'nomina'):
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
    #app.config.from_object(config)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DEBUG=True,
        LOGIN_DISABLED = True,
        
        #SQLALCHEMY_DATABASE_URI ='mysql+pymysql://gezsa001:gez9105ru2@dodder.arvixe.com/Gez_pruebas'
    )
    db = SQLAlchemy()
    login_manager = LoginManager()
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app


#from flask_sqlalchemy import SQLAlchemy
#
#app = Flask(__name__, static_folder='base/static')
##app.config.from_object(config)
#app.config.from_mapping(
#    SECRET_KEY='dev',
#    DEBUG=True,
#    LOGIN_DISABLED = True,
#    
#    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://gezsa001:gez9105ru2@shoesclothing.net/Gez_pruebas'
#)
#db = SQLAlchemy()
#
#
#Error:
#    
#OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on 'shoesclothing.net' (timed out)")

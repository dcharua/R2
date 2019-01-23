from app.administracion import blueprint
from flask import render_template, request
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
import pyodbc
import pandas as pd

import sys 
import os
sys.path.append(os.path.abspath("./app"))
import db_utils as db


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')

@blueprint.route('/clientes', methods=['GET', 'POST'])
def clientes():
    
    
    formaPago = list(['Banamex','Santander','BBVA'])
    vendor = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    proveedor = list(['sub_categoria_1','sub_categoria_2','sub_categoria_3','sub_categoria_4','sub_categoria_5'])
    categoria = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    concepto= list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    user_inputs = dict(request.form)
    print(user_inputs)
        
    
    cur = db.connect_to_db("select * from colores where coldescripcion like '%NEGR%' ORDER BY COLNUMERO")
    print(type(cur))
     


    return render_template("clientes.html",
                           navbar_data_capture = 'active',
                           title = "Registro de Egresos",
                           formaPago = formaPago,
                           vendor = vendor,
                           proveedor = proveedor,
                           categoria = categoria,
                           concepto = concepto,
                           velocity_max = 1)
#
#    
#@blueprint.route('beneficiarios', methods=['GET', 'POST'])
#def beneficiarios():
#    formaPago = list(['Banamex','Santander','BBVA'])
#
#    user_inputs = dict(request.form)
#    print(user_inputs)
#    return render_template("beneficiarios.html",
#                           navbar_data_capture = 'active',
#                           title = "Registro de Egresos",
#                           formaPago = formaPago,
#                           vendor = vendor,
#                           proveedor = proveedor,
#                           categoria = categoria,
#                           concepto = concepto,
#                           velocity_max = 1)
#    
#    
#@blueprint.route('cuentas', methods=['GET', 'POST'])
#def cuentas():
#    formaPago = list(['Banamex','Santander','BBVA'])
#    vendor = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
#    proveedor = list(['sub_categoria_1','sub_categoria_2','sub_categoria_3','sub_categoria_4','sub_categoria_5'])
#    categoria = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
#    concepto= list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
#    user_inputs = dict(request.form)
#    print(user_inputs)
#
#    return render_template("cuentas.html",
#                           navbar_data_capture = 'active',
#                           title = "Registro de Egresos",
#                           formaPago = formaPago,
#                           vendor = vendor,
#                           proveedor = proveedor,
#                           categoria = categoria,
#                           concepto = concepto,
#                           velocity_max = 1)

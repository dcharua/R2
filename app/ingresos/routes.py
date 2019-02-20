from app.ingresos import blueprint
from flask import render_template, request
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager



@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('/capturar_ingreso', methods=['GET', 'POST'])
def captura_ingresos():
    #import df_to_table as df_to_table
    
    formaPago = list(['Banamex','Santander','BBVA'])
    vendor = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    proveedor = list(['sub_categoria_1','sub_categoria_2','sub_categoria_3','sub_categoria_4','sub_categoria_5'])
    categoria = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    concepto= list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
   
    
    user_inputs = dict(request.form)
    print(user_inputs)
    
    #a = df_to_table.df_to_table(list(1))
    #print(a)

    return render_template("capturar_ingreso.html",
                           navbar_data_capture = 'active',
                           title = "aaaRegistro de ingresos",
                           formaPago = formaPago,
                           vendor = vendor,
                           proveedor = proveedor,
                           categoria = categoria,
                           concepto = concepto,
                           velocity_max = 1)




@blueprint.route('/ingresos_tiendas', methods=['GET', 'POST'])
def ingresos_tiendas():
    #import df_to_table as df_to_table
    
    formaPago = list(['Banamex','Santander','BBVA'])
    vendor = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    proveedor = list(['sub_categoria_1','sub_categoria_2','sub_categoria_3','sub_categoria_4','sub_categoria_5'])
    categoria = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    concepto= list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
   
    
    user_inputs = dict(request.form)
    print(user_inputs)
    
    #a = df_to_table.df_to_table(list(1))
    #print(a)

    return render_template("ingresos_tiendas.html",
                           navbar_data_capture = 'active',
                           title = "aaaRegistro de ingresos",
                           formaPago = formaPago,
                           vendor = vendor,
                           proveedor = proveedor,
                           categoria = categoria,
                           concepto = concepto,
                           velocity_max = 1)
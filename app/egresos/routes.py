from app.egresos import blueprint
from flask import render_template, request
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager



@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')

@blueprint.route('capturar_egreso', methods=['GET', 'POST'])
def captura_gasto():
    formaPago = list(['Banamex','Santander','BBVA'])
    vendor = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    proveedor = list(['sub_categoria_1','sub_categoria_2','sub_categoria_3','sub_categoria_4','sub_categoria_5'])
    categoria = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    concepto= list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    user_inputs = dict(request.form)
    print(user_inputs)

    return render_template("capturar_egreso.html",
                           navbar_data_capture = 'active',
                           title = "Registro de Egresos",
                           formaPago = formaPago,
                           vendor = vendor,
                           proveedor = proveedor,
                           categoria = categoria,
                           concepto = concepto,
                           velocity_max = 1)

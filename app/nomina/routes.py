from app.nomina import blueprint
from flask import render_template, request
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager, db_gerardo



@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')

@blueprint.route('/ver_empleados')
@login_required
def ver_empleados():
    cur=db_gerardo.cursor()
    sql = "select * from empleados JOIN puestos pues_descripcion ON empleado.c_puesto = puestos.id"
    cur.execute(sql)
    return render_template('ver_empleados.html',
                            empleados=cur)

@blueprint.route('/capturar_conciliacion', methods=['GET', 'POST'])
def capturar_nomina():
    formaPago = list(['Banamex','Santander','BBVA'])
    vendor = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    proveedor = list(['sub_categoria_1','sub_categoria_2','sub_categoria_3','sub_categoria_4','sub_categoria_5'])
    categoria = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    concepto= list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    user_inputs = dict(request.form)
    print(user_inputs)

    return render_template("capturar_nomina.html",
                           navbar_data_capture = 'active',
                           title = "Registro de Nomina",
                           formaPago = formaPago,
                           vendor = vendor,
                           proveedor = proveedor,
                           categoria = categoria,
                           concepto = concepto,
                           velocity_max = 1)

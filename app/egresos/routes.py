from app.egresos import blueprint
from flask import render_template, request
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.egresos.models import Egresos, DetallesEgreso
from datetime import date

@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')

@blueprint.route('capturar_egreso', methods=['GET', 'POST'])
def capturar_egreso():
    if request.form:
        data = request.form
        montos = list(map(int, data.getlist("monto")))
        monto_total = sum(montos)
        print(data)
        egreso = Egresos(beneficiario=data["beneficiario"], fecha_vencimiento=data["fecha_vencimiento"], 
        fecha_programada_pago=data["fecha_programada_pago"], numero_documento=data["numero_documento"],
        monto_total=monto_total, referencia=data["referencia"], empresa=data["empresa"], comentario=data["comentario"])
        for i in range(len(data.getlist("monto"))):
            detalle = DetallesEgreso(centro_negocios=data.getlist("centro_negocios")[i], proveedor=data.getlist("proveedor")[i],
            categoria=data.getlist("categoria")[i], concepto=data.getlist("concepto")[i], monto=data.getlist("monto")[i], 
            numero_control=data.getlist("numero_control")[i], descripcion=data.getlist("descripcion")[i])
            egreso.detalles.append(detalle)
        db.session.add(egreso)
        db.session.commit()

    #db.session.add(egreso)
    #db.session.commit()
    formaPago = list(['Banamex','Santander','BBVA'])
    vendor = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    proveedor = list(['sub_categoria_1','sub_categoria_2','sub_categoria_3','sub_categoria_4','sub_categoria_5'])
    categoria = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    concepto= list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    

    return render_template("capturar_egreso.html",
                           navbar_data_capture = 'active',
                           title = "Registro de Egresos",
                           formaPago = formaPago,
                           vendor = vendor,
                           proveedor = proveedor,
                           categoria = categoria,
                           concepto = concepto,
                           velocity_max = 1)

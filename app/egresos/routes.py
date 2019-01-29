from app.egresos import blueprint
from flask import render_template, request
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.egresos.models import Egresos, DetallesEgreso, Pagos, Beneficiarios
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
        if ('pagado' in data):
            if ('conciliado_check' in data):
                conciliado = True
                refrencia_conciliacion = data["referencia_conciliacion"]
            else:
                 conciliado = False    
                 refrencia_conciliacion = ""
            pago = Pagos(forma_pago = data["forma_pago"], referencia_pago = data["forma_pago"],fecha_pago = data["fecha_pago"], conciliado = conciliado, 
            referencia_conciliacion= refrencia_conciliacion, empresa = data["empresa"], monto_total = data["monto_pagado"], comentario = data["comentario_pago"], beneficiario_id=1)        
            egreso.pagos.append(pago)
        db.session.add(egreso)
        db.session.commit()


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
                           concepto = concepto)


@blueprint.route('cuentas_por_pagar', methods=['GET', 'POST'])
def cuentas_por_pagar():
    egresos = Egresos.query.all()
    return render_template("cuentas_por_pagar.html", egresos=egresos)

@blueprint.route('/perfil_egreso/<int:egreso_id>', methods=['GET', 'POST'])
def perfil_egreso(egreso_id):
    egreso = Egresos.query.get(egreso_id)
    pagos = Pagos.query.join(Egresos.pagos, Beneficiarios).filter(Egresos.id == egreso_id)
    # No es eficiente muchos queries buscar como hacerlo en el query de arriba
    for pago in pagos:
        pago.beneficiario = Beneficiarios.query.get(pago.beneficiario_id)

    detalles = DetallesEgreso.query.filter(DetallesEgreso.egreso_id == egreso_id)

    return render_template("perfil_egreso.html", egreso=egreso, pagos=pagos, detalles=detalles)
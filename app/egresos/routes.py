from app.egresos import blueprint
from flask import render_template, request
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.egresos.models import *
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
        egreso = Egresos(beneficiario_id=data["beneficiario"], fecha_vencimiento=data["fecha_vencimiento"], 
        fecha_programada_pago=data["fecha_programada_pago"], numero_documento=data["numero_documento"],
        monto_total=monto_total, referencia=data["referencia"], empresa_id=data["empresa"], comentario=data["comentario"])
        for i in range(len(data.getlist("monto"))):
            detalle = DetallesEgreso(centro_negocios_id=data.getlist("centro_negocios")[i], proveedor_id=data.getlist("proveedor")[i],
            categoria_id=data.getlist("categoria")[i], concepto_id=data.getlist("concepto")[i], monto=data.getlist("monto")[i], 
            numero_control=data.getlist("numero_control")[i], descripcion=data.getlist("descripcion")[i])
            egreso.detalles.append(detalle)
        if ('pagado' in data):
            if ('conciliado_check' in data):
                conciliado = True
                refrencia_conciliacion = data["referencia_conciliacion"]
            else:
                 conciliado = False    
                 refrencia_conciliacion = ""
            pago = Pagos(forma_pago_id = data["forma_pago"], cuenta_id= data["cuenta_banco"], referencia_pago = data["forma_pago"],fecha_pago = data["fecha_pago"], conciliado = conciliado, 
            referencia_conciliacion= refrencia_conciliacion,  monto_total = data["monto_pagado"], comentario = data["comentario_pago"], beneficiario_id=1)        
            egreso.pagos.append(pago)
        db.session.add(egreso)
        db.session.commit()

    beneficiarios = Beneficiarios.query.all()
    empresas= Empresas.query.all()
    centros_negocios = CentrosNegocio.query.all()
    proveedores = beneficiarios
    categorias = Categorias.query.all()
    conceptos = Conceptos.query.all()
    cuentas_banco = Cuentas.query.all()
    formas_pago = FormasPago.query.all()


    return render_template("capturar_egreso.html",
                           navbar_data_capture = 'active',
                           title = "Registro de Egresos",
                           beneficiarios = beneficiarios,
                           empresas = empresas,
                           centros_negocios = centros_negocios,
                           proveedores = proveedores,
                           categorias = categorias,
                           conceptos = conceptos,
                           cuentas_banco=cuentas_banco,
                           formas_pago = formas_pago)


@blueprint.route('cuentas_por_pagar', methods=['GET', 'POST'])
def cuentas_por_pagar():
    egresos = Egresos.query.all()
    for egreso in egresos:
        egreso.beneficiario = Beneficiarios.query.get(egreso.beneficiario_id)
    return render_template("cuentas_por_pagar.html", egresos=egresos)

@blueprint.route('/perfil_egreso/<int:egreso_id>', methods=['GET', 'POST'])
def perfil_egreso(egreso_id):
    egreso = Egresos.query.get(egreso_id)
    egreso.beneficiario= Beneficiarios.query.get(egreso.beneficiario_id)
    egreso.empresa = Empresas.query.get(egreso.empresa_id)
    pagos = Pagos.query.join(Egresos.pagos, Beneficiarios).filter(Egresos.id == egreso_id)
    # No es eficiente muchos queries buscar como hacerlo en el query de arriba
    for pago in pagos:
        pago.beneficiario = Beneficiarios.query.get(pago.beneficiario_id)
        pago.cuenta_banco = Cuentas.query.get(pago.cuenta_id)

    detalles = DetallesEgreso.query.filter(DetallesEgreso.egreso_id == egreso_id)
    for detalle in detalles:
        detalle.proveedor = Beneficiarios.query.get(detalle.proveedor_id)
        detalle.centro_negocios = CentrosNegocio.query.get(detalle.centro_negocios_id)
        detalle.categoria = Categorias.query.get(detalle.categoria_id)
        detalle.concepto = Conceptos.query.get(detalle.concepto_id)

    return render_template("perfil_egreso.html", egreso=egreso, pagos=pagos, detalles=detalles)
    

 
@blueprint.route('/perfil_pago/<int:pago_id>', methods=['GET', 'POST'])
def perfil_pago(pago_id):
    pago = Pagos.query.get(pago_id)
    pago.beneficiario= Beneficiarios.query.get(pago.beneficiario_id)
    pago.forma_pago = FormasPago.query.get(pago.forma_pago_id)
    pago.cuenta = Cuentas.query.get(pago.cuenta_id)
    
    return render_template("perfil_pago.html", pago=pago)
   
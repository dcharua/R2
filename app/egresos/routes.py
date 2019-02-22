from app.egresos import blueprint
from flask import render_template, request, redirect, flash
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *
from datetime import date

@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


#####  EGRESOS ROUTES #########
#Egresos Create
@blueprint.route('/capturar_egreso', methods=['GET', 'POST'])
def capturar_egreso():
    
    if request.form:
        data = request.form
        montos = list(map(int, data.getlist("monto")))
        monto_total = sum(montos)
        egreso = Egresos(beneficiario_id=data["beneficiario"], fecha_vencimiento=data["fecha_vencimiento"], 
        fecha_programada_pago=data["fecha_programada_pago"], numero_documento=data["numero_documento"],
        monto_total=monto_total, monto_pagado=0, monto_solicitado=0, monto_por_conciliar=0, referencia=data["referencia"], 
        empresa_id=data["empresa"], comentario=data["comentario"], pagado = False, status='pendiente')
        for i in range(len(data.getlist("monto"))):
            detalle = DetallesEgreso(centro_negocios_id=data.getlist("centro_negocios")[i], proveedor_id=data.getlist("proveedor")[i],
            categoria_id=data.getlist("categoria")[i], concepto_id=data.getlist("concepto")[i], monto=data.getlist("monto")[i], 
            numero_control=data.getlist("numero_control")[i], descripcion=data.getlist("descripcion")[i])
            egreso.detalles.append(detalle)
        if ('pagado' in data):
            monto_pagado=data["monto_pagado"]
            egreso.monto_pagado=monto_pagado
            if ('conciliado_check' in data):
                status = 'conciliado'
                refrencia_conciliacion = data["referencia_conciliacion"]
                if egreso.monto_pagado == egreso.monto_total:
                    egreso.status = 'liquidado'
                else: 
                    egreso.status = 'parcial'
            else:
                egreso.monto_por_conciliar = monto_pagado
                status = 'por_conciliar'    
                refrencia_conciliacion = ""
                if egreso.monto_pagado == egreso.monto_total:
                    egreso.status = 'por_conciliar'
                else:
                    egreso.status = 'parcial'

            pago = Pagos(forma_pago_id = data["forma_pago"], cuenta_id= data["cuenta_banco"], referencia_pago = data["forma_pago"],fecha_pago = data["fecha_pago"], status = status, 
            referencia_conciliacion= refrencia_conciliacion,  monto_total = monto_pagado, comentario = data["comentario_pago"], beneficiario_id=1)
            if  float(monto_pagado) >= monto_total:
                egreso.pagado = True    
            ep = EgresosHasPagos(egreso = egreso, pago = pago, monto = monto_pagado)    
        if ('pagado' in data):
            db.session.add(ep)
        else:
            db.session.add(egreso)
        db.session.commit()
        return redirect("/egresos/cuentas_por_pagar")
        

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

#Egresos View all
@blueprint.route('/cuentas_por_pagar', methods=['GET', 'POST'])
def cuentas_por_pagar():
    egresos_pagados = Egresos.query.filter(Egresos.pagado == True).all()
    egresos_pendientes = Egresos.query.filter(Egresos.pagado == False).all()
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()
    return render_template("cuentas_por_pagar.html", egresos_pagados=egresos_pagados, egresos_pendientes=egresos_pendientes, formas_pago=formas_pago, cuentas=cuentas)


#Egresos perfil
@blueprint.route('/perfil_egreso/<int:egreso_id>', methods=['GET', 'POST'])
def perfil_egreso(egreso_id):
    egreso = Egresos.query.get(egreso_id)
    egreso.beneficiario= Beneficiarios.query.get(egreso.beneficiario_id)
    egreso.empresa = Empresas.query.get(egreso.empresa_id)
    detalles = DetallesEgreso.query.filter(DetallesEgreso.egreso_id == egreso_id)
    return render_template("perfil_egreso.html", egreso=egreso, pagos=egreso.pagos, detalles=detalles)


#Egresos Edit   
@blueprint.route('/editar_egreso/<int:egreso_id>"', methods=['GET', 'POST'])
def editar_egreso(egreso_id):
    return redirect("/")
    

#Egresos Delete
@blueprint.route("/borrar_egreso/<int:egreso_id>",  methods=['GET', 'POST'])
def delete_egreso(egreso_id):
    egreso = Egresos.query.get(egreso_id)
    db.session.delete(egreso)
    db.session.commit()
    flash('Egreso borrado', 'success')
    return redirect("/")


##### PAGOS ROUTES  #########

#pagos tablas
@blueprint.route('/pagos_realizados', methods=['GET', 'POST'])
def pagos_realizados():
    pagos = Pagos.query.filter(Pagos.status == 'solicitado').all()
    pagos_realizados = Pagos.query.filter(Pagos.status.like("%conci%")).all()
    return render_template("pagos_realizados.html", pagos=pagos, pagos_realizados=pagos_realizados)

#perfil pago
@blueprint.route('/perfil_pago/<int:pago_id>', methods=['GET', 'POST'])
def perfil_pago(pago_id):
    pago = Pagos.query.get(pago_id)    
    return render_template("perfil_pago.html", pago=pago)
   


#####perfil beneficiario
@blueprint.route('/perfil_beneficiario/<int:beneficiario_id>', methods=['GET', 'POST'])
def perfil_beneficiario(beneficiario_id):
    beneficiario = Beneficiarios.query.get(beneficiario_id)
    return render_template("perfil_beneficiario.html", beneficiario=beneficiario)   
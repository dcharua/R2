from app.egresos import blueprint
from flask import render_template, request, redirect, flash, jsonify
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
def borrar_egreso(egreso_id):
    egreso = Egresos.query.get(egreso_id)
    db.session.delete(egreso)
    db.session.commit()
    return  jsonify("deleted")

#Egresos Delete
@blueprint.route("/cancelar_egreso/<int:egreso_id>",  methods=['GET', 'POST'])
def cancelar_egreso(egreso_id):
    egreso = Egresos.query.get(egreso_id)
    egreso.status ='cancelado'
    db.session.commit()
    return  jsonify("deleted")



##### PAGOS ROUTES  #########

#pagos tablas
@blueprint.route('/pagos_realizados', methods=['GET', 'POST'])
def pagos_realizados():
    pagos = Pagos.query.filter(Pagos.status == 'solicitado').all()
    pagos_realizados = Pagos.query.filter(Pagos.status != 'solicitado').all()
    return render_template("pagos_realizados.html", pagos=pagos, pagos_realizados=pagos_realizados)

#perfil pago
@blueprint.route('/perfil_pago/<int:pago_id>', methods=['GET', 'POST'])
def perfil_pago(pago_id):
    pago = Pagos.query.get(pago_id)    
    return render_template("perfil_pago.html", pago=pago)
   


###### Borrar pago
@blueprint.route("/borrar_pago/<int:pago_id>",  methods=['GET', 'POST'])
def borrar_pago(pago_id):
    pago = Pagos.query.get(pago_id)
    for egreso in pago.egresos:
        ep = EgresosHasPagos.query.filter_by(egreso_id=egreso.id , pago_id =pago.id ).first()
        egreso.monto_solicitado -= ep.monto
        if egreso.monto_pagado > 0:
            egreso.status = 'parcial'
        else:
            egreso.status = 'pendiente'    
    db.session.delete(ep)
    db.session.delete(pago)
    db.session.commit()
    return  jsonify("deleted")

###### Cancelar pago
@blueprint.route("/cancelar_pago/<int:pago_id>",  methods=['GET', 'POST'])
def cancelar_pago(pago_id):
    pago = Pagos.query.get(pago_id)
    for egreso in pago.egresos:
        ep = EgresosHasPagos.query.filter_by(egreso_id=egreso.id , pago_id =pago.id ).first()
        egreso.monto_pagado -= ep.monto
        if pago.status == 'por_conciliar':
            egreso.monto_por_conciliar -= ep.monto
        ep.monto = 0
        
    pago.status = 'cancelado'
    db.session.commit()
    for egreso in pago.egresos:
        egreso.setStatus()
    return  jsonify("deleted")


###########MODALES  ###########
#####  SOLICITAR PAGO #######
#Solicitar pago data for modal
@blueprint.route('/get_data_pagar<int:egreso_id>', methods=['GET', 'POST'])
@login_required
def get_data_pagar(egreso_id):
        egreso = Egresos.query.get(egreso_id)
        monto_pendiente = egreso.monto_total - egreso.monto_solicitado - egreso.monto_pagado
        return jsonify(egreso_id = egreso.id, beneficiario = egreso.beneficiario.nombre, monto_total=str(monto_pendiente), numero_documento= egreso.numero_documento)


# Solcitar pago form submit
@blueprint.route('/mandar_pagar', methods=['GET', 'POST'])
@login_required
def mandar_pagar():
        if request.form:
                data = request.form
                egreso = Egresos.query.get(data["egreso_id"])
                if ('parcial' in data):
                        monto_total = data["monto_parcial"]
                else:
                        monto_total = egreso.monto_total - egreso.monto_solicitado - egreso.monto_pagado
                pago = Pagos(status='solicitado', beneficiario=egreso.beneficiario, monto_total=monto_total, cuenta_id=data["cuenta_id"], forma_pago_id=data["forma_pago_id"])
              
                ep = EgresosHasPagos(egreso = egreso, pago = pago, monto = monto_total)    
                egreso.monto_solicitado += int(pago.monto_total)

                if egreso.monto_total == egreso.monto_solicitado + egreso.monto_pagado:
                        egreso.status = 'solicitado'
                else:
                        egreso.status = 'parcial'
                db.session.add(ep)
                db.session.commit()
                return  redirect("/egresos/pagos_realizados")   


# Solicitar multiples pagos data for modal 
@blueprint.route('/get_data_pagar_multiple', methods=['GET', 'POST'])
@login_required
def get_data_pagar_multiple():
        list = []
        egresos = request.args.getlist('egresos[]')
        for egreso in egresos:
                e = Egresos.query.get(egreso)
                monto_pendiente = e.monto_total - e.monto_solicitado - e.monto_pagado
                list.append({'egreso_id': e.id, 'beneficiario': e.beneficiario.nombre, 'monto_total': str(monto_pendiente), 'numero_documento': e.numero_documento})
        return jsonify(list)


#Solicitar pago from sumbit
@blueprint.route('/mandar_pagar_multiple', methods=['GET', 'POST'])
@login_required
def mandar_pagar_multiple():
        if request.form:
                data = request.form
                for i in range(int(data["cantidad"])):
                        pago = Pagos(status='solicitado', monto_total=data["monto_total_%d" % i], cuenta_id=data["cuenta_id_%d" % i], forma_pago_id=data["forma_pago_id_%d" % i])
                        for egreso in data.getlist("egreso_%d" % i):
                                e = Egresos.query.get(egreso)
                                e.status = 'solicitado'
                                e.monto_solicitado +=  e.monto_total - e.monto_pagado
                                pago.beneficiario = e.beneficiario
                                ep = EgresosHasPagos(egreso=e, pago=pago, monto=e.monto_solicitado)
                                db.session.add(ep)
                                db.session.commit()
                return  redirect("/egresos/pagos_realizados")   



### CONCILIAT PAGOS ###
#Conciliar pago data for modal
@blueprint.route('/get_data_conciliar<int:pago_id>', methods=['GET', 'POST'])
@login_required
def get_data_conciliar(pago_id):
        pago = Pagos.query.get(pago_id)
        return jsonify(pago_id = pago.id, beneficiario = pago.beneficiario.nombre, monto_total=str(pago.monto_total), referencia = pago.referencia_pago , cuenta=pago.cuenta.nombre)


#Conciliar pago form sumbit
@blueprint.route('/conciliar_movimento', methods=['GET', 'POST'])
@login_required
def conciliar_movimento():
        if request.form:
                data = request.form
                pagos = (data.getlist('pago_id'))
                for pago_id in pagos:
                        pago = Pagos.query.get(pago_id)
                        pago.status = 'conciliado';
                        pago.referencia_conciliacion = data["referencia"]
                        pago.fecha_pago = data["fecha"]
                        pago.comentario = data["comentario"]
                        for egreso in pago.egresos:
                                ep = EgresosHasPagos.query.filter_by(egreso_id=egreso.id , pago_id =pago.id ).first()
                                egreso.monto_por_conciliar -= ep.monto
                                if egreso.monto_total == egreso.monto_pagado and egreso.monto_por_conciliar == 0:
                                        egreso.status = 'liquidado'     
                db.session.commit()
                return  redirect("/egresos/pagos_realizados")   

#Conciliar multiples pagos data for modal
@blueprint.route('/get_data_conciliar_multiple', methods=['GET', 'POST'])
@login_required
def get_data_conciliar_multiple():
        list = []
        pagos = request.args.getlist('pagos[]')
        for pago in pagos:
                p =  Pagos.query.get(pago)
                list.append({'pago_id': p.id, 'beneficiario': p.beneficiario.nombre, 'monto_total': str(p.monto_total), 'referencia': p.referencia_pago, 'cuenta': p.cuenta.nombre})
        return jsonify(list)

### GENERAR PAGO ###
#Generar pago for modal
@blueprint.route('/get_data_generar_pago<int:pago_id>', methods=['GET', 'POST'])
@login_required
def get_data_generar_pago(pago_id):
        pago = Pagos.query.get(pago_id)
        return jsonify(pago_id = pago.id, beneficiario = pago.beneficiario.nombre, 
        monto_total=str(pago.monto_total), cuenta=pago.cuenta.nombre, forma_pago = pago.forma_pago.nombre, 
        referencia = pago.referencia_pago, numero_cheque = str(pago.cuenta.numero_cheque + 1), cuenta_beneficiario=pago.beneficiario.cuenta_banco)     
 
       
# Generar pago form sumbit
@blueprint.route('/generar_pago', methods=['GET', 'POST'])
@login_required
def generar_pago():
        if request.form:
                data = request.form
                pago = Pagos.query.get(data["pago_id"])
                pago.referencia_pago = data["referencia_pago"]
                pago.fecha_pago = data["fecha_pago"]
                for egreso in pago.egresos:
                        ep = EgresosHasPagos.query.filter_by(egreso_id=egreso.id , pago_id =pago.id ).first()
                        egreso.monto_pagado += ep.monto
                        egreso.monto_solicitado -= ep.monto
                        if egreso.monto_pagado == egreso.monto_total:
                                egreso.pagado = True
                        if ('conciliado_check' in data):
                                pago.status = 'conciliado';
                                pago.referencia_conciliacion = data["referencia_conciliacion"]
                                if egreso.status != 'parcial' and egreso.monto_pagado == egreso.monto_total:
                                        egreso.status = 'liquidado'
                        else:
                                egreso.monto_por_conciliar += ep.monto
                                pago.status = 'por_conciliar'
                                if egreso.status != 'parcial' and egreso.monto_pagado == egreso.monto_total:
                                        egreso.status = 'por_conciliar'

                db.session.commit()
                return  redirect("/egresos/pagos_realizados")


#reprogramar_fecha
@blueprint.route('/reprogramar_fecha', methods=['GET', 'POST'])
@login_required
def reprogramar_fecha():
        if request.form:
                data = request.form
                egreso = Egresos.query.get(data["egreso_id"])
                egreso.fecha_programada_pago = data["fecha"]
                db.session.commit()
                return redirect("/egresos/cuentas_por_pagar")


#reprogramar fecha multiple
@blueprint.route('/reprogramar_fecha_multiple', methods=['GET', 'POST'])
@login_required
def reprogramar_fecha_multiple():      
        egresos = request.args.getlist('egresos[]')
        fecha = request.args.get('fecha')
        for egreso in egresos:
                egreso = Egresos.query.get(egreso)
                egreso.fecha_programada_pago=fecha
        db.session.commit()
        return redirect("/egresos/cuentas_por_pagar")
        
    
    
    
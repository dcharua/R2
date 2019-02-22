from app.modales import blueprint
from flask import render_template, request, jsonify, redirect
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *
from sqlalchemy import and_


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')

###### agregar modales

@blueprint.route('/agregar_beneficiario', methods=['GET', 'POST'])
@login_required
def agregar_beneficiario():
    if request.form:
        data = request.form
        beneficiario = Beneficiarios(nombre=data["nombre"], RFC=data["RFC"], 
            direccion=data["direccion"], razon_social=data["razon_social"],
            cuenta_banco=data["cuenta_banco"], banco=data["banco"])
        for i in range(len(data.getlist("nombre_contacto"))):
            contacto = ContactoBeneficiario(nombre=data.getlist("nombre_contacto")[i], correo=data.getlist("correo_contacto")[i],
            telefono=data.getlist("telefono_contacto")[i], extension=data.getlist("extension_contacto")[i], puesto=data.getlist("puesto_contacto")[i])
            beneficiario.contacto.append(contacto) 
        db.session.add(beneficiario)
        db.session.commit()   
        return redirect("/administracion/beneficiarios")
    
    
@blueprint.route('/agregar_cliente', methods=['GET', 'POST'])
@login_required
def agregar_cliente():
    if request.form:
        data = request.form
        cliente = Clientes(nombre = data["nombre"], RFC = data["RFC"], 
            direccion = data["direccion"], razon_social = data["razon_social"],
            cuenta_banco = data["cuenta_banco"], saldo = 0, status = 'Liquidado', comentarios = data["comentarios"],banco = data["banco"]) 
        
        print(data)
        for i in range(len(data.getlist("nombre_contacto"))):         
            contacto = ContactoCliente(nombre=data.getlist("nombre_contacto")[i], correo = data.getlist("correo_contacto")[i],
            telefono = data.getlist("telefono_contacto")[i], extension = data.getlist("extension_contacto")[i], puesto=data.getlist("puesto_contacto")[i])
            cliente.contacto.append(contacto)
            print(contacto)
        db.session.add(cliente)
        db.session.commit()   
        return redirect("/administracion/clientes")

@blueprint.route('/agregar_cuenta', methods=['GET', 'POST'])
@login_required
def agregar_cuenta():
    if request.form:
        data = request.form
        cuenta = Cuentas(nombre=data["nombre"], banco=data["banco"], numero=data["numero"], saldo=data["saldo"], empresa_id=data["empresa"], comentario=data["comentario"], numero_cheque=0) 
        db.session.add(cuenta)
        db.session.commit()   
        return redirect("/administracion/cuentas")    

@blueprint.route('/agregar_categoria', methods=['GET', 'POST'])
@login_required
def agregar_categoria():    
    if request.form:
        data = request.form
        categoria = Categorias(nombre=data["nombre"]) 
        db.session.add(categoria)
        db.session.commit()   
        return redirect("/administracion/otros")     


@blueprint.route('/agregar_centro', methods=['GET', 'POST'])
@login_required
def agregar_centro():
    if request.form:
        data = request.form
        centro = CentrosNegocio(nombre=data["nombre"], numero=data["numero"],  tipo=data["tipo"],  direccion=data["direccion"],  
        empresa_id=data["empresa"],  arrendadora=data["arrendadora"],  comentario=data["comentario"]  ) 
        db.session.add(centro) 
        db.session.commit()   
        return redirect("/administracion/otros")  


@blueprint.route('/agregar_concepto', methods=['GET', 'POST'])
@login_required
def agregar_concepto():
    if request.form:
        data = request.form
        concepto = Conceptos(nombre=data["nombre"]) 
        db.session.add(concepto)
        db.session.commit()   
        return redirect("/administracion/otros")      


@blueprint.route('/agregar_empresa', methods=['GET', 'POST'])
@login_required
def agregar_empresa():
    if request.form:
        data = request.form
        empresa = Empresas(nombre=data["nombre"]) 
        db.session.add(empresa)
        db.session.commit()   
        return redirect("/administracion/otros")
    

        
#agregar_forma pago
@blueprint.route('/agregar_forma_pago', methods=['GET', 'POST'])
@login_required
def agregar_forma_pago():
        if request.form:
                data = request.form
                forma_pago= FormasPago(nombre=data["nombre"])
                db.session.add(forma_pago)
                db.session.commit()   
                return redirect("/administracion/otros")   
    

@blueprint.route('/agregar_tipo_ingreso', methods=['GET', 'POST'])
@login_required
def agregar_tipo_ingreso():
    if request.form:
        data = request.form

        print('AAAAA/n/n/n/n/n/n')
        
        tipo_ingreso = Tipo_Ingreso(tipo = data["tipo"]) 
        print('/n/n/n/n/n/n',tipo_ingreso)
        print('/n/n/n/n/n/n')
        db.session.add(tipo_ingreso)
        db.session.commit()   
        return redirect("/administracion/otros")     
    
    
    
    
###############################
#         INGRESOS
###############################


#####  SOLICITAR PAGO #######
#Solicitar pago data for modal
@blueprint.route('get_data_pagar<int:egreso_id>', methods=['GET', 'POST'])
@login_required
def get_data_pagar(egreso_id):
        egreso = Egresos.query.get(egreso_id)
        monto_pendiente = egreso.monto_total - egreso.monto_solicitado - egreso.monto_pagado
        return jsonify(egreso_id = egreso.id, beneficiario = egreso.beneficiario.nombre, monto_total=str(monto_pendiente), numero_documento= egreso.numero_documento)


# Solcitar pago form submit
@blueprint.route('mandar_pagar', methods=['GET', 'POST'])
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
@blueprint.route('get_data_pagar_multiple', methods=['GET', 'POST'])
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
                                e.monto_solicitado =  e.monto_total - e.monto_solicitado - e.monto_pagado
                                pago.beneficiario = e.beneficiario
                                ep = EgresosHasPagos(egreso=e, pago=pago, monto=e.monto_solicitado)
                                db.session.add(ep)
                                db.session.commit()
                return  redirect("/egresos/pagos_realizados")   



### CONCILIAT PAGOS ###
#Conciliar pago data for modal
@blueprint.route('get_data_conciliar<int:pago_id>', methods=['GET', 'POST'])
@login_required
def get_data_conciliar(pago_id):
        pago = Pagos.query.get(pago_id)
        return jsonify(pago_id = pago.id, beneficiario = pago.beneficiario.nombre, monto_total=str(pago.monto_total), referencia = pago.referencia_pago , cuenta=pago.cuenta.nombre)


#Conciliar pago form sumbit
@blueprint.route('conciliar_movimento', methods=['GET', 'POST'])
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
@blueprint.route('get_data_conciliar_multiple', methods=['GET', 'POST'])
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
@blueprint.route('generar_pago', methods=['GET', 'POST'])
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
@blueprint.route('reprogramar_fecha', methods=['GET', 'POST'])
@login_required
def reprogramar_fecha():
        if request.form:
                data = request.form
                egreso = Egresos.query.get(data["egreso_id"])
                egreso.fecha_programada_pago = data["fecha"]
                db.session.commit()
                return redirect("/egresos/cuentas_por_pagar")


#reprogramar fecha multiple
@blueprint.route('reprogramar_fecha_multiple', methods=['GET', 'POST'])
@login_required
def reprogramar_fecha_multiple():      
        egresos = request.args.getlist('egresos[]')
        fecha = request.args.get('fecha')
        for egreso in egresos:
                egreso = Egresos.query.get(egreso)
                egreso.fecha_programada_pago=fecha
        db.session.commit()
        return redirect("/egresos/cuentas_por_pagar")
        
    
    
    
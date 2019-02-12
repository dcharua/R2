from app.modales import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *



@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('agregar_beneficiario', methods=['GET', 'POST'])
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

@blueprint.route('agregar_cuenta', methods=['GET', 'POST'])
@login_required
def agregar_cuenta():
    if request.form:
        data = request.form
        cuenta = Cuentas(banco=data["banco"], numero=data["numero"], saldo=data["saldo"]) 
        db.session.add(cuenta)
        db.session.commit()   
        return redirect("/administracion/cuentas")    

@blueprint.route('agregar_categoria', methods=['GET', 'POST'])
@login_required
def agregar_categoria():
    if request.form:
        data = request.form
        categoria = Categorias(nombre=data["nombre"]) 
        db.session.add(categoria)
        db.session.commit()   
        return redirect("/administracion/otros")     

@blueprint.route('agregar_centro', methods=['GET', 'POST'])
@login_required
def agregar_centro():
    if request.form:
        data = request.form
        centro = CentrosNegocio(nombre=data["nombre"], numero=data["numero"],  tipo=data["tipo"],  direccion=data["direccion"],  
        empresa_id=data["empresa"],  arrendadora=data["arrendadora"],  comentario=data["comentario"]  ) 
        db.session.add(centro) 
        db.session.commit()   
        return redirect("/administracion/otros")  


@blueprint.route('agregar_concepto', methods=['GET', 'POST'])
@login_required
def agregar_concepto():
    if request.form:
        data = request.form
        concepto = Conceptos(nombre=data["nombre"]) 
        db.session.add(concepto)
        db.session.commit()   
        return redirect("/administracion/otros")      

@blueprint.route('agregar_empresa', methods=['GET', 'POST'])
@login_required
def agregar_empresa():
    if request.form:
        data = request.form
        empresa = Empresas(nombre=data["nombre"]) 
        db.session.add(empresa)
        db.session.commit()   
        return redirect("/administracion/otros")
        
@blueprint.route('agregar_forma_pago', methods=['GET', 'POST'])
@login_required
def agregar_forma_pago():
    if request.form:
        data = request.form
        forma_pago = FormasPago(nombre=data["nombre"]) 
        db.session.add(forma_pago)
        db.session.commit()   
        return redirect("/administracion/otros")    
        
@blueprint.route('get_data_pagar<int:egreso_id>', methods=['GET', 'POST'])
@login_required
def get_data_pagar(egreso_id):
        egreso = Egresos.query.get(egreso_id)
        return jsonify(egreso_id = egreso.id, beneficiario = egreso.beneficiario.nombre, monto_total=str(egreso.monto_total), numero_documento= egreso.numero_documento)

@blueprint.route('mandar_pagar', methods=['GET', 'POST'])
@login_required
def mandar_pagar():
        if request.form:
                data = request.form
                egreso = Egresos.query.get(data["egreso_id"])
                pago = Pagos(conciliado=False, monto_total=egreso.monto_total, cuenta_id=data["cuenta_id"], forma_pago_id=data["forma_pago_id"])
                pago.egresos.append(egreso)
                egreso.monto_pagado = pago.monto_total
                egreso.pagado = True
                pago.beneficiario = egreso.beneficiario
                db.session.add(pago)
                db.session.commit()
                return  redirect("/egresos/pagos_realizados")   


@blueprint.route('get_data_conciliar<int:pago_id>', methods=['GET', 'POST'])
@login_required
def get_data_conciliar(pago_id):
        pago = Pagos.query.get(pago_id)
        return jsonify(pago_id = pago.id, beneficiario = pago.beneficiario.nombre, monto_total=str(pago.monto_total))

@blueprint.route('conciliar_movimento', methods=['GET', 'POST'])
@login_required
def conciliar_movimento():
        if request.form:
                data = request.form
                pago = Pagos.query.get(data["pago_id"])
                pago.conciliado = True;
                pago.referencia_conciliacion = data["referencia"]
                pago.fecha_pago = data["fecha"]
                pago.comentario = data["comentario"]
                db.session.commit()
                return  redirect("/egresos/pagos_realizados")   
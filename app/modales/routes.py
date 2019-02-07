from app.modales import blueprint
from flask import render_template, request
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
        centro = CentrosNegocio(nombre=data["nombre"]) 
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
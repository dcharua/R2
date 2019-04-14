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

    
@blueprint.route('/agregar_cliente', methods=['GET', 'POST'])
@login_required
def agregar_cliente():
    if request.form:
        data = request.form
        cliente = Clientes(nombre = data["nombre"], RFC = data["RFC"], 
            direccion = data["direccion"], razon_social = data["razon_social"],
            cuenta_banco = data["cuenta_banco"], saldo = 0, status = 'liquidado', comentarios = data["comentarios"],banco = data["banco"]) 
        for i in range(len(data.getlist("nombre_contacto"))):         
            contacto = ContactoCliente(nombre=data.getlist("nombre_contacto")[i], correo = data.getlist("correo_contacto")[i],
            telefono = data.getlist("telefono_contacto")[i], extension = data.getlist("extension_contacto")[i], puesto=data.getlist("puesto_contacto")[i])
            cliente.contacto.append(contacto)
        db.session.add(cliente)
        db.session.commit()   
        return redirect("/administracion/clientes")


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
        concepto = Conceptos(nombre=data["nombre"], categoria_id=data["categoria"]) 
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
        tipo_ingreso = Tipo_Ingreso(tipo = data["tipo"]) 
        db.session.add(tipo_ingreso)
        db.session.commit()   
        return redirect("/administracion/otros")     
    
    
    

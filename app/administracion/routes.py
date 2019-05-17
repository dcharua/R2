from app.administracion import blueprint
from flask import render_template, request, redirect, jsonify
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('/beneficiarios', methods=['GET', 'POST'])
@login_required
def beneficiarios():
    beneficiarios = Beneficiarios.query.all()
    categorias = Categorias.query.all()
    return render_template("beneficiarios.html", beneficiarios=beneficiarios, categorias=categorias)      

@blueprint.route('/perfil_de_beneficiario/<int:beneficiario_id>', methods=['GET', 'POST'])
def perfil_de_beneficiario(beneficiario_id):
    documentos_recibidos, documentos_liquidados, documentos_cancelados, documentos_pendientes, documentos_solicitados, documentos_parciales, saldo_pendiente, saldo_solicitado, saldo_transito, saldo_pagado, saldo_total = 0,0,0,0,0,0,0,0,0,0,0
    beneficiario = Beneficiarios.query.get(beneficiario_id)
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()
    categorias = Categorias.query.all()
    for egreso in beneficiario.egresos:
      documentos_recibidos += 1
      if egreso.status != 'cancelado':
        saldo_total += egreso.monto_total
        saldo_pagado += egreso.monto_pagado
        saldo_transito += egreso.monto_por_conciliar
        saldo_solicitado += egreso.monto_solicitado
        saldo_pendiente += egreso.monto_total - egreso.monto_pagado - egreso.monto_solicitado
      if egreso.status == 'liquidado':
        documentos_liquidados += 1
      elif egreso.status == 'cancelado':
        documentos_liquidados += 1
      elif egreso.status == 'pendiente':
        documentos_pendientes += 1
      elif egreso.status == 'solicitado':
        documentos_solicitados += 1
      elif egreso.status == 'parcial':
        documentos_parciales += 1
      

    return render_template("perfil_de_beneficiario.html", beneficiario = beneficiario, formas_pago=formas_pago, cuentas=cuentas, categorias=categorias,
  documentos_recibidos = documentos_recibidos, documentos_liquidados = documentos_liquidados, documentos_cancelados = documentos_cancelados, documentos_pendientes = documentos_pendientes, 
  documentos_solicitados = documentos_solicitados, documentos_parciales = documentos_parciales, saldo_total = saldo_total, 
  saldo_pendiente = saldo_pendiente, saldo_solicitado = saldo_solicitado, saldo_transito = saldo_transito, saldo_pagado = saldo_pagado)   


@blueprint.route('/agregar_beneficiario', methods=['GET', 'POST'])
@login_required
def agregar_beneficiario():
    if request.form:
        data = request.form
        beneficiario = Beneficiarios(nombre=data["nombre"], RFC=data["RFC"], 
            direccion=data["direccion"], razon_social=data["razon_social"],
            cuenta_banco=data["cuenta_banco"], saldo = 0, status = 'liquidado', banco=data["banco"])
        for i in range(len(data.getlist("nombre_contacto"))):
            contacto = ContactoBeneficiario(nombre=data.getlist("nombre_contacto")[i], correo=data.getlist("correo_contacto")[i],
            telefono=data.getlist("telefono_contacto")[i], extension=data.getlist("extension_contacto")[i], puesto=data.getlist("puesto_contacto")[i])
            beneficiario.contacto.append(contacto) 
        for i in range(len(data.getlist("categoria"))):
                categoria = Categorias.query.get(data.getlist("categoria")[i])
                beneficiario.categorias.append(categoria)          
        db.session.add(beneficiario)
        db.session.commit()   
        return redirect("/administracion/beneficiarios")

@blueprint.route('/get_data_editar_beneficiario/<beneficiario_id>', methods=['GET', 'POST'])
@login_required
def get_data_editar_beneficiario(beneficiario_id):
  contactos = []
  b = Beneficiarios.query.get(beneficiario_id)
  for c in b.contacto:
    contactos.append({'nombre':c.nombre,	'correo' : c.correo, 	'telefono': c.telefono, 'extension':c.extension, 'puesto' : c.puesto})
  return jsonify(id=b.id, nombre=b.nombre, RFC=b.RFC, direccion= b.direccion,  razon_social=b.razon_social, cuenta_banco=b.cuenta_banco,
  banco=b.banco, contacto=contactos) 

@blueprint.route('/editar_beneficiario', methods=['GET', 'POST'])
@login_required
def editar_beneficiario():
    if request.form:
        data = request.form
        beneficiario = Beneficiarios.query.get(data["id"]) 
        beneficiario.nombre=data["nombre"]
        beneficiario.RFC=data["RFC"] 
        beneficiario.direccion=data["direccion"]
        beneficiario.razon_social=data["razon_social"]
        beneficiario.cuenta_banco=data["cuenta_banco"] 
        beneficiario.banco=data["banco"]
        for i in range(len(data.getlist("nombre_contacto"))):
            beneficiario.contacto[i].nombre = data.getlist("nombre_contacto")[i]
            beneficiario.contacto[i].correo=data.getlist("correo_contacto")[i]
            beneficiario.contacto[i].telefono=data.getlist("telefono_contacto")[i]
            beneficiario.contacto[i].extension=data.getlist("extension_contacto")[i]
            beneficiario.contacto[i].puesto=data.getlist("puesto_contacto")[i]
        db.session.add(beneficiario)
        db.session.commit()   
        return redirect("/administracion/beneficiarios")

@blueprint.route('/agregar_categoria_cliente/<int:cliente_id>', methods=['GET', 'POST'])
@login_required
def agregar_categoria_cliente(cliente_id):
    if request.form:
        data = request.form
        cliente = Clientes.query.get(cliente_id) 
       
        for i in range(len(data.getlist("categoria"))):
                categoria = Categorias.query.get(data.getlist("categoria")[i])
                cliente.categorias.append(categoria)
        db.session.commit()   
    return redirect('/administracion/perfil_de_cliente/'+str(cliente_id))


@blueprint.route('/agregar_categoria_beneficiario/<int:beneficiario_id>', methods=['GET', 'POST'])
@login_required
def agregar_categoria_beneficiario(beneficiario_id):
    if request.form:
        data = request.form
        beneficiario = Beneficiarios.query.get(beneficiario_id) 
        for i in range(len(data.getlist("categoria"))):
                categoria = Categorias.query.get(data.getlist("categoria")[i])
                beneficiario.categorias.append(categoria)
        db.session.commit()    
    return redirect('/administracion/perfil_de_beneficiario/'+str(beneficiario_id))

@blueprint.route('/clientes', methods=['GET', 'POST'])
@login_required
def clientes():
    clientes = Clientes.query.all()
    return render_template("clientes.html", clientes = clientes)   

@blueprint.route('/agregar_cliente', methods=['GET', 'POST'])
@login_required
def agregar_cliente():
    if request.form:
        data = request.form
        cliente = Clientes(nombre = data["nombre"], RFC = data["RFC"], 
            direccion = data["direccion"], razon_social = data["razon_social"],
            cuenta_banco = data["cuenta_banco"], saldo_pendiente = 0, saldo_por_conciliar = 0,saldo_cobrado = 0,
            status = 'conciliado', comentarios = data["comentarios"],banco = data["banco"]) 
        for i in range(len(data.getlist("nombre_contacto"))):         
            contacto = ContactoCliente(nombre=data.getlist("nombre_contacto")[i], correo = data.getlist("correo_contacto")[i],
            telefono = data.getlist("telefono_contacto")[i], extension = data.getlist("extension_contacto")[i], puesto=data.getlist("puesto_contacto")[i])
            cliente.contacto.append(contacto)
        db.session.add(cliente)
        db.session.commit()   
        return redirect("/administracion/clientes")

@blueprint.route('/perfil_de_cliente/<int:cliente_id>', methods=['GET', 'POST'])
def perfil_de_cliente(cliente_id):

    cliente = Clientes.query.get(cliente_id)
    contactos_cliente = ContactoCliente.query.filter(ContactoCliente.cliente_id == cliente_id).all()
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()
    categorias = Categorias.query.all()
   
    return render_template("perfil_de_cliente.html", cliente = cliente,
                           contactos_cliente=contactos_cliente,formas_pago = formas_pago,
                           cuentas = cuentas,categorias = categorias)#, contactos_cliente = contactos_cliente)   

@blueprint.route('/cuentas', methods=['GET', 'POST'])
@login_required
def cuentas():
    cuentas = Cuentas.query.all()
    empresas = Empresas.query.all()
    return render_template("cuentas.html", cuentas=cuentas, empresas=empresas)   

@blueprint.route('/centros_negocios', methods=['GET', 'POST'])
@login_required
def centros_negocios():
    centros = CentrosNegocio.query.all()
    empresas = Empresas.query.all()
    return render_template("centros_negocios.html", centros=centros, empresas=empresas)

@blueprint.route('/otros', methods=['GET', 'POST'])
@login_required
def otros():
    categorias = Categorias.query.all()
    conceptos = Conceptos.query.all()
    empresas = Empresas.query.all()
    formas_pago = FormasPago.query.all()
    tipo_ingresos = Tipo_Ingreso.query.all()
    return render_template("otros.html", tipo_ingresos = tipo_ingresos, categorias=categorias, conceptos=conceptos, empresas=empresas, formas_pago=formas_pago)

@blueprint.route('/directorio_contactos', methods=['GET', 'POST'])
@login_required
def directorio_contactos():
    beneficiarios = Beneficiarios.query.all()
    clientes = Clientes.query.all()
    return render_template("directorio_contactos.html", beneficiarios = beneficiarios, clientes=clientes)

@blueprint.route('/editar_multiple', methods=['GET', 'POST'])
@login_required
def editar_multiple():
    if request.form:
        data = request.form
        if (data["type"] == "Empresa"):
            obj = Empresas.query.get(data["id"])
            obj.nombre = data["value"]
        elif (data["type"] == "Forma de pago"):
            obj = FormasPago.query.get(data["id"])
            obj.nombre = data["value"]
        elif (data["type"] == "Categoria"):
            obj = Categorias.query.get(data["id"])
            obj.nombre = data["value"]
        elif (data["type"] == "Tipo de ingreso"):
            obj = Tipo_Ingreso.query.get(data["id"])
            obj.tipo = data["value"]
        elif (data["type"] == "Concepto"):
            obj = Conceptos.query.get(data["id"])
            obj.nombre = data["value"]
            obj.categoria_id = data["categoria-id"]
        db.session.commit()  
    return redirect("/administracion/otros")

@blueprint.route('/editar_comentario', methods=['GET', 'POST'])
@login_required
def editar_comentario():
    if request.form:
        data = request.form
        if (data["type"] == "Egreso"):
            obj = Egresos.query.get(data["id"])
            obj.comentario = data["comentario"]
        elif (data["type"] == "Pago"):
            obj = Pagos.query.get(data["id"])
            obj.comentario = data["comentario"]
        elif (data["type"] == "Cuenta"):
            obj = Cuentas.query.get(data["id"])
            obj.comentario = data["comentario"]
        elif (data["type"] == "Beneficiario"):
            obj = Beneficiarios.query.get(data["id"])
            obj.comentarios = data["comentario"]
        elif (data["type"] == "Cliente"):
            obj = Clientes.query.get(data["id"])
            obj.comentarios = data["comentario"]
        db.session.commit()  
    return redirect(data["url"])

@blueprint.route('/borrar_categoria-beneficiario/<categoria_id>/<beneficiario_id>', methods=['GET', 'POST'])
@login_required
def borrar_categoria_beneficiario(categoria_id, beneficiario_id):
  beneficiario = Beneficiarios.query.get(beneficiario_id)
  categoria = Categorias.query.get(categoria_id)
  beneficiario.categorias.remove(categoria)      
  db.session.commit()  
  return redirect('/administracion/perfil_de_beneficiario/'+str(beneficiario_id))
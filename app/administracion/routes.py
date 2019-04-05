from app.administracion import blueprint
from flask import render_template, request, redirect
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
    beneficiario = Beneficiarios.query.get(beneficiario_id)
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()
    categorias = Categorias.query.all()
    return render_template("perfil_de_beneficiario.html", beneficiario = beneficiario, formas_pago=formas_pago, cuentas=cuentas, categorias=categorias)   


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

@blueprint.route('/perfil_de_cliente/<int:cliente_id>', methods=['GET', 'POST'])
def perfil_de_cliente(cliente_id):
    cliente = Clientes.query.get(cliente_id)
    contactos_cliente = ContactoCliente.query.filter(ContactoCliente.cliente_id == cliente_id).all()

    return render_template("perfil_de_cliente.html", cliente = cliente, contactos_cliente = contactos_cliente)   

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

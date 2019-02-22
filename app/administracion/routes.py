from app.administracion import blueprint
from flask import render_template, request
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
    return render_template("beneficiarios.html", beneficiarios=beneficiarios)        

@blueprint.route('/clientes', methods=['GET', 'POST'])
@login_required
def clientes():
    clientes = Clientes.query.all()
    return render_template("clientes.html", clientes = clientes)   

@blueprint.route('/perfil_de_cliente/<int:cliente_id>', methods=['GET', 'POST'])
def perfil_de_cliente(cliente_id):
    cliente = Clientes.query.get(cliente_id)
    contactos_cliente = ContactoCliente.query.filter(ContactoCliente.cliente_id == cliente_id).all()
    #contactos_cliente = ContactoCliente.query.all()
    print(contactos_cliente)

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

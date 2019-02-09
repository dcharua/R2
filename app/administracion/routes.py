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


@blueprint.route('beneficiarios', methods=['GET', 'POST'])
@login_required
def beneficiarios():
    beneficiarios = Beneficiarios.query.all()
    return render_template("beneficiarios.html", beneficiarios=beneficiarios)        

@blueprint.route('/clientes', methods=['GET', 'POST'])
@login_required
def clientes():
    return render_template("clientes.html", cuentas=cuentas)      

@blueprint.route('cuentas', methods=['GET', 'POST'])
@login_required
def cuentas():
    cuentas = Cuentas.query.all()
    return render_template("cuentas.html", cuentas=cuentas)   

@blueprint.route('centros_negocios', methods=['GET', 'POST'])
@login_required
def centros_negocios():
    centros = CentrosNegocio.query.all()
    return render_template("centros_negocios.html", centros=centros)

@blueprint.route('otros', methods=['GET', 'POST'])
@login_required
def otros():
    categorias = Categorias.query.all()
    conceptos = Conceptos.query.all()
    empresas = Empresas.query.all()
    formas_pago = FormasPago.query.all()
    return render_template("otros.html", categorias=categorias, conceptos=conceptos, empresas=empresas, formas_pago=formas_pago)

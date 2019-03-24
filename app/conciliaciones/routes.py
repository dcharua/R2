from app.conciliaciones import blueprint
from flask import render_template, request
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('/capturar_conciliacion', methods=['GET', 'POST'])
def capturar_conciliacion():
    cuentas = Cuentas.query.all()
    for cuenta in cuentas:
        cuenta.saldo_conciliado_egresos = 0
        cuenta.saldo_conciliado_ingresos = 0
        cuenta.saldo_transito_egresos = 0
        cuenta.saldo_transito_ingresos = 0
        cuenta.saldo_solicitado_egresos = 0 
        for pago in cuenta.pagos:
                if pago.status == 'conciliado':
                    cuenta.saldo_conciliado_egresos += pago.monto_total
                elif pago.status == 'por_conciliar':
                    cuenta.saldo_transito_egresos += pago.monto_total
                elif pago.status == 'solicitado':
                    cuenta.saldo_solicitado_egresos += pago.monto_total

        for pago in cuenta.pagos_ingresos:
                if pago.status == 'conciliado':
                    cuenta.saldo_conciliado_ingresos += pago.monto_total
                elif pago.status == 'por_conciliar':
                    cuenta.saldo_transito_ingresos += pago.monto_total
        cuenta.ultima_conciliacion = None
        if (cuenta.conciliaciones):
                cuenta.ultima_conciliacion = cuenta.conciliaciones[-1]
    return render_template("capturar_conciliacion.html", cuentas=cuentas)   

@blueprint.route('/agregar_cuenta', methods=['GET', 'POST'])
@login_required
def agregar_cuenta():
    if request.form:
        data = request.form
        cuenta = Cuentas(nombre=data["nombre"], banco=data["banco"], numero=data["numero"], saldo=data["saldo"], saldo_inicial=data["saldo"], empresa_id=data["empresa"], comentario=data["comentario"], numero_cheque=0) 
        db.session.add(cuenta)
        db.session.commit()   
        return redirect("/conciliaciones/capturar_conciliacion")    

@blueprint.route('/perfil_cuenta/<int:cuenta_id>', methods=['GET', 'POST'])
@login_required
def perfil_cuenta(cuenta_id):
    cuenta = Cuentas.query.get(cuenta_id)
    saldo_conciliado_egresos = 0
    saldo_conciliado_ingresos = 0
    saldo_transito_egresos = 0
    saldo_transito_ingresos = 0
    saldo_solicitado_egresos = 0 
    for pago in cuenta.pagos:
        if pago.status == 'conciliado':
            saldo_conciliado_egresos += pago.monto_total
        elif pago.status == 'por_conciliar':
            saldo_transito_egresos += pago.monto_total
        elif pago.status == 'solicitado':
            saldo_solicitado_egresos += pago.monto_total

    for pago in cuenta.pagos_ingresos:
        if pago.status == 'conciliado':
            saldo_conciliado_ingresos += pago.monto_total
        elif pago.status == 'por_conciliar':
            saldo_transito_ingresos += pago.monto_total
    ultima_conciliacion = None
    if (cuenta.conciliaciones):
        ultima_conciliacion = cuenta.conciliaciones[-1]
    return render_template("perfil_cuenta.html", cuenta=cuenta,  saldo_conciliado_egresos=saldo_conciliado_egresos, saldo_conciliado_ingresos=saldo_conciliado_ingresos,  
    saldo_transito_egresos =  saldo_transito_egresos, saldo_transito_ingresos=saldo_transito_ingresos, saldo_solicitado_egresos = saldo_solicitado_egresos, ultima_conciliacion = ultima_conciliacion)

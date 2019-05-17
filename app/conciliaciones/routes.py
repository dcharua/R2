from app.conciliaciones import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *
from datetime import date


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('/capturar_conciliacion', methods=['GET', 'POST'])
def capturar_conciliacion():
    now = date.today()
    cuentas = Cuentas.query.all()
    empresas = Empresas.query.all()
    formas_pago = FormasPago.query.all()
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
    return render_template("capturar_conciliacion.html", hoy=now, cuentas=cuentas, empresas=empresas, formas_pago=formas_pago)   

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


@blueprint.route('/conciliar_cuenta', methods=['GET', 'POST'])
@login_required
def conciliar_cuenta():
    if request.form:
        now = date.today()
        status=None
        
        data = request.form
        cuenta = Cuentas.query.get(data['cuenta_id'])
        cuenta.saldo = data["saldo"]
        saldo_sistema = cuenta.saldo_inicial
        for pago in cuenta.pagos_ingresos:
            if pago.status == 'conciliado':
                saldo_sistema += pago.monto_total

        for pago in cuenta.pagos:
            if pago.status == 'conciliado':
                saldo_sistema -= pago.monto_total

        conciliacion = Conciliaciones(cuenta_id=data['cuenta_id'], fecha=now, saldo_usuario=data["saldo"], 
        saldo_sistema=saldo_sistema, comentario=data["comentario"], status=status)
        if float(conciliacion.saldo_usuario) == float(conciliacion.saldo_sistema):
            conciliacion.status = 'correcta'
        else:
            conciliacion.status = 'por_revisar'
        db.session.add(conciliacion)
        db.session.commit()   
        if float(conciliacion.saldo_usuario) == float(conciliacion.saldo_sistema):
            return jsonify({'res':1, 'conciliacion':conciliacion.id ,'saldo_sistema': float(conciliacion.saldo_sistema), 'saldo_usuario': float(conciliacion.saldo_usuario)})
        else:
            return jsonify({'res':2, 'conciliacion':conciliacion.id ,'saldo_sistema': float(conciliacion.saldo_sistema), 'saldo_usuario': float(conciliacion.saldo_usuario)})
    return jsonify("error")


@blueprint.route('/ajustar_conciliacion/<int:conciliacion_id>', methods=['GET', 'POST'])
@login_required
def ajustar_conciliacion(conciliacion_id):
    conciliacion = Conciliaciones.query.get(conciliacion_id)
    if conciliacion.saldo_usuario > conciliacion.saldo_sistema:
        monto = conciliacion.saldo_usuario - conciliacion.saldo_sistema
        ajuste = Pagos_Ingresos(referencia_pago="ajuste "+str(conciliacion_id), fecha_pago=conciliacion.fecha,
        status="conciliado", monto_total=monto, cuenta_id=conciliacion.cuenta_id, cliente_id=1, forma_pago_id=1)
        db.session.add(ajuste)
        db.session.commit() 
        conciliacion.ingreso_id= ajuste.id
        conciliacion.status = "con_ajuste"
        db.session.commit() 
        return  jsonify("exito")

    else:
        monto = conciliacion.saldo_sistema - conciliacion.saldo_usuario
        ajuste = Pagos(referencia_pago="ajuste "+str(conciliacion_id), fecha_pago=conciliacion.fecha,
        status="conciliado", monto_total=monto, cuenta_id=conciliacion.cuenta_id, beneficiario_id=1, forma_pago_id=1)
        db.session.add(ajuste)
        db.session.commit()
        conciliacion.egreso_id= ajuste.id
        conciliacion.status = "con_ajuste"
        db.session.commit() 
        return  jsonify("exito")  
    return jsonify("error")  


@blueprint.route('/recalcular_conciliacion', methods=['GET', 'POST'])
@login_required
def recalcular_conciliacion():
    if request.form:
        data = request.form
        conciliacion = Conciliaciones.query.get(data["conciliacion_id"])
        if conciliacion.ingreso_id:
            ingreso = Pagos_Ingresos.query.get(conciliacion.ingreso_id)
            conciliacion.ingreso_id = None
            db.session.delete(ingreso)
        if conciliacion.egreso_id:
            egreso = Pagos.query.get(conciliacion.egreso_id)
            conciliacion.egreso_id = None
            print(egreso)
            db.session.delete(egreso)
        db.session.commit() 
        cuenta = Cuentas.query.get(conciliacion.cuenta_id)
        cuenta.saldo = data["saldo"]
        saldo_sistema = cuenta.saldo_inicial
        for pago in cuenta.pagos_ingresos:
            if pago.status == 'conciliado':
                saldo_sistema += pago.monto_total

        for pago in cuenta.pagos:
            if pago.status == 'conciliado':
                saldo_sistema -= pago.monto_total
        
        conciliacion.saldo_usuario = data["saldo"]
        conciliacion.saldo_sistema = saldo_sistema
        conciliacion.comentario = data["comentario"]
        if float(conciliacion.saldo_usuario) == float(conciliacion.saldo_sistema):
            conciliacion.status = 'correcta'
        else:
            conciliacion.status = 'por_revisar'
        db.session.add(conciliacion)
        db.session.commit()   
        if float(conciliacion.saldo_usuario) == float(conciliacion.saldo_sistema):
            return jsonify({'res':1, 'conciliacion':conciliacion.id ,'saldo_sistema': float(conciliacion.saldo_sistema), 'saldo_usuario': float(conciliacion.saldo_usuario)})
        else:
            return jsonify({'res':2, 'conciliacion':conciliacion.id ,'saldo_sistema': float(conciliacion.saldo_sistema), 'saldo_usuario': float(conciliacion.saldo_usuario)})
    return jsonify("error")

@blueprint.route('/cambiar_numero_cheque/<int:cuenta_id>', methods=['GET', 'POST'])
@login_required
def cambiar_numero_cheque(cuenta_id):
    if request.form:
        cuenta = Cuentas.query.get(cuenta_id)
        data = request.form
        cuenta.numero_cheque = data["number"]
        db.session.commit() 
        return redirect("/conciliaciones/perfil_cuenta/" + str(cuenta_id))    
        

@blueprint.route('/transferir', methods=['GET', 'POST'])
def transferir():
  if request.form:
        data = request.form
        p_egreso = Pagos(referencia_pago=data["referencia"], fecha_pago=date.today(),
        status="conciliado", monto_total=data["monto"], cuenta_id=data["cuenta_origen"], beneficiario_id=1, forma_pago_id=data["forma_pago_origen"], comentario=data["comentario"])
        p_ingreso = Pagos_Ingresos(referencia_pago=data["referencia"], fecha_pago=date.today(),
        status="conciliado", monto_total=data["monto"], cuenta_id=data["cuenta_destino"], cliente_id=1, forma_pago_id=data["forma_pago_destino"], comentario=data["comentario"])
        db.session.add(p_egreso)
        db.session.add(p_ingreso)
        db.session.commit() 
        return redirect("/conciliaciones/capturar_conciliacion")  

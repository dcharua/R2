from app.egresos import blueprint
from flask import render_template, request, redirect, flash, jsonify, send_file
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *
from app.db_models.db_migration import *
from datetime import date,timedelta
from decimal import Decimal
from sqlalchemy.sql import func

import pyodbc
import pandas as pd
import numpy as np
import time

from apscheduler.schedulers.background import BackgroundScheduler
from app.db_models.db_migration import *

########################### REAL EGRESOS!! ########################

import pyodbc
import pandas as pd


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


def test_connection():
   
    try:
        con_GEZ = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=gez;uid=gezsa001;pwd=gez9105ru2")
        con_rdm = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=rdm;uid=gezsa001;pwd=gez9105ru2")

        sql = "SELECT * FROM dbo.proveedores"
        data = pd.read_sql(sql,con_GEZ)
        return (data.head())
    
    except Exception as e:

        return e


#####  EGRESOS ROUTES #########
#Egresos Create
@blueprint.route('/capturar_egreso', methods=['GET', 'POST'])
def capturar_egreso():
    if request.form:
        data = request.form
        montos = list(map(float, data.getlist("monto")))
        monto_total = sum(montos)
        egreso = Egresos(beneficiario_id=data["beneficiario"], fecha_vencimiento=data["fecha_vencimiento"],
                         fecha_documento = data["fecha_documento"], numero_documento=data["numero_documento"],
                         monto_total=monto_total, monto_documento = monto_total, monto_pagado=0, monto_solicitado=0, monto_por_conciliar=0, referencia=data["referencia"],
                         empresa_id=data["empresa"], comentario=data["comentario"], pagado=False, status='pendiente')
        if (data["fecha_programada_pago"] != ""):
          egreso.fecha_programada_pago = data["fecha_programada_pago"]
        for i in range(len(data.getlist("monto"))):
            detalle = DetallesEgreso(centro_negocios_id=data.getlist("centro_negocios")[i], proveedor_id=data.getlist("proveedor")[i],
                                     categoria_id=data.getlist("categoria")[i], concepto_id=data.getlist(
                                         "concepto")[i], monto=float(data.getlist("monto")[i]),
                                     numero_control=data.getlist("numero_control")[i], descripcion=data.getlist("descripcion")[i])
            egreso.detalles.append(detalle)
        if ('pagado' in data):

            monto_pagado = float(data["monto_pagado"])
            egreso.monto_pagado = monto_pagado

            if ('conciliado_check' in data):
                status = 'conciliado'
                refrencia_conciliacion = data["referencia_conciliacion"]
                if float(egreso.monto_pagado) == float(egreso.monto_total):
                    egreso.status = 'liquidado'
                else:
                    egreso.status = 'parcial'
            else:
                egreso.monto_por_conciliar == monto_pagado
                status = 'por_conciliar'
                refrencia_conciliacion = ""
                if float(egreso.monto_pagado) == float(egreso.monto_total):
                    egreso.status = 'por_conciliar'
                else:
                    egreso.status = 'parcial'

            pago = Pagos(forma_pago_id=data["forma_pago"], cuenta_id=data["cuenta_banco"], referencia_pago=data["referencia_pago"], fecha_pago=data["fecha_pago"], status=status,
                         referencia_conciliacion=refrencia_conciliacion, fecha_conciliacion=data["fecha_pago"], monto_total=monto_pagado, comentario=data["comentario_pago"], beneficiario_id=data["beneficiario"])
            if float(monto_pagado) >= float(monto_total):
                egreso.pagado = True
            ep = EgresosHasPagos(egreso=egreso, pago=pago, monto=monto_pagado)
        if ('pagado' in data):
            db.session.add(ep)
        else:
            db.session.add(egreso)
        db.session.commit()
        return redirect("/egresos/cuentas_por_pagar")

    beneficiarios = Beneficiarios.query.all()
    empresas = Empresas.query.all()
    centros_negocios = CentrosNegocio.query.all()
    proveedores = beneficiarios
    categorias = Categorias.query.filter(Categorias.tipo=="egreso").all()
    conceptos = Conceptos.query.all()
    cuentas_banco = Cuentas.query.all()
    formas_pago = FormasPago.query.all()
    return render_template("capturar_egreso.html",
                           navbar_data_capture='active',
                           title="Registro de Egresos --"+str(a),
                           beneficiarios=beneficiarios,
                           empresas=empresas,
                           centros_negocios=centros_negocios,
                           proveedores=proveedores,
                           categorias=categorias,
                           conceptos=conceptos,
                           cuentas_banco=cuentas_banco,
                           formas_pago=formas_pago)



#Egresos View all
@blueprint.route('/cuentas_por_pagar', methods=['GET', 'POST'])
def cuentas_por_pagar():
    egresos_pagados = Egresos.query.filter(Egresos.pagado == True).all()
    egresos_pendientes = Egresos.query.filter(Egresos.pagado == False).all()
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()
    return render_template("cuentas_por_pagar.html", egresos_pagados=egresos_pagados, egresos_pendientes=egresos_pendientes, formas_pago=formas_pago, cuentas=cuentas)



#Egresos perfil
@blueprint.route('/perfil_egreso/<int:egreso_id>', methods=['GET', 'POST'])
def perfil_egreso(egreso_id):

    egreso = Egresos.query.get(egreso_id)
    egresos = Egresos.query.filter(Egresos.beneficiario_id==egreso.beneficiario_id).all()
    centros_negocio = CentrosNegocio.query.all()
    proveedores = Beneficiarios.query.all()
    categorias = Categorias.query.filter(Categorias.tipo=="egreso").all()
    conceptos = Conceptos.query.all()
    cuentas = Cuentas.query.all()
    empresas = Empresas.query.all()
    notas = NotasCredito.query.filter(NotasCredito.egreso_WR_id == egreso_id)
    monto_notas = 0
    for nota in notas:
        monto_notas += nota.monto
    formas_pago = FormasPago.query.all()
    if egreso.descuento is None:
            egreso.descuento = 0
    return render_template("perfil_egreso.html", egreso=egreso, notas = notas, monto_notas = monto_notas,egresos = egresos, empresas=empresas, centros_negocio=centros_negocio, proveedores=proveedores, categorias=categorias, conceptos=conceptos, formas_pago=formas_pago, cuentas=cuentas)


#Egresos Edit
@blueprint.route('/editar_egreso/<int:egreso_id>"', methods=['GET', 'POST'])
def editar_egreso(egreso_id):
    if request.form:
        data = request.form
        egreso = Egresos.query.get(egreso_id)
        if "beneficiario" in data:
            egreso.beneficiario_id =  data["beneficiario"]
        egreso.empresa_id =  data["empresa"]
        if  data["fecha_programada_pago"]:
            egreso.fecha_programada_pago = data["fecha_programada_pago"]
        egreso.fecha_vencimiento = data["fecha_vencimiento"]
        egreso.referencia = data["referencia"]
        egreso.numero_documento = data["numero_documento"]
        egreso.comentario = data["comentario"]
        db.session.commit()
    return redirect("/egresos/perfil_egreso/" + str(egreso_id))





#Egresos Delete
@blueprint.route("/borrar_egreso/<int:egreso_id>", methods=['GET', 'POST'])
def borrar_egreso(egreso_id):
    egreso = Egresos.query.get(egreso_id)
    db.session.delete(egreso)
    db.session.commit()
    return jsonify("deleted")

#Egresos Delete
@blueprint.route("/cancelar_egreso/<int:egreso_id>", methods=['GET', 'POST'])
def cancelar_egreso(egreso_id):
    '''
    egreso = Egresos.query.get(egreso_id)
    egreso.status = 'cancelado'
    db.session.commit()
    '''
    print('heere')
    return jsonify("deleted")

#Egresos Delete
@blueprint.route("/cancelar_egreso_2/<int:egreso_id>", methods=['GET', 'POST'])
def cancelar_egreso_2(egreso_id):
    egreso = Egresos.query.get(egreso_id)
    egreso.status = 'cancelado'
    db.session.commit()
    return jsonify("deleted")


@blueprint.route('/test_egreso"', methods=['GET', 'POST'])
def test_egreso():
    print('heeey')
    return jsonify("deleted")


##### PAGOS ROUTES  #########

#pagos tablas
@blueprint.route('/pagos_realizados', methods=['GET', 'POST'])
def pagos_realizados():
    pagos = Pagos.query.filter(Pagos.status == 'solicitado').all()
    pagos_realizados = Pagos.query.filter(Pagos.status != 'solicitado').all()
    return render_template("pagos_realizados.html", pagos=pagos, pagos_realizados=pagos_realizados)

#perfil pago
@blueprint.route('/perfil_pago/<int:pago_id>', methods=['GET', 'POST'])
def perfil_pago(pago_id):
    pago = Pagos.query.get(pago_id)
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()
    ep = EgresosHasPagos.query.filter_by(pago_id=pago_id)
    montoDocumentos = 0
    montoDescuentos = 0
    for egreso in ep:
        if egreso.egreso.descuento is None:
                egreso.egreso.descuento = 0  
        montoDescuentos =+ egreso.egreso.descuento
        montoDocumentos =+ egreso.egreso.monto_total
        
    return render_template("perfil_pago.html", pago=pago, cuentas= cuentas, formas_pago = formas_pago, ep=ep, montoDocumentos = montoDocumentos, montoDescuentos = montoDescuentos)

#Editar pago
@blueprint.route('/editar_pago/<int:pago_id>"', methods=['GET', 'POST'])
def editar_pago(pago_id):
    if request.form:
        data = request.form
        pago = Pagos.query.get(pago_id)
        if "cuenta" in data:
            pago.cuenta_id = data["cuenta"]
        if "forma_pago" in data:
            pago.forma_pago_id = data["forma_pago"]
        if "referencia" in data:
            pago.referencia_pago = data["referencia"]
        if "fecha_pago" in data:
            pago.fecha_pago = data["fecha_pago"]
        pago.comentario = data["comentario"]
        db.session.commit()
    return redirect("/egresos/perfil_pago/" + str(pago_id))


###### Borrar pago
@blueprint.route("/borrar_pago/<int:pago_id>", methods=['GET', 'POST'])
def borrar_pago(pago_id):
    pago = Pagos.query.get(pago_id)
    for egreso in pago.egresos:
        ep = EgresosHasPagos.query.filter_by(egreso_id=egreso.id, pago_id=pago.id).first()
        egreso.monto_solicitado -= ep.monto
        db.session.delete(ep)
        db.session.commit()
        if egreso.monto_pagado > 0:
            egreso.status = 'parcial'
        else:
            egreso.status = 'pendiente'
    db.session.delete(pago)
    db.session.commit()
    return jsonify("deleted")

###### Cancelar pago
@blueprint.route("/cancelar_pago/<int:pago_id>", methods=['GET', 'POST'])
def cancelar_pago(pago_id):
    pago = Pagos.query.get(pago_id)
    for egreso in pago.egresos:
        ep = EgresosHasPagos.query.filter_by(egreso_id=egreso.id, pago_id=pago.id).first()
        egreso.monto_pagado -= ep.monto
        if pago.status == 'por_conciliar':
            egreso.monto_por_conciliar -= ep.monto
        ep.monto = 0
        egreso.pagado = False

    pago.status = 'cancelado'
    db.session.commit()
    for egreso in pago.egresos:
        egreso.setStatus()
    db.session.commit()
    return jsonify("deleted")


###########MODALES  ###########
#####  SOLICITAR PAGO #######
#Solicitar pago data for modal
@blueprint.route('/get_data_pagar<int:egreso_id>', methods=['GET', 'POST'])
@login_required
def get_data_pagar(egreso_id):
        egreso = Egresos.query.get(egreso_id)
        monto_pendiente = egreso.monto_total - egreso.monto_solicitado - egreso.monto_pagado
        return jsonify(egreso_id=egreso.id, beneficiario=egreso.beneficiario.nombre, monto_total=str(monto_pendiente), numero_documento=egreso.numero_documento)


# Solcitar pago form submit
@blueprint.route('/mandar_pagar', methods=['GET', 'POST'])
@login_required
def mandar_pagar():
        if request.form:
                data = request.form
                print(data)
                egreso = Egresos.query.get(data["egreso_id"])
                if ('parcial' in data):
                        monto_total = data["monto_parcial"]
                else:
                        monto_total = egreso.monto_total - egreso.monto_solicitado - egreso.monto_pagado
                pago = Pagos(status='solicitado', beneficiario=egreso.beneficiario, monto_total=monto_total,
                             cuenta_id=data["cuenta_id"], forma_pago_id=data["forma_pago_id"])

                ep = EgresosHasPagos(egreso=egreso, pago=pago, monto=monto_total)
                egreso.monto_solicitado += Decimal(pago.monto_total)

                if egreso.monto_total == egreso.monto_solicitado + egreso.monto_pagado:
                        egreso.status = 'solicitado'
                else:
                        egreso.status = 'parcial'
                db.session.add(ep)
                db.session.commit()
                if ('url' in data):
                    return redirect(data["url"])
                else:
                    return redirect("/egresos/pagos_realizados")


# Solicitar multiples pagos data for modal
@blueprint.route('/get_data_pagar_multiple', methods=['GET', 'POST'])
@login_required
def get_data_pagar_multiple():
        list = []
        egresos = request.args.getlist('egresos[]')
        for egreso in egresos:
                e = Egresos.query.get(egreso)
                monto_pendiente = e.monto_total - e.monto_solicitado - e.monto_pagado
                list.append({'egreso_id': e.id, 'beneficiario': e.beneficiario.nombre, 'monto_total': str(
                    monto_pendiente), 'numero_documento': e.numero_documento})
        return jsonify(list)


#Solicitar pago Múltiple from sumbit
@blueprint.route('/mandar_pagar_multiple', methods=['GET', 'POST'])
@login_required
def mandar_pagar_multiple():
        if request.form:
                data = request.form
                for i in range(int(data["cantidad"])):
                        pago = Pagos(status='solicitado', monto_total=data["monto_total_%d" % i],
                                     cuenta_id=data["cuenta_id_%d" % i], forma_pago_id=data["forma_pago_id_%d" % i])
                        for egreso in data.getlist("egreso_%d" % i):
                                e = Egresos.query.get(egreso)
                                e.status = 'solicitado'
                                monto = e.monto_total - e.monto_pagado - e.monto_solicitado
                                e.monto_solicitado += monto
                                pago.beneficiario = e.beneficiario
                                ep = EgresosHasPagos(egreso=e, pago=pago, monto=monto)
                                db.session.add(ep)
                                db.session.commit()
                if ('url' in data):
                    return redirect(data["url"])
                else:
                    return redirect("/egresos/pagos_realizados")


### CONCILIAR PAGOS ###
#Conciliar pago data for modal
@blueprint.route('/get_data_conciliar<int:pago_id>', methods=['GET', 'POST'])
@login_required
def get_data_conciliar(pago_id):
        pago = Pagos.query.get(pago_id)
        return jsonify(pago_id=pago.id, beneficiario=pago.beneficiario.nombre, monto_total=str(pago.monto_total), referencia=pago.referencia_pago, cuenta=pago.cuenta.nombre)


#Conciliar pago form sumbit
@blueprint.route('/conciliar_movimento', methods=['GET', 'POST'])
@login_required
def conciliar_movimento():
        if request.form:
                data = request.form
                pagos = (data.getlist('pago_id'))
                for pago_id in pagos:
                        pago = Pagos.query.get(pago_id)
                        pago.status = 'conciliado'
                        pago.referencia_conciliacion = data["referencia"]
                        pago.fecha_conciliacion = data["fecha"]
                        pago.comentario = str(pago.comentario) + data["comentario"]
                        for egreso in pago.egresos:
                                ep = EgresosHasPagos.query.filter_by(
                                    egreso_id=egreso.id, pago_id=pago.id).first()
                                egreso.monto_por_conciliar -= ep.monto
                                if egreso.monto_total == egreso.monto_pagado and egreso.monto_por_conciliar == 0:
                                        egreso.status = 'liquidado'
                db.session.commit()
                if ('url' in data):
                    return redirect(data["url"])
                else:
                    return redirect("/egresos/pagos_realizados")

#Conciliar multiples pagos data for modal
@blueprint.route('/get_data_conciliar_multiple', methods=['GET', 'POST'])
@login_required
def get_data_conciliar_multiple():
        list = []
        pagos = request.args.getlist('pagos[]')
        for pago in pagos:
            p = Pagos.query.get(pago)
            list.append({'pago_id': p.id, 'beneficiario': p.beneficiario.nombre, 'monto_total': str(
                p.monto_total), 'referencia': p.referencia_pago, 'cuenta': p.cuenta.nombre})
        return jsonify(list)

### GENERAR PAGO ###
#Generar pago for modal
@blueprint.route('/get_data_generar_pago<int:pago_id>', methods=['GET', 'POST'])
@login_required
def get_data_generar_pago(pago_id):
        pago = Pagos.query.get(pago_id)
        return jsonify(pago_id=pago.id, beneficiario=pago.beneficiario.nombre,
                       monto_total=str(pago.monto_total), cuenta=pago.cuenta.nombre, forma_pago=pago.forma_pago.nombre,
                       referencia=pago.referencia_pago, numero_cheque=str(pago.cuenta.numero_cheque + 1), cuenta_beneficiario=pago.beneficiario.cuenta_banco)


# Generar pago form sumbit
@blueprint.route('/generar_pago', methods=['GET', 'POST'])
@login_required
def generar_pago():
        if request.form:
                data = request.form
                pago = Pagos.query.get(data["pago_id"])
                pago.referencia_pago = data["referencia_pago"]
                pago.fecha_pago = data["fecha_pago"]
                for egreso in pago.egresos:
                        ep = EgresosHasPagos.query.filter_by(
                            egreso_id=egreso.id, pago_id=pago.id).first()
                        egreso.monto_pagado += ep.monto
                        egreso.monto_solicitado -= ep.monto
                        if egreso.monto_pagado == egreso.monto_total:
                                egreso.pagado = True
                        if ('conciliado_check' in data):
                                pago.status = 'conciliado'
                                pago.referencia_conciliacion = data["referencia_conciliacion"]
                                if egreso.status != 'parcial' and egreso.monto_pagado == egreso.monto_total:
                                        egreso.status = 'liquidado'
                        else:
                                egreso.monto_por_conciliar += ep.monto
                                pago.status = 'por_conciliar'
                                if egreso.status != 'parcial' and egreso.monto_pagado == egreso.monto_total:
                                        egreso.status = 'por_conciliar'

                db.session.commit()
                if ('url' in data):
                    return redirect(data["url"])
                else:
                    return redirect("/egresos/pagos_realizados")


#Generar multiples pagos data for modal
@blueprint.route('/generar_pagos_multiple', methods=['GET', 'POST'])
@login_required
def generar_pagos_multiple():
        if request.form:
                cheque_counter = 0
                data = request.form
                pagos = (data.getlist('pago_id'))
                for pago_id in pagos:
                        pago = Pagos.query.get(pago_id)
                        if pago.forma_pago.nombre.lower() == 'cheque':
                                pago.referencia_pago = data.getlist('numero_cheque')[cheque_counter]
                                cheque_counter += 1
                                pago.cuenta.numero_cheque += 1
                                pago.fecha_pago = data["fecha_pago_cheque"]
                                pago.comentario = data["comentario_cheque"]
                        elif pago.forma_pago.nombre.lower() == 'transferencia':
                                pago.referencia_pago = data["referencia_pago_transferencia"]
                                pago.fecha_pago = data["fecha_pago_transferencia"]
                                pago.comentario = data["comentario_transferencia"]
                        else:
                                pago.referencia_pago = data["referencia_pago_efectivo"]
                                pago.fecha_pago = data["_efectivo"]
                                pago.comentario = data["comentario_efectivo"]
                        for egreso in pago.egresos:
                                ep = EgresosHasPagos.query.filter_by(
                                    egreso_id=egreso.id, pago_id=pago.id).first()
                                egreso.monto_pagado += ep.monto
                                egreso.monto_solicitado -= ep.monto
                                if egreso.monto_pagado == egreso.monto_total:
                                        egreso.pagado = True
                                egreso.monto_por_conciliar += ep.monto
                                pago.status = 'por_conciliar'
                                if egreso.status != 'parcial' and egreso.monto_pagado == egreso.monto_total:
                                        egreso.status = 'por_conciliar'

                db.session.commit()
                return redirect("/egresos/pagos_realizados")
# Generar pago multiple form sumbit
@blueprint.route('/get_data_generar_pagos_multiple', methods=['GET', 'POST'])
@login_required
def get_data_generar_pagos_multiple():
        list = []
        pagos = request.args.getlist('pagos[]')
        for pago in pagos:
            p = Pagos.query.get(pago)
            list.append({'pago_id': p.id, 'beneficiario': p.beneficiario.nombre, 'monto_total': str(p.monto_total), 'forma_pago': p.forma_pago.nombre,
                         'cuenta': p.cuenta.nombre, 'cuenta_id': str(p.cuenta.id), 'numero_cheque': str(p.cuenta.numero_cheque)})
        return jsonify(list)


#reprogramar_fecha
@blueprint.route('/reprogramar_fecha', methods=['GET', 'POST'])
@login_required
def reprogramar_fecha():
        if request.form:
                data = request.form
                egreso = Egresos.query.get(data["egreso_id"])
                egreso.fecha_programada_pago = data["fecha"]
                db.session.commit()
                if ('url' in data):
                    return redirect(data["url"])
                else:
                    return redirect("/egresos/cuentas_por_pagar")


#reprogramar fecha multiple
@blueprint.route('/reprogramar_fecha_multiple', methods=['GET', 'POST'])
@login_required
def reprogramar_fecha_multiple():
        egresos = request.args.getlist('egresos[]')
        fecha = request.args.get('fecha')
        for egreso in egresos:
                egreso = Egresos.query.get(egreso)
                egreso.fecha_programada_pago = fecha
        db.session.commit()
        if ('url' in data):
            return redirect(data["url"])
        else:
            return redirect("/egresos/cuentas_por_pagar")


### Detalles ###
#Agregar detalle al egreso
@blueprint.route('/agregar_detalle<int:egreso_id>', methods=['GET', 'POST'])
@login_required
def agregar_detalle(egreso_id):
        if request.form:
                egreso = Egresos.query.get(egreso_id)
                data = request.form
                detalle = DetallesEgreso(centro_negocios_id=data["centro_negocios"], proveedor_id=data["proveedor"], categoria_id=data["categoria"],
                                         concepto_id=data["concepto"], monto=data["monto"], numero_control=data["numero_control"], descripcion=data["comentario"])
                egreso.detalles.append(detalle)
                egreso.monto_total += int(detalle.monto)
                ######Checar el status y que hacer con pago negativo
                egreso.setStatus()
                db.session.commit()
                return redirect("/egresos/perfil_egreso/" + str(egreso_id))

#Ge data for editar detalle de egreso
@blueprint.route('/get_data_editar_detalle<int:detalle_id>', methods=['GET', 'POST'])
@login_required
def get_data_editar_detalle(detalle_id):
        detalle = DetallesEgreso.query.get(detalle_id)
        return jsonify(id=detalle.id, centro_negocios=detalle.centro_negocios_id, proveedor=detalle.proveedor_id, monto=str(detalle.monto),
                       categoria=detalle.categoria_id, concepto=detalle.concepto_id, numero_control=detalle.numero_control, descripcion=detalle.descripcion)

 #editar detalle de egreso
@blueprint.route('/editar_detalle<int:egreso_id>', methods=['GET', 'POST'])
@login_required
def editar_detalle(egreso_id):
        if request.form:
                data = request.form
                detalle = DetallesEgreso.query.get(data["id"])
                detalle.centro_negocios_id = data["centro_negocios"]
                detalle.proveedor_id = data["proveedor"]
                detalle.categoria_id = data["categoria"]
                detalle.concepto_id = data["concepto"]
                detalle.monto = data["monto"]
                detalle.numero_control = data["numero_control"]
                detalle.descripcion = data["comentario"]
                db.session.commit()
                return redirect("/egresos/perfil_egreso/" + str(egreso_id))


#Desconciliar Pago
@blueprint.route("/desconciliar_pago/<int:pago_id>", methods=['GET', 'POST'])
def desconciliar_pago(pago_id):
        pago = Pagos.query.get(pago_id)
        pago.status = 'por_conciliar'
        pago.referencia_conciliacion = None
        pago.fecha_conciliacion = None
        for egreso in pago.egresos:
                ep = EgresosHasPagos.query.filter_by(egreso_id=egreso.id, pago_id=pago.id).first()
                egreso.monto_por_conciliar += ep.monto
        db.session.commit()
        ### NO FUNCIONA
        for egreso in pago.egresos:
                egreso.setStatus()
        db.session.commit()
        return redirect("/egresos/pagos_realizados")


#Borrar Ep
@blueprint.route("/borrarEP/<int:egreso_id>/<int:pago_id>", methods=['GET', 'POST'])
def borrarEP(egreso_id, pago_id):
        egreso = Egresos.query.get(egreso_id)
        pago = Pagos.query.get(pago_id)
        ep = EgresosHasPagos.query.filter_by(egreso_id=egreso_id, pago_id=pago_id).first()
        egreso.monto_solicitado -= ep.monto
        pago.monto_total -= ep.monto
        db.session.delete(ep)
        egreso.setStatus()
        db.session.commit()
        return redirect("/egresos/perfil_pago/" + str(pago_id))


@blueprint.route('/get_beneficiario_categorias/<int:beneficiario_id>', methods=['GET', 'POST'])
def get_beneficiario_categorias(beneficiario_id):
  list = []
  categorias = Categorias.query.filter(Categorias.beneficiarios.any(id=beneficiario_id), Categorias.tipo=="egreso").all()
  for categoria in categorias:
    list.append({'id': categoria.id, 'nombre': categoria.nombre})
  return jsonify(list)

@blueprint.route('/get_concepto_categoria/<int:categoria_id>', methods=['GET', 'POST'])
def get_concepto_categoria(categoria_id):
  list = []
  conceptos = Conceptos.query.filter_by(categoria_id=categoria_id).all()
  for concepto in conceptos:
    list.append({'id': concepto.id, 'nombre': concepto.nombre})
  return jsonify(list)


@blueprint.route('/reembolso_egreso/<int:egreso_id>', methods=['GET', 'POST'])
def reembolso_egreso(egreso_id):
  if request.form:
    data = request.form
    egreso = Egresos.query.get(egreso_id)
    if ('parcial_reembolso' in data):
      monto = - Decimal(data["monto_parcial"])
    else:  
      monto = - egreso.monto_pagado

    egreso.monto_pagado += monto
    pago = Pagos(forma_pago_id=data["forma_pago"], cuenta_id=data["cuenta"], referencia_pago=data["referencia_pago"], fecha_pago=data["fecha_pago"], status='conciliado',
    fecha_conciliacion=data["fecha_pago"], monto_total=monto, comentario=data["comentario"], beneficiario_id=egreso.beneficiario_id)
    ep = EgresosHasPagos(egreso=egreso, pago=pago, monto=monto)

    if ('monto_documento' in data):
      egreso.monto_total += monto
      egreso.monto_documento += monto
      detalle = DetallesEgreso(centro_negocios_id=data["centro_negocios"], proveedor_id=data["proveedor"],
                                categoria_id=data["categoria"], concepto_id=data["concepto"], monto=monto,
                                numero_control='reembolso', descripcion=data["comentario"])
      egreso.detalles.append(detalle)
    db.session.add(ep)
    db.session.commit()
  return redirect("/egresos/perfil_egreso/" + str(egreso_id))

@blueprint.route('/generar_cheque/<int:pago_id>', methods=['GET', 'POST'])
def generar_cheque(pago_id):
        pago = Pagos.query.get(pago_id)
        pago.referencia_pago = pago.cuenta.numero_cheque
        pago.cuenta.numero_cheque += 1
        pago.fecha_pago = date.today()
        for egreso in pago.egresos:
                ep = EgresosHasPagos.query.filter_by(
                        egreso_id=egreso.id, pago_id=pago.id).first()
                egreso.monto_pagado += ep.monto
                egreso.monto_solicitado -= ep.monto
                if egreso.monto_pagado == egreso.monto_total:
                        egreso.pagado = True
                egreso.monto_por_conciliar += ep.monto
                pago.status = 'por_conciliar'
                if egreso.status != 'parcial' and egreso.monto_pagado == egreso.monto_total:
                        egreso.status = 'por_conciliar'

        db.session.commit()
        return(chequePDF(pago.fecha_pago, pago.monto_total, pago.beneficiario.razon_social, pago.egresos, pago.referencia_pago, pago.id ))
                
@blueprint.route('/imprimir_cheque/<int:pago_id>', methods=['GET', 'POST'])
def imprimir_cheque(pago_id):
    pago = Pagos.query.get(pago_id)
    return(chequePDF(pago.fecha_pago, pago.monto_total, pago.beneficiario.razon_social, pago.egresos, pago.referencia_pago, pago.id ))


#ver notas
@blueprint.route('/notas_credito', methods=['GET', 'POST'])
def notas_credito():
    notas = NotasCredito.query.all()
    return render_template("notas_credito.html", notas=notas)

#ver notas
@blueprint.route('/perfil_nota/<int:nota_id>', methods=['GET', 'POST'])
def perfil_nota(nota_id):
    nota = NotasCredito.query.get(nota_id)
    return render_template("perfil_nota.html", nota=nota)
#crear notas de credito
@blueprint.route('/nota_credito/<int:egreso_id>"', methods=['GET', 'POST'])
def nota_credito(egreso_id):
    if request.form:
        data = request.form
        egresoQB =Egresos.query.get(egreso_id)
        nota_credito = NotasCredito(egreso_QB_id=egreso_id, aplicado = False, monto=data["monto"], numero_documento = data["numero_documento"], comentario=data["comentario"], fecha=data["fecha"], beneficiario =egresoQB.beneficiario )
        if "aplicar_check" in data:
            nota_credito.aplicado = True
            nota_credito.egreso_WR_id = data["egresoWR"]
            egresoWR = Egresos.query.get(data["egresoWR"])
            egresoWR.monto_total -=  Decimal(nota_credito.monto)
       
        if "generar_reembolso_check" in data:
            monto = - Decimal(data["monto"])
            pago = Pagos(forma_pago_id=data["forma_pago"], cuenta_id=data["cuenta"], referencia_pago=data["numero_documento"], fecha_pago=data["fecha"], status='conciliado',
            fecha_conciliacion=data["fecha"], monto_total=monto, comentario=data["comentario"], beneficiario_id=egresoQB.beneficiario_id)
            ep = EgresosHasPagos(egreso=egresoWR, pago=pago, monto=monto)
            db.session.add(ep)
        db.session.add(nota_credito)
        db.session.commit()
    return redirect("/egresos/perfil_egreso/" + str(egreso_id))


from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import portrait
from PyPDF2 import PdfFileWriter, PdfFileReader
from io import StringIO
from num2words import num2words

def chequePDF(fecha, monto, beneficiario, egresos, numero, pago_id):
    cv = canvas.Canvas('app/cheque' +str(numero) +'.pdf')

    # Horizontal, Vertical

    #create a string
    cv.drawString(390, 770, str(fecha))

    # Fila 2
    cv.drawString(30, 710, str(beneficiario))
    cv.drawString(430, 710, str(monto))

    #Fila 3
    cv.drawString(30, 690, num2words(monto, lang='es').upper() + ' PESOS 00/100 M.N.')

    #Fila 3
    offset = 0
    for egreso in egresos:
        ep =  EgresosHasPagos.query.filter_by(egreso_id=egreso.id, pago_id=pago_id).first() 
        cv.drawString(160 + offset, 500 - offset, ' | # de documento: ' + str(egreso.numero_documento))
        cv.drawString(400, 500 - offset, '$' + str(ep.monto))
        offset += 20

    #Fila 5
    cv.drawString(400, 200, str(monto))

    #Fila 6
    cv.drawString(360, 180, str(numero))

    cv.save()
    return send_file('cheque' +str(numero) +'.pdf' , as_attachment=True)

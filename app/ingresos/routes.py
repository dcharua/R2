from app.ingresos import blueprint
from flask import render_template, request, redirect, flash, jsonify
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from datetime import datetime
from app.db_models.models import *
import decimal

@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')



def calcular_saldo_cliente(cliente_id):
    
    cliente = Clientes.query.get(cliente_id)
    print('Cliente = ',cliente)
    ingresos = cliente.ingresos
    saldo_pendiente = 0
    saldo_por_conciliar = 0
    saldo_cobrado = 0
    
    for ingreso in ingresos:        
        monto_total,monto_pagado,monto_por_conciliar = float(ingreso.monto_total),float(ingreso.monto_pagado),float(ingreso.monto_por_conciliar)
        if ingreso.status == 'cancelado':
            monto_por_conciliar = 0
            monto_total = monto_pagado
        saldo_pendiente += (monto_total - monto_pagado - monto_por_conciliar)
        saldo_por_conciliar += monto_por_conciliar
        saldo_cobrado += monto_pagado
    
    cliente.saldo_cobrado = saldo_cobrado
    cliente.saldo_por_conciliar = saldo_por_conciliar
    cliente.saldo_pendiente = saldo_pendiente
    
    if saldo_pendiente > 0: cliente.status = 'pendiente'
    elif saldo_por_conciliar > 0 and saldo_pendiente == 0: cliente.status = 'por_conciliar'
    else: cliente.status = 'conciliado'
    
    db.session.add(cliente)  
    db.session.commit()

@blueprint.route('/capturar_ingreso', methods=['GET', 'POST'])
def captura_ingresos():
    
    
    if request.form:
        data = request.form
        montos = list(map(float, data.getlist("monto")))
        monto_total = float(sum(montos))

        
        ingreso = Ingresos(cliente_id = data["cliente"],
                           tipo_ingreso_id = data["tipo_ingreso"],
                           fecha_vencimiento = data["fecha_vencimiento"], 
                           numero_documento = data["numero_documento"],
                           empresa_id = data["empresa"],
                           referencia = data["referencia"],
                           monto_total = monto_total, comentario = data["comentario"],pagado = False,      
                           status = "pendiente", monto_pagado = 0, monto_solicitado = 0,monto_por_conciliar = 0) 
        if (data["fecha_programada_pago"] != ""):
            ingreso.fecha_programada_pago = data["fecha_programada_pago"]                                                                             

        if ('pagado' in data):
            if ('conciliado_check' in data):                
                monto_pagado,monto_por_conciliar,pagado = float(data["monto_pagado"]), 0, True
                if monto_pagado == monto_total: status_ingreso = 'conciliado'
                else: status_ingreso = 'parcial'
                status_pago = 'conciliado'
                
            else:                
                status_pago = 'por_conciliar'
                monto_pagado,monto_por_conciliar,pagado = 0,float(data["monto_pagado"]),False
                if monto_por_conciliar == monto_total: status_ingreso = 'por_conciliar'
                else: status_ingreso = 'pendiente'
                

            ingreso = Ingresos(cliente_id = data["cliente"],
                           tipo_ingreso_id = data["tipo_ingreso"],
                           fecha_vencimiento = data["fecha_vencimiento"], 
                           numero_documento = data["numero_documento"],
                           empresa_id = data["empresa"],
                           referencia = data["referencia"],
                           monto_total = monto_total, comentario = data["comentario"],pagado = pagado,      
                           status = status_ingreso, monto_pagado = monto_pagado, monto_solicitado = 0, monto_por_conciliar = monto_por_conciliar)
            if (data["fecha_programada_pago"] != ""):
                ingreso.fecha_programada_pago = data["fecha_programada_pago"]  
               
            
            pago_ingreso = Pagos_Ingresos(status = status_pago, cliente_id = data["cliente"], 
                                  monto_total = float(data["monto_pagado"]), cuenta_id = int(data["cuenta_id"]), 
                                  fecha_pago = data["fecha_pago"], 
                                  comentario = data["comentario_pago"],
                                  forma_pago_id = data["forma_pago"],
                                  referencia_pago = data["referencia_pago"],
                                  fecha_conciliacion = data["fecha_pago"],
                                  referencia_conciliacion = data["referencia"],
                                  )

            ep = IngresosHasPagos(ingreso = ingreso, pago = pago_ingreso, monto = float(data["monto_pagado"]))    
        

            db.session.add(ep)
            db.session.add(pago_ingreso)
            
        for i in range(len(data.getlist("monto"))):           
            detalle = DetallesIngreso(cliente_id = data["cliente"],
                                      categoria_id = data.getlist("categoria")[i], 
                                      concepto_id = data.getlist("concepto")[i], 
                                      centro_negocios_id = data.getlist("centro_negocios")[i], 
                                      monto = data.getlist("monto")[i], 
                                      numero_control = data.getlist("numero_control")[i], 
                                      descripcion=data.getlist("descripcion")[i])
            ingreso.detalles.append(detalle)
        
        
        
            
        print('Linea 90')
        db.session.add(ingreso)  
        print('Linea 92')
        db.session.commit()
        calcular_saldo_cliente(data["cliente"])
        
        return redirect("/ingresos/cuentas_por_cobrar")
    
    clientes = Clientes.query.all()
    empresas = Empresas.query.all()
    centros_negocios = CentrosNegocio.query.all()
    categorias = Categorias.query.all()
    conceptos = Conceptos.query.all()
    cuentas_banco = Cuentas.query.all()
    formas_pago = FormasPago.query.all()
    tipo_ingreso = Tipo_Ingreso.query.all()
    

    return render_template("capturar_ingreso.html",
                           navbar_data_capture = 'active',
                           title = "aaaRegistro de ingresos",
                           tipo_ingreso = tipo_ingreso,
                           clientes = clientes,
                           categorias  = categorias,
                           conceptos = conceptos,
                           cuentas_banco = cuentas_banco,
                           centros_negocios = centros_negocios,
                           formas_pago = formas_pago,        
                           empresas = empresas,
                           velocity_max = 1)


@blueprint.route('/cuentas_por_cobrar', methods=['GET', 'POST'])
def cuentas_por_cobrar():
    print(Ingresos.query.all())
    ingresos_recibidos = Ingresos.query.filter(Ingresos.status == 'conciliado').all()
    ingresos_pendientes = Ingresos.query.filter(Ingresos.status != 'conciliado').filter(Ingresos.status != 'cancelado').all()
    ingresos_cancelados = Ingresos.query.filter(Ingresos.status == 'cancelado').all()
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()
    return render_template("cuentas_por_cobrar.html", ingresos_recibidos = ingresos_recibidos, ingresos_pendientes = ingresos_pendientes, formas_pago = formas_pago, cuentas=cuentas)


#Egresos perfil
@blueprint.route('/perfil_ingreso/<int:ingreso_id>', methods=['GET', 'POST'])
def perfil_ingreso(ingreso_id):
    ingreso = Ingresos.query.get(ingreso_id)
    clientes = Clientes.query.all()
    centros_negocio = CentrosNegocio.query.all()
    categorias = Categorias.query.all()
    conceptos = Conceptos.query.all()
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()
    empresas = Empresas.query.all()
        
    
    return render_template("perfil_ingreso.html", 
                           ingreso = ingreso, 
                           centros_negocio = centros_negocio, 
                           clientes = clientes, 
                           categorias = categorias, 
                           conceptos = conceptos,
                           formas_pago = formas_pago, 
                           cuentas=cuentas,
                           empresas=empresas)


#Ingresos Edit
@blueprint.route('/editar_ingreso/<int:ingreso_id>"', methods=['GET', 'POST'])
def editar_ingreso(ingreso_id):
    if request.form:
        data = request.form
        ingreso = Ingresos.query.get(ingreso_id)
        if "cliente" in data:
            ingreso.cliente_id =  data["cliente"]
        ingreso.empresa_id =  data["empresa"]
        if  data["fecha_programada_pago"]:
            ingreso.fecha_programada_pago = data["fecha_programada_pago"]
        ingreso.fecha_vencimiento = data["fecha_vencimiento"]
        ingreso.referencia = data["referencia"]
        ingreso.numero_documento = data["numero_documento"]
        ingreso.comentario = data["comentario"]
        db.session.commit()
    return redirect("/ingresos/perfil_ingreso/" + str(ingreso_id))
    

#Egresos Delete
@blueprint.route("/borrar_ingreso/<int:ingreso_id>",  methods=['GET', 'POST'])
def borrar_ingreso(ingreso_id):
    print('En Borrar Ingreso!')
    ingreso = Ingresos.query.get(ingreso_id)
    db.session.delete(ingreso)
    db.session.commit()
    calcular_saldo_cliente(ingreso.cliente_id)
    return  jsonify("deleted")

#Ingresos Cancelar
@blueprint.route("/cancelar_ingreso/<int:ingreso_id>",  methods=['GET', 'POST'])
def cancelar_ingreso(ingreso_id):
    ingreso = Ingresos.query.get(ingreso_id)
    ingreso.status ='cancelado'
    db.session.commit()
    calcular_saldo_cliente(ingreso.cliente_id)
    print(ingreso)
    return  jsonify("deleted")


##### PAGOS ROUTES  #########

#pagos tablas
@blueprint.route('/pagos_recibidos', methods=['GET', 'POST'])
def pagos_recibidos():
    pagos = Pagos_Ingresos.query.filter(Pagos_Ingresos.status == 'solicitado').all()
    pagos_recibidos = Pagos_Ingresos.query.filter(Pagos_Ingresos.status != 'solicitado').all()
    return render_template("pagos_recibidos.html", pagos=pagos, pagos_recibidos=pagos_recibidos)

#perfil pago
@blueprint.route('/perfil_pago_ingreso/<int:pago_id>', methods=['GET', 'POST'])
def perfil_pago_ingreso(pago_id):
    pago = Pagos_Ingresos.query.get(pago_id)  
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()  
    
    return render_template("perfil_pago_ingreso.html", pago=pago, formas_pago = formas_pago, cuentas=cuentas)

###### Borrar pago
@blueprint.route("/borrar_pago/<int:pago_id>",  methods=['GET', 'POST'])
def borrar_pago(pago_id):
    pago = Pagos_Ingresos.query.get(pago_id)
    for ingreso in pago.ingresos:
        ep = IngresosHasPagos.query.filter_by(ingreso_id  = ingreso.id ,pago_id = pago.id ).first()
        ingreso.monto_por_conciliar -= ep.monto
        ingreso.setStatus()
        calcular_saldo_cliente(ingreso.cliente_id)
        db.session.delete(ep)
    db.session.delete(pago)
    db.session.commit()
    return  jsonify("deleted")


###### Cancelar pago
@blueprint.route("/cancelar_pago_ingreso/<int:pago_id>",  methods=['GET', 'POST'])
def cancelar_pago_ingreso(pago_id):
    
    pago = Pagos_Ingresos.query.get(pago_id)
    
    for ingreso in pago.ingresos:
        ep = IngresosHasPagos.query.filter_by(ingreso_id=ingreso.id , pago_id = pago.id ).first()
        if pago.status == 'conciliado':
            ingreso.monto_pagado -= ep.monto
        if pago.status == 'por_conciliar':
            ingreso.monto_por_conciliar -= ep.monto
        ep.monto = 0
        ingreso.pagado = False   
        
    pago.status = 'cancelado'
    db.session.commit()
    
    for ingreso in pago.ingresos:
        ingreso.setStatus()
        calcular_saldo_cliente(ingreso.cliente_id)
        
    db.session.commit()
    
    return  jsonify("deleted")

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
    return redirect("/ingresos/perfil_pago_ingreso/" + str(pago_id))


###########MODALES  ###########
#####  SOLICITAR PAGO #######
#Solicitar pago data for modal
@blueprint.route('/get_data_pagar<int:ingreso_id>', methods=['GET', 'POST'])
@login_required
def get_data_pagar(ingreso_id):
        ingreso = Ingresos.query.get(ingreso_id)   

        return jsonify(ingreso_id = ingreso.id, cliente = str(ingreso.cliente.nombre), monto_total = str(ingreso.monto_total), 
        monto_pagado = str(ingreso.monto_pagado),monto_por_conciliar = str(ingreso.monto_por_conciliar), numero_documento = ingreso.numero_documento)


# Solcitar pago form submit
@blueprint.route('/mandar_cobrar', methods=['GET', 'POST'])
@login_required
def mandar_cobrar():

    if request.form:
        data = request.form
        ingreso = Ingresos.query.get(data["ingreso_id"])
        
        if ('conciliado_check' in data):
            status_pago = 'conciliado'
    
            if ('parcial' in data):
                monto_total_pago = float(data["monto_parcial"]) if data["monto_parcial"] != '' else 0
            else:
                monto_total_pago = float(ingreso.monto_total - ingreso.monto_pagado - ingreso.monto_por_conciliar)
                            
            ingreso.monto_pagado = float(ingreso.monto_pagado) + monto_total_pago 
            ingreso.setStatus()
            status_pago = 'conciliado'
            fecha_conciliacion = datetime.now()
            
        else:
            
            if ('parcial' in data):
                monto_total_pago = float(data["monto_parcial"])
            else:
                monto_total_pago = float(ingreso.monto_total - ingreso.monto_pagado - ingreso.monto_por_conciliar)
            
            status_pago = 'por_conciliar'
            ingreso.monto_por_conciliar = float(ingreso.monto_por_conciliar) + monto_total_pago
            ingreso.setStatus()
            fecha_conciliacion = None
        if 'referencia_conciliacion' in data: referencia_conciliacion = data["referencia_conciliacion"]
        else: referencia_conciliacion = ''
                
        pago = Pagos_Ingresos(status = status_pago , cliente = ingreso.cliente, fecha_pago = datetime.now(),
                              fecha_conciliacion = fecha_conciliacion, monto_total = monto_total_pago, 
                              cuenta_id = data["cuenta_id"], forma_pago_id = data["forma_pago_id"],
                              referencia_pago = data["ingreso_id"],
                              referencia_conciliacion = referencia_conciliacion)
      
        ep = IngresosHasPagos(ingreso = ingreso, pago = pago, monto = monto_total_pago)    

                
        calcular_saldo_cliente(ingreso.cliente_id)

        db.session.add(ep)
        db.session.add(pago)
        db.session.commit()
        
        return  redirect("/ingresos/perfil_ingreso/"+str(ingreso.id))  


# Solicitar multiples pagos data for modal 
@blueprint.route('/get_data_pagar_multiple', methods=['GET', 'POST'])
@login_required
def get_data_pagar_multiple():
    list = []
    ingresos = request.args.getlist('ingresos[]')
    for ingreso in ingresos:
            ing = Ingresos.query.get(ingreso)
            monto_pendiente = ing.monto_total - ing.monto_por_conciliar - ing.monto_pagado
            list.append({'ingreso_id': ing.id, 'cliente': ing.cliente.nombre, 'monto_total': str(monto_pendiente), 'numero_documento': ing.numero_documento})
    return jsonify(list)



#Solicitar pago from sumbit
@blueprint.route('/mandar_cobrar_multiple', methods=['GET', 'POST'])
@login_required
def mandar_cobrar_multiple():
        if request.form:
                data = request.form
                for i in range(int(data["cantidad"])):
                    
                    pago = Pagos_Ingresos(status='por_conciliar', monto_total=data["monto_total_%d" % i], fecha_pago = datetime.now(),
                                            cuenta_id=data["cuenta_id_%d" % i], forma_pago_id=data["forma_pago_id_%d" % i])

                    for ingreso in data.getlist("ingreso_%d" % i):
                            ing = Ingresos.query.get(ingreso)
                            monto_total_pago = float(ing.monto_total - ing.monto_pagado - ing.monto_por_conciliar)
                            ing.monto_por_conciliar += decimal.Decimal(monto_total_pago)
                            ing.setStatus()
                            ep = IngresosHasPagos(ingreso = ing, pago = pago, monto = monto_total_pago)
                            pago.cliente_id = ing.cliente_id
                            db.session.add(ep)
                            db.session.commit()
                            calcular_saldo_cliente(ing.cliente_id)
                    
                    
                    

                return  redirect("/ingresos/cuentas_por_cobrar")   



### CONCILIAT PAGOS ###
#Conciliar pago data for modal
@blueprint.route('/get_data_conciliar_pago_ingreso<int:pago_id>', methods=['GET', 'POST'])
@login_required
def get_data_conciliar_pago_ingreso(pago_id):
        pago_ingreso = Pagos_Ingresos.query.get(pago_id)
        return jsonify(pago_id = pago_id, cliente = pago_ingreso.cliente.nombre, monto_total=str(pago_ingreso.monto_total), referencia = pago_ingreso.referencia_pago , cuenta=pago_ingreso.cuenta.nombre)

@blueprint.route('/get_data_conciliar<int:ingreso_id>', methods=['GET', 'POST'])
@login_required
def get_data_conciliar(ingreso_id):
        ingreso = Ingresos.query.get(ingreso_id)
        return jsonify(ingreso_id = ingreso.id, cliente = str(ingreso.cliente.nombre),empresa = ingreso.empresa.nombre, monto_total=str(ingreso.monto_total), num_documento = ingreso.numero_documento )


#Conciliar pago form sumbit
@blueprint.route('/conciliar_pago_ingreso', methods=['GET', 'POST'])
@login_required
def conciliar_pago_ingreso():
        if request.form:
            data = request.form
            print(data)
            pagos = (data.getlist('pago_id'))
            print('PAGOS = ',pagos)

            for pago_id in pagos:
                pago = Pagos_Ingresos.query.get(pago_id)
                pago.status = 'conciliado';
                pago.referencia_conciliacion = data["referencia"]
                pago.fecha_conciliacion = data["fecha"]
                pago.comentario = data["comentario"]

                print('Pago ID = ',pago.id)            
                ep = IngresosHasPagos.query.filter_by(pago_id = pago.id)
                print(type(ep))
                print(list(ep))

                for p in list(ep):
                    print('ingros_has_pago = ',p)
                    print('-Id = ',p.ingreso_id)
                    print('-Monto = ',p.monto)


                    ingreso = Ingresos.query.get(p.ingreso_id)

                    ingreso.monto_por_conciliar -= p.monto
                    print('ingreso.monto_pagado = ',ingreso.monto_pagado)
                    ingreso.monto_pagado += p.monto
                    print('ingreso.monto_pagado = ',ingreso.monto_pagado)

                    ingreso.setStatus()
                    calcular_saldo_cliente(ingreso.cliente_id)
                    db.session.commit()
                    
            return  redirect("/ingresos/perfil_ingreso/"+str(ingreso.id))  
        
#Desconciliar Pago
@blueprint.route("/desconciliar_pago_ingreso/<int:pago_id>",  methods=['GET', 'POST'])
def desconciliar_pago_ingreso(pago_id):
        pago = Pagos_Ingresos.query.get(pago_id)
        pago.status = 'por_conciliar'
        pago.referencia_conciliacion = None
        pago.fecha_conciliacion = None
        db.session.commit()
        
        for ingreso in pago.ingresos:
            ep = IngresosHasPagos.query.filter_by(ingreso_id=ingreso.id , pago_id = pago.id).first()
            ingreso.monto_por_conciliar += ep.monto
            ingreso.monto_pagado -= ep.monto
            ingreso.setStatus() 
            calcular_saldo_cliente(ingreso.cliente_id)
        db.session.commit()
        
        return  redirect("/ingresos/cuentas_por_cobrar")       

    
    #Conciliar pago form sumbit
@blueprint.route('/conciliar_ingreso', methods=['GET', 'POST'])
@login_required
def conciliar_ingreso():
        print('En conciliar_ingreso!')
        
        if request.form:
            data = request.form
            ingreso = Ingresos.query.get(data["ingreso_id"])
            pagos = ingreso.pagos_ingresos

            for pago in pagos:
                pago = Pagos_Ingresos.query.get(pago.id)
                pago.status = 'conciliado';
                pago.referencia_conciliacion = data["referencia"]
                pago.fecha_pago = data["fecha"]
                pago.fecha_conciliacion = data["fecha"]
                pago.comentario = data["comentario"]
                
                ep = IngresosHasPagos.query.filter_by(pago_id = pago.id ).first()
                ingreso.monto_por_conciliar -= ep.monto
                ingreso.monto_pagado += ep.monto
     
            ingreso.setStatus()
            calcular_saldo_cliente(ingreso.cliente_id)
            db.session.commit()
            return  redirect("/ingresos/perfil_ingreso/"+str(ingreso.id))   

#Conciliar multiples pagos data for modal
@blueprint.route('/get_data_conciliar_multiple', methods=['GET', 'POST'])
@login_required
def get_data_conciliar_multiple():
        list = []
        pagos = request.args.getlist('pagos[]')
        print('HERE!')
        for pago in pagos:
            print(pago)
            p =  Pagos_Ingresos.query.get(pago)
            list.append({'pago_id': p.id, 'cliente': p.cliente.nombre, 'monto_total': str(p.monto_total), 'referencia': p.referencia_pago, 'cuenta': p.cuenta.nombre})
        return jsonify(list)

### GENERAR PAGO ###
#Generar pago for modal
@blueprint.route('/get_data_generar_pago_ingreso<int:pago_id>', methods=['GET', 'POST'])
@login_required
def get_data_generar_pago_ingreso(pago_id):
        pago = Pagos_Ingresos.query.get(pago_id)
        return jsonify(pago_id = pago.id, cliente = pago.cliente.nombre, 
                       monto_total = str(pago.monto_total), cuenta = pago.cuenta.nombre, forma_pago = pago.forma_pago.nombre, 
                       referencia = pago.referencia_pago, numero_cheque = str(pago.cuenta.numero_cheque + 1), 
                       cuenta_cliente=pago.cliente.cuenta_banco)     
 
       


#reprogramar_fecha
@blueprint.route('/reprogramar_fecha', methods=['GET', 'POST'])
@login_required
def reprogramar_fecha():
        if request.form:
            data = request.form
            print(data)
            ingreso = Ingresos.query.get(data["ingreso_id"])
            print(ingreso)
            ingreso.fecha_programada_pago = data["fecha"]
            db.session.commit()
            return redirect("/ingresos/cuentas_por_cobrar")


#reprogramar fecha multiple
@blueprint.route('/reprogramar_fecha_multiple', methods=['GET', 'POST'])
@login_required
def reprogramar_fecha_multiple():      
        ingresos = request.args.getlist('ingresos[]')
        print(ingresos)
        fecha = request.args.get('fecha')
        for ingreso in ingresos:
            ingreso = Ingresos.query.get(ingreso)
            ingreso.fecha_programada_pago=fecha
        db.session.commit()
        return redirect("/ingresos/cuentas_por_cobrar")


@blueprint.route('/ingresos_tiendas', methods=['GET', 'POST'])
def ingresos_tiendas():
    ingresos_recibidos = Ingresos.query.filter(Ingresos.status == 'conciliado').all()
    ingresos_pendientes = Ingresos.query.filter(Ingresos.status != 'conciliado').all()
    ingresos_cancelados = Ingresos.query.filter(Ingresos.status == 'cancelado').all()
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()
    return render_template("ingresos_tiendas.html", 
                        ingresos_recibidos = ingresos_recibidos,
                        ingresos_pendientes = ingresos_pendientes, 
                        formas_pago = formas_pago, 
                        cuentas=cuentas)

    

    
@blueprint.route('/agregar_detalle<int:ingreso_id>', methods=['GET', 'POST'])
@login_required
def agregar_detalle(ingreso_id):
        if request.form:
            ingreso = Ingresos.query.get(ingreso_id)
            data = request.form
            detalle = DetallesIngreso(centro_negocios_id=data["centro_negocios"], cliente_id=data["cliente"], categoria_id=data["categoria"], 
            concepto_id=data["concepto"], monto=data["monto"],  numero_control=data["numero_control"], descripcion=data["comentario"])
            ingreso.detalles.append(detalle)
            ingreso.monto_total += int(detalle.monto);
            #Checar el status y que hacer con pago negativo
            ingreso.setStatus()
            db.session.commit()
            calcular_saldo_cliente(ingreso.cliente_id)
            return redirect("/ingresos/perfil_ingreso/"+str(ingreso_id))
    

#Ge data for editar detalle de Ingreso
@blueprint.route('/get_data_editar_detalle<int:detalle_id>', methods=['GET', 'POST'])
@login_required
def get_data_editar_detalle(detalle_id):

    detalle = DetallesIngreso.query.get(detalle_id)
    print('ID = ',detalle.id)
    print('centro_negocios=',detalle.centro_negocios_id)
    print('cliente=',detalle.cliente_id)
    print('monto=',str(detalle.monto))
    print('categoria =',detalle.categoria_id)
    print('concepto=',detalle.concepto_id)
    print('numero_control=',detalle.numero_control)
    print('descripcion=',detalle.descripcion)
    

    return jsonify(id = detalle.id, centro_negocios = detalle.centro_negocios_id, 
                       cliente=detalle.cliente_id,  monto=str(detalle.monto), 
                       categoria = detalle.categoria_id , concepto=detalle.concepto_id, 
                       numero_control=detalle.numero_control, descripcion = detalle.descripcion)



 #Ge data for editar detalle de Ingreso
@blueprint.route('/editar_detalle<int:ingreso_id>', methods=['GET', 'POST'])
@login_required
def editar_detalle(ingreso_id):
        if request.form:
                data = request.form
                detalle = DetallesIngreso.query.get(data["id"])
                detalle. centro_negocios_id=data["centro_negocios"] 
                detalle.cliente_id = data["cliente"]
                detalle.categoria_id = data["categoria"]
                detalle.concepto_id = data["concepto"]
                detalle.monto = data["monto"]  
                detalle.numero_control = data["numero_control"]
                detalle.descripcion = data["comentario"]
                db.session.commit()
                return redirect("/ingresos/perfil_ingreso/"+str(ingreso_id))
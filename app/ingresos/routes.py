from app.ingresos import blueprint
from flask import render_template, request, redirect, flash, jsonify
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')



@blueprint.route('/capturar_ingreso', methods=['GET', 'POST'])
def captura_ingresos():
    
    
    if request.form:
        data = request.form
        montos = list(map(int, data.getlist("monto")))
        monto_total = float(sum(montos))

        
        ingreso = Ingresos(cliente_id = data["cliente"],
                           tipo_ingreso_id = data["tipo_ingreso"],
                           fecha_vencimiento = data["fecha_vencimiento"], 
                           fecha_programada_pago = data["fecha_programada_pago"],
                           numero_documento = data["numero_documento"],
                           empresa_id = data["empresa"],
                           referencia = data["referencia"],
                           monto_total = monto_total, comentario = data["comentario"],pagado = False,      
                           status = "pendiente", monto_pagado = 0, monto_solicitado = 0,monto_por_conciliar = 0)                                                                                
        
            
        print(data)  
            
        if ('pagado' in data):
            monto_pagado = float(data["monto_pagado"])
            
            if ('conciliado_check' in data):
                status_ingreso = 'conciliado'
                status_pago = 'conciliado'            
                
            else:
                if monto_pagado == monto_total: status_ingreso = 'por_conciliar'
                else: status_ingreso = 'por_conciliar'
                status_pago = 'por_conciliar'


            ingreso = Ingresos(cliente_id = data["cliente"],
                           tipo_ingreso_id = data["tipo_ingreso"],
                           fecha_vencimiento = data["fecha_vencimiento"], 
                           fecha_programada_pago = data["fecha_programada_pago"],
                           numero_documento = data["numero_documento"],
                           empresa_id = data["empresa"],
                           referencia = data["referencia"],
                           monto_total = monto_total, comentario = data["comentario"],pagado = True,      
                           status = status_ingreso, monto_pagado = monto_pagado, monto_solicitado = 0, monto_por_conciliar = monto_total - monto_pagado)
               
            
            print('Linea 63')
            try:
                pago_ingreso = Pagos_Ingresos(status = status_pago, cliente_id = data["cliente"], 
                                  monto_total = monto_pagado, cuenta_id = data["cuenta_id"], 
                                  fecha_pago = data["fecha_pago"], fecha_conciliacion = data["fecha_pago"],
                                  comentario = data["comentario_pago"],
                                  forma_pago_id = data["forma_pago"],referencia_pago = data["referencia_pago"],
                                  referencia_conciliacion = data["referencia_conciliacion"]
                                  )
            except:
                print('linea 73')
                pago_ingreso = Pagos_Ingresos(status = 'conciliado', cliente_id = (data["cliente"]), 
                                  monto_total = monto_pagado, cuenta_id = int(data["cuenta_id"]), 
                                  fecha_pago = data["fecha_pago"],
                                  comentario = data["comentario_pago"],
                                  forma_pago_id = int(data["forma_pago"])
                                  )
      

            print('Linea 90')

            ep = IngresosHasPagos(ingreso = ingreso, pago = pago_ingreso, monto = monto_total)    
        

            print('Linea 85')
            db.session.add(ep)
            print('Linea 87')
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

@blueprint.route('/ingresos_recibidos', methods=['GET', 'POST'])
def ingresos_recibidos():
    ingresos_pagados = Ingresos.query.filter(Ingresos.pagado == True).all()
    ingresos_pendientes = Ingresos.query.filter(Ingresos.pagado == False).all()
    formas_pago = FormasPago.query.all()
    cuentas = Cuentas.query.all()
    return render_template("ingresos_recibidos.html", ingresos_pagados = ingresos_pagados, ingresos_pendientes = ingresos_pendientes, formas_pago = formas_pago, cuentas=cuentas)



@blueprint.route('/cuentas_por_cobrar', methods=['GET', 'POST'])
def cuentas_por_cobrar():
    print(Ingresos.query.all())
    ingresos_recibidos = Ingresos.query.filter(Ingresos.status == 'conciliado').all()
    ingresos_pendientes = Ingresos.query.filter(Ingresos.pagado == False).filter(Ingresos.status != 'cancelado').all()
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
    
    pagos = ingreso.pagos_ingresos
    print(type(pagos))
    pagos_por_conciliar = []
    pagos_conciliados = []
    for pago in pagos:
        if pago.status == 'conciliado': pagos_conciliados.append(pago)
        else: pagos_por_conciliar.append(pago)
        
    
    return render_template("perfil_ingreso.html", 
                           ingreso = ingreso, 
                           centros_negocio = centros_negocio, 
                           clientes = clientes, 
                           categorias = categorias, 
                           pagos_por_conciliar = pagos_por_conciliar,
                           pagos_conciliados = pagos_conciliados)


#Egresos Edit   
@blueprint.route('/editar_ingreso/<int:ingreso_id>"', methods=['GET', 'POST'])
def editar_ingreso(ingreso_id):
    return redirect("/")
    

#Egresos Delete
@blueprint.route("/borrar_ingreso/<int:ingreso_id>",  methods=['GET', 'POST'])
def borrar_ingreso(ingreso_id):
    ingreso = Ingresos.query.get(ingreso_id)
    db.session.delete(ingreso)
    db.session.commit()
    return  jsonify("deleted")

#Egresos Delete
@blueprint.route("/cancelar_ingreso/<int:ingreso_id>",  methods=['GET', 'POST'])
def cancelar_ingreso(ingreso_id):
    ingreso = Ingresos.query.get(ingreso_id)
    ingreso.status ='cancelado'
    db.session.commit()
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
@blueprint.route('/perfil_pago/<int:pago_id>', methods=['GET', 'POST'])
def perfil_pago(pago_id):
    pago = Pagos_Ingresos.query.get(pago_id)    
    return render_template("perfil_pago.html", pago=pago)
   


###### Borrar pago
@blueprint.route("/borrar_pago/<int:pago_id>",  methods=['GET', 'POST'])
def borrar_pago(pago_id):
    pago = Pagos_Ingresos.query.get(pago_id)
    for ingreso in pago.ingresos:
        ep = IngresosHasPagos.query.filter_by(ingreso_id  =ingreso.id ,pago_id = pago.id ).first()
        ingreso.monto_solicitado -= ep.monto
        if ingreso.monto_pagado > 0:
            ingreso.status = 'parcial'
        else:
            ingreso.status = 'pendiente'    
    db.session.delete(ep)
    db.session.delete(pago)
    db.session.commit()
    return  jsonify("deleted")

###### Cancelar pago
@blueprint.route("/cancelar_pago/<int:pago_id>",  methods=['GET', 'POST'])
def cancelar_pago(pago_id):
    pago = Pagos_Ingresos.query.get(pago_id)
    for ingreso in pago.ingresos:
        ep = IngresosHasPagos.query.filter_by(ingreso_id=ingreso.id , pago_id =pago.id ).first()
        ingreso.monto_pagado -= ep.monto
        if pago.status == 'por_conciliar':
            ingreso.monto_por_conciliar -= ep.monto
        ep.monto = 0
        
    pago.status = 'cancelado'
    db.session.commit()
    for ingreso in pago.ingresos:
        ingreso.setStatus()
    return  jsonify("deleted")


###########MODALES  ###########
#####  SOLICITAR PAGO #######
#Solicitar pago data for modal
@blueprint.route('/get_data_pagar<int:ingreso_id>', methods=['GET', 'POST'])
@login_required
def get_data_pagar(ingreso_id):
        ingreso = Ingresos.query.get(ingreso_id)   
        
        return jsonify(ingreso_id = ingreso.id, cliente = ingreso.cliente.nombre, monto_total = str(ingreso.monto_total), monto_pagado = str(ingreso.monto_pagado),numero_documento = ingreso.numero_documento)


# Solcitar pago form submit
@blueprint.route('/mandar_cobrar', methods=['GET', 'POST'])
@login_required
def mandar_cobrar():

    if request.form:
        data = request.form
        ingreso = Ingresos.query.get(data["ingreso_id"])
        
        if ('parcial' in data):
                monto_total_pago = data["monto_parcial"]
        else:
                monto_total_pago = ingreso.monto_total - ingreso.monto_pagado
                
        pago = Pagos_Ingresos(status = 'por_conciliar', cliente = ingreso.cliente, 
                              monto_total = monto_total_pago, cuenta_id = data["cuenta_id"], 
                              forma_pago_id = data["forma_pago_id"],referencia_pago = data["ingreso_id"])
      
        ep = IngresosHasPagos(ingreso = ingreso, pago = pago, monto = monto_total_pago)    

        if ingreso.monto_total == ingreso.monto_pagado + ingreso.monto_por_conciliar:            
                ingreso.status = 'por_conciliar'
                
        else: ingreso.status = 'parcial'
                
        ingreso.monto_por_conciliar += monto_total_pago  
        db.session.add(ep)
        db.session.add(pago)
        db.session.commit()
        
        return  redirect("/ingresos/cuentas_por_cobrar")   


# Solicitar multiples pagos data for modal 
@blueprint.route('/get_data_pagar_multiple', methods=['GET', 'POST'])
@login_required
def get_data_pagar_multiple():
        list = []
        ingresos = request.args.getlist('ingresos[]')
        for egreso in egresos:
                e = Ingresos.query.get(egreso)
                monto_pendiente = e.monto_total - e.monto_solicitado - e.monto_pagado
                list.append({'igreso_id': e.id, 'cliente': e.cliente.nombre, 'monto_total': str(monto_pendiente), 'numero_documento': e.numero_documento})
        return jsonify(list)


#Solicitar pago from sumbit
@blueprint.route('/mandar_pagar_multiple', methods=['GET', 'POST'])
@login_required
def mandar_pagar_multiple():
        if request.form:
                data = request.form
                for i in range(int(data["cantidad"])):
                        pago = Pagos_Ingresos(status='solicitado', monto_total=data["monto_total_%d" % i], cuenta_id=data["cuenta_id_%d" % i], forma_pago_id=data["forma_pago_id_%d" % i])
                        for ingreso in data.getlist("ingreso_%d" % i):
                                e = Ingresos.query.get(ingreso)
                                e.status = 'solicitado'
                                e.monto_solicitado +=  e.monto_total - e.monto_pagado
                                pago.cliente = e.cliente
                                ep = IngresosHasPagos(ingreso=e, pago=pago, monto=e.monto_solicitado)
                                db.session.add(ep)
                                db.session.commit()
                return  redirect("/ingresos/pagos_recibidos")   



### CONCILIAT PAGOS ###
#Conciliar pago data for modal
@blueprint.route('/get_data_conciliar_pago_ingreso<int:ingreso_id><int:pago_id>', methods=['GET', 'POST'])
@login_required
def get_data_conciliar_pago_ingreso(ingreso_id,pago_id):
        #ingreso = Pagos_Ingresos.query.get(ingreso_id)
        ingreso = Pagos_Ingresos.query.get(pago_id)
        print('En ingresos/routes.py - Get_data_conciliar')
        print(ingreso_id)
        print(ingreso.cliente.nombre)
        print(ingreso.monto_total)
        print(ingreso.cuenta.nombre)
        print('Pago ID = ',pago_id)
        return jsonify(pago_id = pago_id, cliente = ingreso.cliente.nombre, monto_total=str(ingreso.monto_total), referencia = ingreso.referencia_pago , cuenta=ingreso.cuenta.nombre)

@blueprint.route('/get_data_conciliar<int:ingreso_id>', methods=['GET', 'POST'])
@login_required
def get_data_conciliar(ingreso_id):
        ingreso = Pagos_Ingresos.query.get(ingreso_id)
        print('En ingresos/routes.py - Get_data_conciliar')
        print(ingreso.cliente.nombre)
        print(ingreso.monto_total)
        print(ingreso.cuenta.nombre)
        print('Pago ID = ',ingreso.cuenta.nombre)
        return jsonify(ingreso_id = ingreso.id, cliente = ingreso.cliente.nombre, monto_total=str(ingreso.monto_total), referencia = ingreso.referencia_pago , cuenta=ingreso.cuenta.nombre)


#Conciliar pago form sumbit
@blueprint.route('/conciliar_pago_ingreso', methods=['GET', 'POST'])
@login_required
def conciliar_pago_ingreso():
        print('En conciliar_pago_ingreso!')
        if request.form:
            data = request.form
            print(data)
            pagos = (data.getlist('pago_id'))

            for pago_id in pagos:
                pago = Pagos_Ingresos.query.get(pago_id)
                pago.status = 'conciliado';
                pago.referencia_conciliacion = data["referencia"]
                pago.fecha_pago = data["fecha"]
                pago.comentario = data["comentario"]
                
                
                
                ep = IngresosHasPagos.query.filter_by(pago_id = pago.id ).first()
                ingreso = Ingresos.query.get(ep.ingreso_id)
                
                ingreso.monto_por_conciliar -= ep.monto
                ingreso.monto_pagado += ep.monto
                ingreso.setStatus()
                
            db.session.commit()
            return  redirect("/ingresos/cuentas_por_cobrar")  
        
        
    #Conciliar pago form sumbit
@blueprint.route('/conciliar_ingreso', methods=['GET', 'POST'])
@login_required
def conciliar_ingreso():
        print('En conciliar_ingreso!')
        if request.form:
            data = request.form
            print(data)
            pagos = (data.getlist('pago_id'))
            for pago_id in pagos:
                    pago = Pagos_Ingresos.query.get(pago_id)
                    pago.status = 'conciliado';
                    pago.referencia_conciliacion = data["referencia"]
                    pago.fecha_pago = data["fecha"]
                    pago.comentario = data["comentario"]
                    for ingreso in pago.Ingresos:
                            ep = IngresosHasPagos.query.filter_by(ingreso_id=ingreso.id , pago_id =pago.id ).first()
                            ingreso.monto_por_conciliar -= ep.monto
                            if ingreso.monto_total == ingreso.monto_pagado and ingreso.monto_por_conciliar == 0:
                                    ingreso.status = 'liquidado'     
            db.session.commit()
            return  redirect("/ingresos/cuentas_por_cobrar")   

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
 
       
# Generar pago form sumbit
@blueprint.route('/generar_pago_ingreso', methods=['GET', 'POST'])
@login_required
def generar_pago_ingreso():
        if request.form:
                data = request.form
                pago = Pagos_Ingresos.query.get(data["pago_id"])
                pago.referencia_pago = data["referencia_pago"]
                pago.fecha_pago = data["fecha_pago"]
                for ingreso in pago.ingresos:
                        ep = IngresosHasPagos.query.filter_by(ingreso_id=ingreso.id , pago_id = pago.id ).first()
                        ingreso.monto_pagado += ep.monto
                        ingreso.monto_solicitado -= ep.monto
                        if ingreso.monto_pagado == ingreso.monto_total:
                                ingreso.pagado = True
                        if ('conciliado_check' in data):
                                pago.status = 'conciliado';
                                pago.referencia_conciliacion = data["referencia_conciliacion"]
                                if ingreso.status != 'parcial' and ingreso.monto_pagado == ingreso.monto_total:
                                        ingreso.status = 'liquidado'
                        else:
                                ingreso.monto_por_conciliar += ep.monto
                                pago.status = 'por_conciliar'
                                if ingreso.status != 'parcial' and ingreso.monto_pagado == ingreso.monto_total:
                                        ingreso.status = 'por_conciliar'

                db.session.commit()
                return  redirect("/ingresos/pagos_recibidos")


#reprogramar_fecha
@blueprint.route('/reprogramar_fecha', methods=['GET', 'POST'])
@login_required
def reprogramar_fecha():
        if request.form:
                data = request.form
                ingreso = Ingresos.query.get(data["ingreso_id"])
                ingreso.fecha_programada_pago = data["fecha"]
                db.session.commit()
                return redirect("/ingresos/cuentas_por_cobar")


#reprogramar fecha multiple
@blueprint.route('/reprogramar_fecha_multiple', methods=['GET', 'POST'])
@login_required
def reprogramar_fecha_multiple():      
        ingresos = request.args.getlist('ingresos[]')
        fecha = request.args.get('fecha')
        for ingreso in ingresos:
                egreso = Ingresos.query.get(ingreso)
                egreso.fecha_programada_pago=fecha
        db.session.commit()
        return redirect("/ingresos/cuentas_por_cobar")


@blueprint.route('/ingresos_tiendas', methods=['GET', 'POST'])
def ingresos_tiendas():
    #import df_to_table as df_to_table
    
    formaPago = list(['Banamex','Santander','BBVA'])
    vendor = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    proveedor = list(['sub_categoria_1','sub_categoria_2','sub_categoria_3','sub_categoria_4','sub_categoria_5'])
    categoria = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    concepto= list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
   
    
    user_inputs = dict(request.form)
    print(user_inputs)
    
    #a = df_to_table.df_to_table(list(1))
    #print(a)

    return render_template("ingresos_tiendas.html",
                           navbar_data_capture = 'active',
                           title = "aaaRegistro de ingresos",
                           formaPago = formaPago,
                           vendor = vendor,
                           proveedor = proveedor,
                           categoria = categoria,
                           concepto = concepto,
                           velocity_max = 1)
    
    
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
                return redirect("/ingresos/perfil_ingreso/"+str(ingreso_id))
    
#Ge data for editar detalle de egreso
@blueprint.route('/get_data_editar_detalle<int:detalle_id>', methods=['GET', 'POST'])
@login_required
def get_data_editar_detalle(detalle_id):
        detalle = DetallesIngreso.query.get(detalle_id)
        return jsonify(id = detalle.id, centro_negocios = detalle.centro_negocios_id, cliente=detalle.cliente_id,  monto=str(detalle.monto), 
        categoria = detalle.categoria_id , concepto=detalle.concepto_id, numero_control=detalle.numero_control, descripcion = detalle.descripcion)



 #Ge data for editar detalle de egreso
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
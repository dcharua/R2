from app.ingresos import blueprint
from flask import render_template, request
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
        print("\n\n\n{}\n\n\n".format(data.getlist("monto")))
        montos = list(map(int, data.getlist("monto")))
        monto_total = sum(montos)
        print('Igot here')
        print('IIIIgot here')

        
        ingreso = Ingresos(cliente_id = data["cliente"],
                           tipo_ingreso_id = data["tipo_ingreso"],
                           fecha_vencimiento = data["fecha_vencimiento"], 
                           fecha_programada_pago = data["fecha_programada_pago"],
                           numero_documento = data["numero_documento"],
                           monto_total = monto_total, comentario = data["comentario"],pagado = False,      
                           status = "pendiente", monto_pagado = 0, monto_solicitado = 0,monto_por_conciliar = 0)                                                                                
        
        
        for i in range(len(data.getlist("monto"))):           
            print(i)
            detalle = DetallesIngreso(cliente_id = data["cliente"],
                                      categoria_id = data.getlist("categoria")[i], 
                                      concepto_id = data.getlist("concepto")[i], 
                                      centro_negocios_id = data.getlist("centro_negocios")[i], 
                                      monto = data.getlist("monto")[i], 
                                      numero_control = data.getlist("numero_control")[i], 
                                      descripcion=data.getlist("descripcion")[i])
            ingreso.detalles.append(detalle)
            
        print('444444 got here')
            
        if ('pagado' in data):
            
            print('55555 got here')
            monto_pagado = data["monto_pagado"]
            ingreso.monto_pagado = monto_pagado
            
            if ('conciliado_check' in data):
                status = 'conciliado'
                refrencia_conciliacion = data["referencia_conciliacion"]
                ingreso.status = 'parcial'
                    
            else:
                ingreso.monto_por_conciliar = 0
                status = 'por_conciliar'    
                refrencia_conciliacion = ""
                if ingreso.monto_pagado == ingreso.monto_total: ingreso.status = 'por_conciliar'
                else: ingreso.status = 'parcial'

            pago_ingreso = Pagos_Ingresos(forma_pago_id = data["forma_pago"], 
                                          cuenta_id= data["cuenta_banco"], 
                                          referencia_pago = data["forma_pago"],
                                          fecha_pago = data["fecha_pago"], 
                                          status = status, 
                                          referencia_conciliacion = refrencia_conciliacion,  monto_total = monto_pagado, comentario = data["comentario_pago"], beneficiario_id=1)
            
            if  float(monto_pagado) >= monto_total:
                ingreso.pagado = True 
            ep = IngresosHasPagos(ingreso = ingreso, pago_ingreso = pago_ingreso, monto = monto_total)    
        

        if ('pagado' in data):
            db.session.add(ep)
        else:
            print('666666 got here')
            db.session.add(ingreso)
        
        print('777777 got here')
        db.session.commit()
        print('8888 got here')
        
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
                           velocity_max = 1)




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
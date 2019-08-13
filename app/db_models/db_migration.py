from app.egresos import blueprint
from flask import render_template, request, redirect, flash, jsonify, send_file
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *
from datetime import date,timedelta
from decimal import Decimal
import unidecode
from sqlalchemy.sql import func

import pyodbc
import pandas as pd
import numpy as np
import time



def get_connections():

    con_GEZ = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=gez;uid=gezsa001;pwd=gez9105ru2")
    con_rdm = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=rdm;uid=gezsa001;pwd=gez9105ru2")
    '''
    sql = "SELECT * FROM dbo.Ingresos_Cabecera_r2"
    data = pd.read_sql(sql,con_GEZ)
    data.to_csv('~/Desktop/Ingresos_Cabecera_r2.csv',index = False)
    print(data.head())
    print('TEST SUCCESSFUL!')

    sql = "SELECT * FROM dbo.Ingresos_Detalles_r2"
    data = pd.read_sql(sql, con_GEZ)
    data.to_csv('~/Desktop/Ingresos_Detalles_r2.csv', index=False)

    '''

    return con_GEZ,con_rdm


###################################################################
############### TRANSLATIONS AND RELATIVE FUNCTIONS #############
###################################################################





############### TRANSLATE EGRESOS ############

def translate_egreso(egreso,R2_id):

    fecha_documento = str(egreso['FechaDocto'])
    fecha_vencimiento = str(egreso['FechaRecepcion'] + timedelta(int(egreso['DiasCredito'])))
    fecha_programada_pago = str(egreso['Pagar'])  # Como crear esto? usar lo de arriba y hacer el martes
    numero_documento = str(egreso['NumDocto']).rstrip()[:20]

    monto_total = egreso['TotalAPagar']

    status = 'liquidado' if str(egreso['cxp_liquidado']) == 'True' else 'pendiente'

    monto_pagado = 0 if status != 'liquidado' else monto_total
    monto_solicitado = 0
    monto_por_conciliar = 0
    referencia = 'N/A'  # Preguntar a Uri que poner de referencia
    comentario = str(egreso['Observaciones']).rstrip()[:199]
    pagado = False if status != 'liquidado' else True


    beneficiario_id = int(mapping_beneficiarios[mapping_beneficiarios.GEZ_id == int(egreso['Proveedor_ID'])].R2_id)
    empresa_id = int(mapping_empresas[mapping_empresas.GEZ_id == int(egreso['EmpresaNum'])].R2_id)


    # NUEVAS COLUMNAS!!!
    iva = egreso['Iva']
    descuento = egreso['Descuento']
    monto_documento = egreso['SubTotal'] + iva
    notas_credito = 0

    # Detalles de Egreso
    detalle = generar_detalle_egreso(R2_id, egreso, beneficiario_id)

    # Generar Pago para los liquidados
    if status == 'liquidado': pago = generar_pago_migracion(beneficiario_id,monto_total,egreso)
    else: pago = None

    # print('\n Egreso: \n fecha_documento= {}, \nfecha_vencimiento= {}, \nfecha_programada_pago={}, \nnumero_documento= {}, \nmonto_total= {}, \nmonto_pagado= {}, \nmonto_solicitado= {}, \nmonto_por_conciliar= {}, \nreferencia= {}, \ncomentario,= {}, \npagado= {}, \nstatus= {}, \nbeneficiario_id= {}, \nempresa_id= {}, \niva= {}, \ndescuento= {}, \nmonto_documento= {}, \nnotas_credito= {}'.format(fecha_documento, fecha_vencimiento,fecha_programada_pago, numero_documento, \
    #        monto_total, monto_pagado, monto_solicitado, monto_por_conciliar, referencia, comentario, pagado, status, beneficiario_id, empresa_id, iva, descuento, monto_documento, notas_credito))


    return fecha_documento, fecha_vencimiento, fecha_programada_pago, numero_documento, \
           monto_total, monto_pagado, monto_solicitado, monto_por_conciliar, referencia, comentario, \
           pagado, status, beneficiario_id, empresa_id, iva, descuento, monto_documento, notas_credito, detalle, pago



def generar_pago_migracion(beneficiario_id,monto_total,egreso):

    status = 'liquidado'
    global pago_id_egreso
    pago_id_egreso = pago_id_egreso + 1
    fecha_pago = str(egreso['FechaDPago']) if str(egreso['FechaDPago']) != 'NaT' else None

    pago = Pagos(id=int(pago_id_egreso), fecha_pago = fecha_pago, status=status, beneficiario_id=int(beneficiario_id), monto_total=float(monto_total),
                 cuenta_id=int(cuenta_id), forma_pago_id=int(forma_pago_id))

    #print('\nPago: \nid = {} \n status = {} \nfecha_pago = {}\n beneficiario_id = {} \nmonto_total= {} \n cuenta_id = {} \n forma_pago_id = {}'.format(pago_id_egreso,status,fecha_pago,beneficiario_id,monto_total,cuenta_id, forma_pago_id))

    return pago


def generar_detalle_egreso(R2_id,egreso, beneficiario_id):

    try: centro_negocios_id = int(mapping_centros_negocio[mapping_centros_negocio.GEZ_id == int(egreso['AlmQRecibe'])].R2_id)
    except: centro_negocios_id = centros_negocio_sin_definir_id

    monto = egreso['TotalAPagar']
    numero_control = str(egreso['NombreDMarca'])
    descripcion = str(egreso['TipoDescripcion'])

    #print('\n  Detalle de Egreso: \n centro_negocios_id= {}, \nproveedor_id= {}, \ncategoria_id= {}, \nconcepto_id= {}, \nmonto= {}, \nnumero_control= {}, \ndescripcion = {}'.format(centro_negocios_id,beneficiario_id,categoria_id,concepto_id,monto,numero_control,descripcion))

    detalle = DetallesEgreso(centro_negocios_id =int(centro_negocios_id), proveedor_id=int(beneficiario_id),
                             categoria_id=int(categoria_id), concepto_id=int(concepto_id), monto=float(monto),
                             numero_control=numero_control,
                             descripcion=descripcion)



    return detalle


############### TRANSLATE INGRESOS ############


def translate_ingreso(ingresos_list,ingreso,R2_id):

    dias_para_vencimiento = 10

    status = 'liquidado'
    tipo_ingreso_id = tipo_ingreso_id
    cliente_id = cliente_id
    empresa_id = int(mapping_empresas[mapping_empresas.GEZ_id == int(ingreso['EmpresaID'])].R2_id)

    referencia = ''# str(ingreso['Referencia_Pago']).rstrip()[:200]
    fecha_vencimiento = str(ingreso['Fecha'] + timedelta(dias_para_vencimiento))
    fecha_programada_pago = str(ingreso['Fecha'] + timedelta(dias_para_vencimiento))
    fecha_documento = str(ingreso['Fecha'])
    numero_documento = ''
    monto_total = ingreso['IngresoTotalo']
    monto_pagado = ingreso['IngresoTotal']
    costo_venta = ingreso['CostoTotal']
    iva_ingresos = ingreso['Iva_dIngresos']
    iva_ventas = ingreso['CostoTotalIva']
    utilidad_neta = ingreso['UtilidadNeta']
    monto_solicitado = 0
    monto_por_conciliar = 0

    comentario = ''
    pagado = True

    # Detalles de Egreso
    detalle = generar_detalle_egreso(R2_id, ingreso, empresa_id, cliente_id)

    print('\n Egreso: \nfecha_vencimiento= {}, \nfecha_programada_pago={}\nfecha_documento = {} \nnumero_documento= {}, \nmonto_total= {}, \nmonto_pagado= {}, \nmonto_solicitado= {}, \nmonto_por_conciliar= {}, '
          '\nreferencia= {},\npagado= {}, \nstatus= {}, \ncliente_id= {}, \nempresa_id= {}, \niva_ventas= {}, \niva_ingresos= {} \ncosto_venta = {}\nutilidad_neta= {}'.format(
            fecha_vencimiento, fecha_programada_pago,fecha_documento, numero_documento, \
            monto_total, monto_pagado, monto_solicitado, monto_por_conciliar, referencia, pagado, status,cliente_id,
            empresa_id, iva_ventas,iva_ingresos, costo_venta,utilidad_neta))

    return status,tipo_ingreso_id, cliente_id,empresa_id, referencia, fecha_vencimiento, fecha_programada_pago, fecha_documento, numero_documento,monto_total,monto_pagado,\
           monto_solicitado, monto_por_conciliar,costo_venta,iva_ingresos,iva_ventas,utilidad_neta, pagado, detalle


def generar_detalle_ingreso(R2_id,ingreso, empresa_id, cliente_id):

    try: centro_negocios_id = int(mapping_centros_negocio[mapping_centros_negocio.GEZ_id == int(ingreso['ingr_sucursal'])].R2_id)
    except: centro_negocios_id = centros_negocio_sin_definir_id


    monto = ingreso['TotalAPagar']
    cliente_id = cliente_id

    categoria_ingresos_id = categoria_ingresos_id
    concepto_ingresos_id = concepto_ingresos_id
    monto = ingreso['Referencia_Pago']

    print('\n  Detalle de Ingreso: \n centro_negocios_id= {}, \ncategoria_id= {}, \nconcepto_id= {}, \nmonto= {}, \nnumero_control= {}, \ndescripcion = {}'.format(centro_negocios_id,categoria_id,concepto_id,monto,numero_control,descripcion))



    detalle = DetallesIngreso(cliente_id=cliente_id,
                              categoria_id=categoria_id,
                              concepto_id=concepto_id,
                              centro_negocios_id=centro_negocios_id,
                              monto=monto)


    return detalle


def generar_pago_ingreso_migracion(pago):

    global pago_id_ingreso
    pago_id_ingreso = pago_id_ingreso + 1

    status = 'liquidado'
    cliente_id = cliente_id
    monto_total = pago['monto_total']
    fecha_pago = str(pago['Fecha'])
    forma_pago_id = int(mapping_centros_negocio[mapping_centros_negocio.GEZ_id == int(pago['ingr_sucursal'])].R2_id)
    referencia_pago = ''
    fecha_conciliacion = str(pago['Fecha'])
    referencia_conciliacion = ''
    try: cuenta_id = int(mapping_centros_negocio[mapping_cuentas.GEZ_id == int(pago['ingr_sucursal'])].R2_id)
    except: cuenta_id = cuenta_id_por_definir


    pago_ingreso = Pagos_Ingresos(status=status, cliente_id=cliente_id,
                                  monto_total=monto_total, cuenta_id=int(data["cuenta_id"]),
                                  fecha_pago=data["fecha_pago"],
                                  forma_pago_id=forma_pago_id,
                                  fecha_conciliacion=fecha_conciliacion,
                                  referencia_conciliacion=referencia_conciliacion,
                                  )


    #print('\nPago: \nid = {} \n status = {},\n beneficiario_id = {} \nmonto_total= {} \n cuenta_id = {} \n forma_pago_id = {}'.format(pago_id,status,beneficiario_id,monto_total,cuenta_id, forma_pago_id))

    return pago_ingreso






############### TRANSLATE BENEFICIARIOS ############


def translate_beneficiario(proveedor,variable,con):
    GEZ_id = int(proveedor['pro_numero'])

    nombre = proveedor['pro_razon']
    nombre_corto = proveedor['pro_ncorto'].rstrip()
    RFC = proveedor['pro_rfc'].rstrip()
    direccion = get_direccion(proveedor,variable)
    comentarios = proveedor['pro_observaciones'].rstrip()
    razon_social = proveedor['pro_razon'].rstrip()

    try:
        numero_cuenta = (pd.read_sql("select provcta_numero from dbo.proveedores_cuentasdeposito where prov_vtaprov = {}".format(GEZ_id), con)).iloc[0,0]

    except: numero_cuenta = ''

    try:
        banco = (
        pd.read_sql("select provcta_banco from dbo.proveedores_cuentasdeposito where prov_vtaprov = {}".format(GEZ_id), con)).iloc[0,0]

    except: banco = ''

    saldo = 0

    status = 'liquidado'

    contacto_1, contacto_2, contacto_3 = agregar_contactos(proveedor)

    return GEZ_id, nombre, nombre_corto, RFC, direccion, comentarios, razon_social, numero_cuenta, banco, saldo, status, contacto_1,contacto_2, contacto_3



def get_direccion(item,variable):

    if variable == 'beneficiarios':

        calle = str(item['pro_calle']).rstrip()
        colonia = str(item['pro_colonia']).rstrip()
        cp = str(item['pro_cp']).rstrip()

        # TODO: mapear el estado y pais
        estado = str(item['pro_estado']).rstrip()
        pais = str(item['pro_pais']).rstrip()
        ciudad = str(item['pro_delompio']).rstrip()

    elif variable == 'centros_negocio':

        calle = str(item['succalle']).rstrip()
        colonia = str(item['succolonia']).rstrip()
        cp = str(item['succp']).rstrip()

        # TODO: mapear el estado y pais
        estado = ''
        pais = str(item['sucpais']).rstrip()
        ciudad = str(item['sucdelompio']).rstrip()


    return unidecode.unidecode(calle + ' ' + colonia + ' ' + cp + ' ' + ciudad + ' ' + estado + ' ' + pais)


def agregar_contactos(proveedor):

    contacto_1 = ContactoBeneficiario(nombre=str(proveedor['pro_creycobranza']).rstrip()[:50],
                                        correo=str(proveedor['pro_cobranza_email']).rstrip()[:50],
                                        telefono=str(proveedor['pro_cobranza_tel']).rstrip()[:30],
                                        puesto='Cobranza')


    contacto_2 = ContactoBeneficiario(nombre=proveedor['pro_director'].rstrip(),
                                  puesto='Director')



    contacto_3 = ContactoBeneficiario(nombre=str(proveedor['pro_atencion']).rstrip()[:50],
                                      telefono=str(proveedor['pro_telefonos']).rstrip()[:30],
                                      puesto='Atencion')

    return contacto_1,contacto_2, contacto_3





############### TRANSLATE CENTROS_NEGOCIO ############


def translate_centros_negocio(item,variable):


    nombre = item['sucnombre']
    numero = int(item['sucnumero'])
    tipo = 'Pendiente de Definir'
    direccion = get_direccion(item,variable)
    arrendadora = 'Pendiente de Definir'
    comentario = ''
    empresa_id = int(str(Empresas_Mapping.query.
                                        filter(Empresas_Mapping.GEZ_id == int(item['sucempresa'])).all())
                                        .replace('[','').replace(']',''))

    print('id = {}, \nnombre= {}, \nnumero= {}, \ndireccion= {}, \ntipo= {}, \narrendadora= {}, \ncomentario= {},\n empresa_id = {}'.format(
        id, nombre, numero, direccion, tipo, arrendadora, comentario, empresa_id))
    return numero, direccion, tipo, arrendadora, comentario, empresa_id




############### TRANSLATE NOMINA ############


def translate_empleados(item,variable):



    nombre = item['cnombre'].rstrip()
    apellido = item['capepater'].rstrip()
    segundo_appellido = item['capemater'].rstrip()
    puesto = int(item['c_puesto'])
    try: sexo = 'Masculino' if int(item['c_sexo']) == 1 else 'Femenino'
    except: sexo = 'Masculino'
    tienda = int(item['ctienda'])
    departamento = int(item['c_depto'])
    fecha_nacimiento = str(item['fnacimiento']) if str(item['fnacimiento']) != 'NaT' else None
    fecha_alta = str(item['cfecalt']) if str(item['cfecalt']) != 'NaT' else None
    fecha_ingreso = str(item['c_fecingreso']) if str(item['c_fecingreso']) != 'NaT' else None
    fecha_contrato = str(item['c_feccontrato']) if str(item['c_feccontrato']) != 'NaT' else None
    fecha_baja = str(item['cfecbaj']) if str(item['cfecbaj']) != 'NaT' else None
    motivo_baja = str(item['cmotbaj']).rstrip() if str(item['cmotbaj']).rstrip() != 'None' else None
    sueldo = float(0)
    prestamo_monto = float(0)
    prestamos_fecha_entrega = ''
    prestamos_fecha_vuelta = ''

    # print('Adding: nombre= {}, \napellido= {}, \nsegundo_appellido= {}, \npuesto= {}, \nsexo= {}, \ntienda= {}, \ndepartamento= {}, \nfecha_nacimiento= {}, \nfecha_alta= {}, \nfecha_ingreso= {}, \nfecha_contrato= {}, \nfecha_baja= {}, \nmotivo_baja= {}, \nsueldo= {}, \n'.format(nombre, apellido, segundo_appellido, puesto,sexo, tienda,departamento,fecha_nacimiento,\
    #        fecha_alta ,fecha_ingreso, fecha_contrato,fecha_baja,motivo_baja,sueldo))

    return nombre, apellido, segundo_appellido, puesto,sexo, tienda,departamento,fecha_nacimiento,\
           fecha_alta ,fecha_ingreso, fecha_contrato,fecha_baja,motivo_baja,sueldo, prestamo_monto, \
           prestamos_fecha_entrega,prestamos_fecha_vuelta






###################################################################
################ USEFUL FUNCTIONS #####################
###################################################################

def get_nombre_and_id(variable_item,variable):


    if variable == 'empresas':

        return variable_item.iloc[2].rstrip(), variable_item.iloc[0]

    elif variable == 'beneficiarios':

        return variable_item['pro_razon'].rstrip(), variable_item.iloc[0]

    elif variable == 'egresos':

        return variable_item['Recep_ID'], variable_item['Recep_ID']

    elif variable == 'centros_negocio':

        return variable_item['sucnombre'].rstrip(), variable_item['sucnum']

    elif variable == 'empleados':

        return str(variable_item['cnum']), variable_item['cnum_id']





def get_lists(con,variable):


    if variable == 'empresas':

        list_R2 = Empresas.query.all()
        list_GEZ = pd.read_sql("SELECT * FROM dbo.empresas", con)
        mapping_table = mapping_empresas

    elif variable == 'beneficiarios':

        list_R2 = Beneficiarios.query.all()
        list_GEZ = pd.read_sql("SELECT * FROM dbo.proveedores", con)
        mapping_table = mapping_beneficiarios

    elif variable == 'centros_negocio':

        list_R2 = CentrosNegocio.query.all()
        list_GEZ = pd.read_sql("SELECT * FROM dbo.sucursales", con)
        mapping_table = mapping_centros_negocio

    elif variable == 'empleados':

        list_R2 = Empleados.query.all()
        list_GEZ = pd.read_sql("SELECT * FROM dbo.empleados", con)
        mapping_table = mapping_empleados

    elif variable == 'egresos':

        list_R2 = Egresos.query.all()
        list_GEZ = pd.read_sql("SELECT * FROM dbo.Egresos_r2", con)
        list_GEZ = list_GEZ[list_GEZ.FechaDocto > '2017']
        mapping_table = mapping_egresos

    elif variable == 'ingresos':

        list_R2 = Ingresos.query.all()
        list_GEZ = pd.read_sql("dbo.Ingresos_Cabecera_r2", con)
        list_GEZ = list_GEZ[list_GEZ.Fecha > '2017']
        mapping_table = mapping_ingresos

    else:
        print('Variable not found!!')


    return list_GEZ,list_R2, mapping_table


def write_variable_R2(variable, R2_id, GEZ_id, nombre, variable_item, agregar_item,list_GEZ,con):

    if variable == 'empresas':

        variable_item = Empresas(id=int(R2_id),nombre=nombre)
        variable_map = Empresas_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))

    # agregar el item si no existe


    if variable == 'beneficiarios':

        GEZ_id, nombre, nombre_corto, RFC, direccion, comentarios, razon_social, cuenta_banco, banco, saldo, status, contacto_1,contacto_2, contacto_3 = translate_beneficiario(variable_item,variable,con)

        variable_item = Beneficiarios(id=R2_id, nombre=nombre,nombre_corto=nombre_corto, RFC=RFC,
                                      direccion=direccion, razon_social=razon_social,comentarios = comentarios,
                                      cuenta_banco=cuenta_banco, saldo=saldo, status=status, banco=banco)

        variable_item.contacto.append(contacto_1)
        variable_item.contacto.append(contacto_2)
        variable_item.contacto.append(contacto_3)

        variable_map = Beneficiarios_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))


    if variable == 'centros_negocio':

        numero, direccion, tipo, arrendadora, comentario, empresa_id = translate_centros_negocio(variable_item,variable)

        variable_item = CentrosNegocio(id=R2_id, nombre=nombre, numero=numero, direccion=direccion,
                                       tipo=tipo, arrendadora=arrendadora, comentario=comentario,
                                       empresa_id=empresa_id)

        variable_map = CentrosNegocio_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))

    if variable == 'empleados':

        nombre, apellido, segundo_appellido, puesto, sexo, tienda, departamento, fecha_nacimiento, fecha_alta, fecha_ingreso, fecha_contrato, \
        fecha_baja, motivo_baja, sueldo, prestamo_monto, prestamos_fecha_entrega, prestamos_fecha_vuelta = translate_empleados(variable_item,variable)

        variable_item = Empleados(id=R2_id, nombre=nombre, apellido=apellido, segundo_appellido=segundo_appellido, puesto=puesto, sexo=sexo, tienda=tienda,
                                  departamento=departamento, fecha_nacimiento=fecha_nacimiento,fecha_alta=fecha_alta, fecha_ingreso=fecha_ingreso,
                                  fecha_contrato=fecha_contrato, fecha_baja=fecha_baja, motivo_baja=motivo_baja, sueldo=sueldo, prestamo_monto=prestamo_monto)

        variable_map = Empleados_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))

    if variable == 'egresos':

        fecha_documento, fecha_vencimiento, fecha_programada_pago, numero_documento, monto_total, monto_pagado, monto_solicitado, monto_por_conciliar, referencia, comentario, \
        pagado, status, beneficiario_id, empresa_id, iva, descuento, monto_documento, notas_credito, detalle, pago = translate_ingreso(variable_item,variable)


        variable_map = Egresos_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))

        variable_item.detalles.append(detalle)
        #
        if pago != None:
            ep = EgresosHasPagos(egreso_id=int(R2_id), pago_id=int(pago.id), monto=float(monto_total))
            db.session.add(pago)
            db.session.add(ep)


        variable_item = Egresos(id=int(R2_id), fecha_documento=fecha_documento, fecha_vencimiento=fecha_vencimiento, fecha_programada_pago=fecha_programada_pago, numero_documento=str(numero_documento),
                                monto_total=float(monto_total), monto_pagado=float(monto_pagado), monto_solicitado=float(monto_solicitado),
                                monto_por_conciliar=float(monto_por_conciliar), referencia=str(referencia),comentario=comentario, pagado=pagado,status=status,
                                beneficiario_id=int(beneficiario_id), empresa_id=int(empresa_id), iva=float(iva), descuento=float(descuento), monto_documento=float(monto_documento),notas_credito=float(notas_credito))



    if variable == 'ingresos':

        status, tipo_ingreso_id, cliente_id, empresa_id, referencia, fecha_vencimiento, fecha_programada_pago, fecha_documento, numero_documento, monto_total, monto_pagado, \
        monto_solicitado, monto_por_conciliar, costo_venta, iva_ingresos, iva_ventas, utilidad_neta, pagado, detalle = translate_ingreso(variable_item,variable)


        # Generar Pagos
        pagos_ingreso = list_GEZ[list_GEZ.md_id == int(GEZ_id)]

        for i in range(len(pagos_ingreso)):
            pago, GEZ_id_pago = generar_pago_ingreso_migracion(variable_item)
            ep = IngresosHasPagos(ingreso_id=int(R2_id), pago_id=int(pago.id), monto=float(monto_total))
            db.session.add(pago)
            db.session.add(ep)


        # Crear el ingreso
        variable_item = Ingresos(id=int(R2_id), fecha_documento=fecha_documento, fecha_vencimiento=fecha_vencimiento, fecha_programada_pago=fecha_programada_pago, numero_documento=str(numero_documento),
                                monto_total=float(monto_total), monto_pagado=float(monto_pagado), monto_solicitado=float(monto_solicitado),
                                monto_por_conciliar=float(monto_por_conciliar), referencia=str(referencia),comentario='', pagado=pagado,status=status,
                                empresa_id=int(empresa_id), iva_ventas=float(iva_ventas), iva_ingresos=float(iva_ingresos), costo_venta=float(costo_venta),utilidad_neta=float(utilidad_neta))


        variable_map = Ingresos_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))

        variable_item.detalles.append(detalle)

    if agregar_item:
        db.session.add(variable_item)

    db.session.add(variable_map)
    db.session.commit()

    return

def get_max_id(list_r):

    indexes = np.array(np.zeros(len(list_r)))
    if len(list_r) == 0: indexes = np.array([0])

    for i in range(len(list_r)):
        indexes[i] = list_r[i].id

    return int(max(indexes))




def migrate_table(con_GEZ,con_rdm,variable):

    list_GEZ, list_R2, mapping_table = get_lists(con_GEZ,variable)


    # Define some control variables
    map_cnt = get_max_id(list_R2) + 1


    # por cada fila de la table, checar si ya existe en la base de datos y registrar
    for i in range(len(list_GEZ)):

        agregar_item, already_registered = True, 0

        GEZ_nombre, GEZ_id = get_nombre_and_id(list_GEZ.iloc[i,:],variable)
        print('\n ID, Name GEZ list: --{}--,{} '.format(GEZ_nombre, GEZ_id))


        # Primero, checar si ya esta mapeado
        match = mapping_table[mapping_table.GEZ_id == int(GEZ_id)]
        if len(match) > 0:
            print('This id is already registered as R2_id = {} ! doing Nothing!'.format(match.iloc[0,1]))
            already_registered = 1

        # Si no esta registrada, hacer lo siguiente
        if already_registered == 0:
            print('This id is not registered! Registering needed!')

            #  Checar si el nombre de la compania ya existe en R2,

            start = time.time()
            print("hello")

            # Si el nombre es diferenete que el id (empresas, beneficiarios, centros de negocio tienen que verificar que no se ha registrado otro id con el mismo nombre

            if GEZ_nombre != GEZ_id:
                for j in range(len(list_R2)):
                    #print('Comparando -{}- vs -{}-'.format(list_R2[j], GEZ_nombre))

                    if str(list_R2[j]) == GEZ_nombre:
                        print('Se encontro el match con GEZ_id = {}, R2_id = {}'.format(GEZ_id, list_R2[j].id))

                        agregar_item = False
                        R2_id = list_R2[j].id
                        break

            end = time.time()
            print(' No match found! Searching time = ',end - start)

            if agregar_item == True:
                ('No existe este nombre en R2, se creara un nuevo R2_id')
                R2_id = (map_cnt + i)

            print('Adding GEZ_id = {}, and mapping with {}'.format(GEZ_id, R2_id))
            write_variable_R2(variable, R2_id, GEZ_id, GEZ_nombre,list_GEZ.iloc[i, :], agregar_item,list_GEZ, con_GEZ)



def mapping_to_Dataframe(map_table):

    df = pd.DataFrame(np.zeros([len(map_table),2]))
    df.columns = ['GEZ_id','R2_id']

    for i in range(len(df)):
        df.iloc[i,0] = int(map_table[i].GEZ_id)
        df.iloc[i,1] =int(map_table[i].R2_id)

    return df

def initialize_global_var():
    global categoria_id
    global concepto_id
    global cuenta_id
    global forma_pago_id
    global tipo_ingreso_id

    # IDs por definir
    global centros_negocio_sin_definir_id
    global cuenta_id_por_definir

    global pago_id_egreso
    global pago_id_ingreso
    global categoria_ingresos_id
    global concepto_ingresos_id

    global mapping_empresas
    global mapping_beneficiarios
    global mapping_centros_negocio
    global mapping_egresos
    global mapping_empleados
    global mapping_ingresos

    ###Tablas de Mapeo
    mapping_beneficiarios = mapping_to_Dataframe(Beneficiarios_Mapping.query.all())
    mapping_empresas = mapping_to_Dataframe(Empresas_Mapping.query.all())
    mapping_centros_negocio = mapping_to_Dataframe(CentrosNegocio_Mapping.query.all())
    mapping_egresos = mapping_to_Dataframe(Egresos_Mapping.query.all())
    mapping_empleados = mapping_to_Dataframe(Empleados_Mapping.query.all())
    mapping_ingresos = mapping_to_Dataframe(Ingresos_Mapping.query.all())

    # Constantes Egresos
    categoria_id = Categorias.query.filter(Categorias.nombre == "Compras").all()[0].id
    concepto_id = Conceptos.query.filter(Conceptos.nombre == 'Zapato').all()[0].id
    cuenta_id = Cuentas.query.filter(Cuentas.nombre == 'Prueba').all()[0].id
    forma_pago_id = FormasPago.query.filter(FormasPago.nombre == 'Transferencia').all()[0].id
    centros_negocio_sin_definir_id = CentrosNegocio.query.filter(CentrosNegocio.nombre == 'SinDefinir').all()[0].id
    try: pago_id_egreso = db.session.query(db.func.max(Pagos.id)).scalar() + 1
    except: pago_id_egreso = 1

    # Constantes Ingresos
    tipo_ingreso_id = Tipo_Ingreso.query.filter(Tipo_Ingreso.tipo == 'Ventas').all()[0].id
    cliente_id = Clientes.query.filter(Clientes.nombre == 'Prueba').all()[0].id
    try: pago_id_ingreso = db.session.query(db.func.max(Pagos_Ingresos.id)).scalar() + 1
    except: pago_id_ingreso = 1
    categoria_ingresos_id = Categorias.query.filter(Categorias.nombre == "Ventas").all()[0].id
    concepto_ingresos_id = Conceptos.query.filter(Conceptos.nombre == 'Tiendas').all()[0].id
    cuenta_id_por_definir = Cuentas.query.filter(Cuentas.nombre == 'SinDefinir').all()[0].id

########## MAIN FUNCTION ##########


def run_all_migrations():
    #initialize_global_var()
    #con_GEZ, con_rdm = get_connections()

    #list_GEZ, list_R2, mapping_table = get_lists(con_GEZ, 'egresos')




    i = 0

    # #Migrate Empresas
    # variable = 'empresas'
    # migrate_table(con_GEZ, con_rdm, variable)
    #
    # #Migrate Proveedores
    #
    # variable = 'beneficiarios'
    # migrate_table(con_GEZ, con_rdm, variable)
    #
    # # Migrate Centrs_Negocio
    # variable = 'centros_negocio'
    # migrate_table(con_GEZ, con_rdm, variable)

    # Migrate Empleados
    # variable = 'empleados'
    # migrate_table(con_GEZ, con_rdm, variable)

    # Migrate Egresos

    variable = 'egresos'
    print('Job running at :',time.time())
    #migrate_table(con_GEZ, con_rdm, variable)

    # Migrate Ingresos

    # Migration Testing Proceedure

    #
    # # Paso 1: Editar Get_list
    # # Paso 2: agregar Mapping table en routes.py
    # list_GEZ, list_R2, mapping_table = get_lists(con_GEZ, variable)
    #
    # print(list_GEZ.head())
    # print(list_GEZ.iloc[i,:])
    # print(list_R2)
    #
    # # paso 3 asegurar que GEZ_nombre, GEZ_id esten correctos en get_nombre_and_id




    #Paso 4: Generar translation function
    #
    # GEZ_nombre, GEZ_id = get_nombre_and_id(list_GEZ.iloc[i,:],variable)
    # print('\n ID, Name GEZ list: --{}--,{} '.format(GEZ_nombre, GEZ_id))
    #

    # write_variable_R2(variable, 3, GEZ_id, GEZ_nombre, list_GEZ.iloc[i,:], True, con_GEZ)

    # # paso 4 asegurar que las variables que dependen de sub-queries funcionen:

def job():
    print("I'm working...")
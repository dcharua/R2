from app.egresos import blueprint
from flask import render_template, request, redirect, flash, jsonify, send_file
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *
from datetime import date,timedelta
from decimal import Decimal
from sqlalchemy.sql import func

import pyodbc
import pandas as pd
import numpy as np
import time
import pdb
from config import config_dict

# from app import create_app
# app = create_app(config_dict['Debug'])
# app.app_context().push()



#########################################################################################
#--------------------------------   RANDOM FUNCIONS     --------------------------------#
#########################################################################################

def mapping_to_Dataframe(map_table):

    df = pd.DataFrame(np.zeros([len(map_table),2]))
    df.columns = ['GEZ_id','R2_id']

    for i in range(len(df)):
        df.iloc[i,0] = int(map_table[i].GEZ_id)
        df.iloc[i,1] = int(map_table[i].R2_id)

    return df


def get_max_id(list_r):

    indexes = np.array(np.zeros(len(list_r)))
    if len(list_r) == 0: indexes = np.array([0])

    for i in range(len(list_r)):
        indexes[i] = list_r[i].id

    return int(max(indexes))

def get_connections():

    con_GEZ = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=gez;uid=gezsa001;pwd=gez9105ru2")
    con_rdm = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=rdm;uid=gezsa001;pwd=gez9105ru2")

    return con_GEZ,con_rdm


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


    return (calle + ' ' + colonia + ' ' + cp + ' ' + ciudad + ' ' + estado + ' ' + pais)





def get_nombre_and_id(variable_item,variable):


    if variable == 'empresas':

        return variable_item.iloc[2].rstrip(), variable_item.iloc[0]

    elif variable == 'beneficiarios':

        return variable_item['pro_razon'].rstrip(), variable_item.iloc[0]

    elif variable == 'egresos':

        return variable_item['Recep_ID'], variable_item['Recep_ID']

    elif variable == 'ingresos':

        return variable_item['md_id'], variable_item['md_id']

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
        list_GEZ = list_GEZ[list_GEZ.FechaDocto > '2019']
        mapping_table = mapping_egresos

    elif variable == 'ingresos':

        list_R2 = Ingresos.query.all()
        list_GEZ = pd.read_sql("SELECT * FROM dbo.Ingresos_Cabecera_r2", con)
        list_GEZ = list_GEZ[list_GEZ.Fecha > '2017']
        mapping_table = mapping_ingresos

    else:
        print('Variable not found!!')


    return list_GEZ,list_R2, mapping_table









##########################################################################################################
#--------------------------------  Initialize Variables  -------------------------------- #
##########################################################################################################





def initialize_global_var(con, variable):
    global categoria_id
    global concepto_id
    global cuenta_id
    global forma_pago_id
    global cuenta_id_egreso
    global forma_pago_id_egreso
    global tipo_ingreso_id
    global formas_pago

    # IDs por definir
    global centros_negocio_sin_definir_id
    global cuenta_id_por_definir

    global pago_id_egreso
    global pago_id_ingreso
    global categoria_ingresos_id
    global concepto_ingresos_id
    global centros_negocio

    global mapping_empresas
    global mapping_beneficiarios
    global mapping_centros_negocio
    global mapping_egresos
    global mapping_empleados
    global mapping_ingresos
    global mapping_cuentas

    global list_GEZ_Detalles
    global cliente_id
    global cliente_ecommerce_id
    global cliente_tiendas_id
    global cliente_otro_id

    global concepto_ingresos_tiendas_id
    global concepto_ingresos_ecommerce_id
    global concepto_ingresos_otro_id


    list_GEZ_Detalles = pd.read_sql("SELECT * FROM dbo.Ingresos_Detalles_r2", con)
    list_GEZ_Detalles = list_GEZ_Detalles[list_GEZ_Detalles.fecha > '2017']
    centros_negocio = CentrosNegocio.query.all()

    ###Tablas de Mapeo
    mapping_cuentas = pd.read_excel('./app/db_models/MapeoCuentasIngresos.xlsx',converters={'Banamex':str,'Amex':str,'BBVA':str,'Efectivo':str,'Credito':str})
    mapping_beneficiarios = mapping_to_Dataframe(Beneficiarios_Mapping.query.all())
    mapping_empresas = mapping_to_Dataframe(Empresas_Mapping.query.all())
    mapping_centros_negocio = mapping_to_Dataframe(CentrosNegocio_Mapping.query.all())
    mapping_egresos = mapping_to_Dataframe(Egresos_Mapping.query.all())
    mapping_empleados = mapping_to_Dataframe(Empleados_Mapping.query.all())
    mapping_ingresos = mapping_to_Dataframe(Ingresos_Mapping.query.all())
    #mapping_cuentas = pd.read_csv('./app/db_models/cuentas_mapping.csv', converters={i: str for i in range(0, 7)})


    # Constantes Egresos
    if variable == 'egresos':
        categoria_id = Categorias.query.filter(Categorias.nombre == "Compras").all()[0].id
        concepto_id = Conceptos.query.filter(Conceptos.nombre == 'Zapato').all()[0].id
        cuenta_id_egreso = Cuentas.query.filter(Cuentas.nombre == 'Prueba').all()[0].id
        forma_pago_id_egreso = FormasPago.query.filter(FormasPago.nombre == 'Transferencia').all()[0].id
        centros_negocio_sin_definir_id = CentrosNegocio.query.filter(CentrosNegocio.nombre == 'SinDefinir').all()[0].id
        try: pago_id_egreso = db.session.query(db.func.max(Pagos.id)).scalar() + 1
        except: pago_id_egreso = 1


    # Constantes Ingresos
    if variable == 'ingresos':
        tipo_ingreso_id = Tipo_Ingreso.query.filter(Tipo_Ingreso.tipo == 'Ventas').all()[0].id
        cliente_ecommerce_id = Clientes.query.filter(Clientes.nombre == 'Ventas Tiendas Fisicas').all()[0].id
        cliente_tiendas_id = Clientes.query.filter(Clientes.nombre == 'Ventas Ecommerce').all()[0].id
        cliente_otro_id = Clientes.query.filter(Clientes.nombre == 'Ventas Adicionales').all()[0].id
        formas_pago = FormasPago.query.all()
        try: pago_id_ingreso = db.session.query(db.func.max(Pagos_Ingresos.id)).scalar() + 1
        except: pago_id_ingreso = 1
        categoria_ingresos_id = Categorias.query.filter(Categorias.nombre == "Ventas").all()[0].id

        concepto_ingresos_tiendas_id = Conceptos.query.filter(Conceptos.nombre == 'Tiendas').all()[0].id
        concepto_ingresos_ecommerce_id = Conceptos.query.filter(Conceptos.nombre == 'Ventas Ecommerce').all()[0].id
        concepto_ingresos_otro_id = Conceptos.query.filter(Conceptos.nombre == 'Ventas Adicionales').all()[0].id

        cuenta_id_por_definir = Cuentas.query.filter(Cuentas.nombre == 'SinDefinir').all()[0].id
        centros_negocio_sin_definir_id = CentrosNegocio.query.filter(CentrosNegocio.nombre == 'SinDefinir').all()[0].id










#########################################################################################################
#--------------------------------  TRANSLATIONS AND RELATIVE FUNCTIONS -------------------------------- #
#########################################################################################################



def translate_egreso(R2_id, egreso):

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


    return fecha_documento, fecha_vencimiento, fecha_programada_pago, numero_documento, \
           monto_total, monto_pagado, monto_solicitado, monto_por_conciliar, referencia, comentario, \
           pagado, status, beneficiario_id, empresa_id, iva, descuento, monto_documento, notas_credito, detalle



def generar_pago_migracion(beneficiario_id, monto_total, egreso):

    status = 'conciliado'
    global pago_id_egreso
    pago_id_egreso += 1
    fecha_pago = str(egreso['FechaDPago']) if str(egreso['FechaDPago']) != 'NaT' else None

    pago = Pagos(id=int(pago_id_egreso), fecha_pago=fecha_pago, status=status, beneficiario_id=int(beneficiario_id), monto_total=float(monto_total),
                 cuenta_id=int(cuenta_id_egreso), forma_pago_id=int(forma_pago_id_egreso))

    #print('\nPago: \nid = {} \n status = {} \nfecha_pago = {}\n beneficiario_id = {} \nmonto_total= {} \n cuenta_id = {} \n forma_pago_id = {}'.format(pago_id_egreso,status,fecha_pago,beneficiario_id,monto_total,cuenta_id, forma_pago_id))

    return pago


def generar_detalle_egreso(R2_id, egreso, beneficiario_id):

    try: centro_negocios_id = int(mapping_centros_negocio[mapping_centros_negocio.GEZ_id == int(egreso['AlmQRecibe'])].R2_id)
    except: centro_negocios_id = centros_negocio_sin_definir_id

    monto = egreso['TotalAPagar']
    numero_control = str(egreso['NombreDMarca'])
    descripcion = str(egreso['TipoDescripcion'])

    detalle = DetallesEgreso(centro_negocios_id =int(centro_negocios_id), proveedor_id=int(beneficiario_id),
                             categoria_id=int(categoria_id), concepto_id=int(concepto_id), monto=float(monto),
                             numero_control=numero_control, descripcion=descripcion)



    return detalle








############### TRANSLATE INGRESOS ############


def translate_ingreso(ingreso):


    dias_para_vencimiento = 15
    status = 'por_conciliar'
    tipo_ingreso_id = tipo_ingreso_id # Definido en funcion 'initalize_global_var()

    # Checar centro de negocio de
    centro_negocio_tipo = mapping_centros_negocio[mapping_centros_negocio.GEZ_id == int(ingreso['SucID'])].tipo

    if centro_negocio_tipo == 'E-commerce':
        cliente_id = cliente_ecommerce_id
        concepto_ingresos_id = concepto_ingresos_tiendas_id

    elif centro_negocio_tipo == 'E-commerce':
        cliente_id = cliente_tiendas_id
        concepto_ingresos_id = concepto_ingresos_ecommerce_id

    else:
        cliente_id = cliente_otro_id
        concepto_ingresos_id = concepto_ingresos_otro_id



    empresa_id = int(mapping_empresas[mapping_empresas.GEZ_id == int(ingreso['EmpresaID'])].R2_id)

    referencia = ''
    fecha_vencimiento = str(ingreso['Fecha'] + timedelta(dias_para_vencimiento))
    fecha_programada_pago = str(ingreso['Fecha'] + timedelta(dias_para_vencimiento))
    fecha_documento = str(ingreso['Fecha'])
    numero_documento = ingreso['md_id']
    monto_total = ingreso['IngresoTotal']
    monto_pagado = 0
    costo_venta = ingreso['CostoTotal']
    iva_ingresos = ingreso['Iva_dIngresos']
    iva_ventas = ingreso['CostoTotalIva']
    utilidad_neta = ingreso['UtilidadNeta']
    monto_solicitado = 0
    monto_por_conciliar = 0
    comentario = ''
    pagado = False

    return status,tipo_ingreso_id, cliente_id, empresa_id, referencia, fecha_vencimiento, fecha_programada_pago, fecha_documento, numero_documento,monto_total,monto_pagado,\
           monto_solicitado, monto_por_conciliar,costo_venta,iva_ingresos,iva_ventas,utilidad_neta, pagado, comentario, concepto_ingresos_id




def generar_detalle_ingreso(R2_id, cliente_id, concepto_ingresos_id, detalle):

    try: centro_negocios_id = int(mapping_centros_negocio[mapping_centros_negocio.GEZ_id == int(detalle['SucID'])].R2_id)
    except: centro_negocios_id = centros_negocio_sin_definir_id


    detalle = DetallesIngreso(cliente_id=cliente_id,
                              categoria_id=categoria_ingresos_id,
                              concepto_id=concepto_ingresos_id,
                              centro_negocios_id=centro_negocios_id,
                              monto=detalle['monto_total'],
                              descripcion=detalle['nomconcept'], # ES LO QUE SE NECESITA PARA LA DESCRICPION?
                              numero_control = detalle['Referencia_Pago'], # ESTA BIEN ESTO?
                              ingreso_id = R2_id)


    return detalle


def generar_pago_ingreso_migracion(monto, cliente_id, detalle):

    status = 'por_conciliar'
    cliente_id = cliente_id

    monto_total = monto
    fecha_pago = str(detalle['fecha'])
    forma_pago_id = int(FormasPago.query.filter(FormasPago.nombre.ilike('%'+detalle['nomconcept']+'%')).all()[0].id)
    referencia_pago = str(detalle['Referencia_Pago'])
    try: cuenta_id = int(mapping_cuentas[mapping_cuentas.GEZ_id == int(detalle['ingr_sucursal'])].R2_id) # ayudame con esto
    except: cuenta_id = cuenta_id_por_definir

    cuenta_id = detalle['Expr1']   # Esto deberia de ser de mapping cuentas? El primer detalle que intente, el numero no coincidia con
    comentario = '' #Esta bien esto?

    pago_ingreso = Pagos_Ingresos(referencia_pago=referencia_pago, fecha_pago=fecha_pago, status=status, cliente_id=cliente_id,
                                  monto_total=monto_total, cuenta_id=cuenta_id,
                                  forma_pago_id=forma_pago_id, comentario  = comentario
                                  )


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
        cuenta_banco = (pd.read_sql("select provcta_numero from dbo.proveedores_cuentasdeposito where prov_vtaprov = {}".format(GEZ_id), con)).iloc[0,0]

    except: cuenta_banco = ''

    try:
        banco = (
        pd.read_sql("select provcta_banco from dbo.proveedores_cuentasdeposito where prov_vtaprov = {}".format(GEZ_id), con)).iloc[0,0]

    except: banco = ''

    saldo = 0

    status = 'Activo' if proveedor['pro_status'] else 'Inactivo'

    contacto_1, contacto_2, contacto_3 = agregar_contactos(proveedor)

    return GEZ_id, nombre, nombre_corto, RFC, direccion, comentarios, razon_social, cuenta_banco.rstrip(), banco, saldo, status, contacto_1,contacto_2, contacto_3






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
    numero = int(item['sucnsucursal'])
    tipo = 'Pendiente de Definir'
    direccion = get_direccion(item,variable)
    arrendadora = 'Pendiente de Definir'
    comentario = ''
    empresa_id = int(str(Empresas_Mapping.query.
                                        filter(Empresas_Mapping.GEZ_id == int(item['sucempresa'])).all())
                                        .replace('[','').replace(']',''))


    return numero, direccion, tipo, arrendadora, comentario, empresa_id




############### TRANSLATE NOMINA ############


def translate_empleados(item):


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







#########################################################################################################
#--------------------------------  Write Item to R2 table  -------------------------------- #
#########################################################################################################




def write_variable_R2(variable, R2_id, GEZ_id, nombre, variable_item, agregar_item, list_GEZ,con):

    if variable == 'empresas':

        variable_item = Empresas(id=int(R2_id),nombre=nombre)
        variable_map = Empresas_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))

    # agregar el item si no existe


    if variable == 'beneficiarios':

        GEZ_id, nombre, nombre_corto, RFC, direccion, comentarios, razon_social, cuenta_banco, banco, saldo, status, contacto_1,contacto_2, contacto_3 = translate_beneficiario(variable_item,variable,con)

        variable_item = Beneficiarios(id=R2_id, nombre=nombre,nombre_corto=nombre_corto, RFC=RFC,
                                      direccion=direccion, razon_social=razon_social,comentarios=comentarios,
                                      cuenta_banco=cuenta_banco, saldo=saldo, status=status, banco=banco)

        variable_item.contacto.append(contacto_1)
        variable_item.contacto.append(contacto_2)
        variable_item.contacto.append(contacto_3)


        variable_map = Beneficiarios_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))


    if variable == 'centros_negocio':

        numero, direccion, tipo, arrendadora, comentario, empresa_id = translate_centros_negocio(variable_item,variable)

        if int(variable_item['sucempresa']) == 1:

            variable_item = CentrosNegocio(id=R2_id, nombre=nombre, numero=numero, direccion=direccion,
                                           tipo=tipo, arrendadora=arrendadora, comentario=comentario,
                                           empresa_id=empresa_id)

            variable_map = CentrosNegocio_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))

        else: agregar_item = False


    if variable == 'empleados':

        nombre, apellido, segundo_appellido, puesto, sexo, tienda, departamento, fecha_nacimiento, fecha_alta, fecha_ingreso, fecha_contrato, \
        fecha_baja, motivo_baja, sueldo, prestamo_monto, prestamos_fecha_entrega, prestamos_fecha_vuelta = translate_empleados(variable_item)

        variable_item = Empleados(id=R2_id, nombre=nombre, apellido=apellido, segundo_appellido=segundo_appellido, puesto=puesto, sexo=sexo, tienda=tienda,
                                  departamento=departamento, fecha_nacimiento=fecha_nacimiento,fecha_alta=fecha_alta, fecha_ingreso=fecha_ingreso,
                                  fecha_contrato=fecha_contrato, fecha_baja=fecha_baja, motivo_baja=motivo_baja, sueldo=sueldo, prestamo_monto=prestamo_monto)

        variable_map = Empleados_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))

    if variable == 'egresos':

        fecha_documento, fecha_vencimiento, fecha_programada_pago, numero_documento, monto_total, monto_pagado, monto_solicitado, monto_por_conciliar, referencia, comentario, \
        pagado, status, beneficiario_id, empresa_id, iva, descuento, monto_documento, notas_credito, detalle = translate_egreso(R2_id, variable_item)


        if status == 'liquidado':
            pago = generar_pago_migracion(beneficiario_id, monto_total, variable_item)
            ep = EgresosHasPagos(egreso_id=int(R2_id), pago_id=int(pago.id), monto=float(monto_total))
            db.session.add(pago)
            db.session.add(ep)
        else:
            pago = None

        variable_item = Egresos(id=int(R2_id), fecha_documento=fecha_documento, fecha_vencimiento=fecha_vencimiento, fecha_programada_pago=fecha_programada_pago, numero_documento=str(numero_documento),
                                monto_total=float(monto_total), monto_pagado=float(monto_pagado), monto_solicitado=float(monto_solicitado),
                                monto_por_conciliar=float(monto_por_conciliar), referencia=str(referencia),comentario=comentario, pagado=pagado,status=status,
                                beneficiario_id=int(beneficiario_id), empresa_id=int(empresa_id), iva=float(iva), descuento=float(descuento), monto_documento=float(monto_documento),notas_credito=float(notas_credito))


        variable_map = Egresos_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))

        variable_item.detalles.append(detalle)

        # Generar Pago para los liquidados








    if variable == 'ingresos':

        status, tipo_ingreso_id, cliente_id, empresa_id, referencia, fecha_vencimiento, fecha_programada_pago, fecha_documento, numero_documento, monto_total, monto_pagado, \
        monto_solicitado, monto_por_conciliar, costo_venta, iva_ingresos, iva_ventas, utilidad_neta, pagado, detalle, concepto_ingresos_id = translate_ingreso(variable_item)

        sobrante_RDM = variable_item['SobranteRDM']

        # ---- Generar el Ingreso
        variable_item = Ingresos(id=int(R2_id), status=status, tipo_ingreso_id = tipo_ingreso_id, cliente_id =cliente_id,empresa_id=int(empresa_id),
                                 referencia=str(referencia), fecha_vencimiento=fecha_vencimiento, fecha_programada_pago=fecha_programada_pago,
                                 fecha_documento=fecha_documento, numero_documento=str(numero_documento),
                                 monto_total=float(monto_total), monto_pagado=float(monto_pagado),
                                 monto_solicitado=float(monto_solicitado), monto_por_conciliar=float(monto_por_conciliar),
                                 comentario='', pagado=pagado, costo_venta=float(costo_venta), iva_ingresos=float(iva_ingresos),
                                 iva_ventas=float(iva_ventas), utilidad_neta=float(utilidad_neta))

        # ----  Generar Pagos

        detalles = list_GEZ_Detalles[list_GEZ_Detalles.Movtos_ID == variable_item['md_id']]
        variable_map = Ingresos_Mapping(GEZ_id=int(GEZ_id), R2_id=int(R2_id))

        pdb.set_trace()
        # Por cada detalle encontrado del ingreso generar un detalle
        for i in range(len(detalles)):

            detalle = generar_detalle_ingreso(R2_id,cliente_id, concepto_ingresos_id, detalles.iloc[i, :])
            variable_item.detalles.append(detalle)

            if detalle['nomconcept'] != 'Efectivo':
                monto = detalle['monto_total']
                pago = generar_pago_ingreso_migracion(pago, monto)
                ep = IngresosHasPagos(ingreso_id=int(R2_id), pago_id=int(pago.id), monto=float(monto_total))
                db.session.add(pago)
                db.session.add(ep)

            if detalle['nomconcept'] == 'Efectivo':

                monto = pago['monto_total'] - sobrante_RDM
                pago = generar_pago_ingreso_migracion(pago, monto)
                ep = IngresosHasPagos(ingreso_id=int(R2_id), pago_id=int(pago.id), monto=float(monto_total))
                db.session.add(pago)
                db.session.add(ep)

                #Asi esta bien? o aunque el monto sea 0, se hace un pago?
                if (sobrante_RDM > 0) and (monto > 0):
                    monto = sobrante_RDM
                    generar_pago_ingreso_migracion(pago, monto)
                    ep = IngresosHasPagos(ingreso_id=int(R2_id), pago_id=int(pago.id), monto=float(monto_total))
                    db.session.add(pago)
                    db.session.add(ep)


    if agregar_item:
        db.session.add(variable_item)

        db.session.add(variable_map)
        # pdb.set_trace()
        db.session.commit()

    return







##########################################################################################################
#--------------------------------  Migrate Entire table from GEZ to R2  -------------------------------- #
##########################################################################################################



def migrate_table(con_GEZ, con_rdm, variable):

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
        variable_item = list_GEZ.iloc[i, :]


        if len(match) > 0:

            R2_id = match.iloc[0,1]

            # TODO: Updatear si se ha cancelado o no
            print('This id is already registered as R2_id = {} ! doing Nothing!'.format(R2_id))

            if variable == 'egreso':
                if str(variable_item['Cancelado']) == 'True':
                    egreso = Egresos.query.get(R2_id)
                    egreso.status = 'cancelado'
                    db.session.commit()

            if variable == 'beneficiario':
                if str(variable_item['pro_status']) == 'False':
                    beneficiario = Beneficiarios.query.get(R2_id)
                    beneficiario.status = 'cancelado'
                    db.session.commit()


        # Si no esta registrada, hacer lo siguiente
        else:
            print('This id is not registered! Registering needed!')


            #  Checar si el nombre de la compania ya existe en R2, aunque el id nos ea igual
            if GEZ_nombre != GEZ_id:
                for j in range(len(list_R2)):

                    if str(list_R2[j]) == GEZ_nombre:
                        agregar_item = False
                        R2_id = list_R2[j].id
                        break

            if agregar_item == True:
                R2_id = (map_cnt + i)


            write_variable_R2(variable, R2_id, GEZ_id, GEZ_nombre, variable_item, agregar_item, list_GEZ, con_GEZ)




def write_inital_conditions():

    try: Tipo_Ingreso.query.filter(Tipo_Ingreso.tipo == 'Ventas').all()[0].id
    except:
        tipo_i = Tipo_Ingreso(tipo='Ventas')
        db.session.add(tipo_i)

    # CLIENTES
    try: Clientes.query.filter(Clientes.nombre == 'Ventas Tiendas Fisicas').all()[0].id
    except:
        cliente = Clientes(nombre='Ventas Tiendas Fisicas', saldo_pendiente=0, saldo_por_conciliar=0, saldo_cobrado=0,status='conciliado')
        db.session.add(cliente)

    try: Clientes.query.filter(Clientes.nombre == 'Ventas Ecommerce').all()[0].id
    except:
        cliente = Clientes(nombre='Ventas Ecommerce', saldo_pendiente=0, saldo_por_conciliar=0, saldo_cobrado=0, status='conciliado')
        db.session.add(cliente)

    try:  Clientes.query.filter(Clientes.nombre == 'Ventas Adicionales').all()[0].id
    except:
        cliente = Clientes(nombre='Ventas Adicionales', saldo_pendiente=0, saldo_por_conciliar=0, saldo_cobrado=0, status='conciliado')
        db.session.add(cliente)

    # CUENTAS

    try:  Cuentas.query.filter(Cuentas.nombre == 'Prueba').all()[0].id
    except:
        cuenta = Cuentas(nombre='Prueba', saldo=0,  saldo_inicial=0)
        db.session.add(cuenta)

    try: Cuentas.query.filter(Cuentas.nombre == 'SinDefinir').all()[0].id
    except:
        cuenta = Cuentas(nombre='SinDefinir', saldo=0, saldo_inicial=0)
        db.session.add(cuenta)



    try: Cuentas.query.filter(Cuentas.nombre == 'BBVA 111').all()[0].id
    except:
        cuenta = Cuentas(nombre='BBVA 111', banco='BBVA', numero='0103783111', saldo=0, saldo_inicial=0)
        db.session.add(cuenta)


    try: Cuentas.query.filter(Cuentas.nombre == 'BBVA 189').all()[0].id
    except:
        cuenta = Cuentas(nombre='BBVA 189', banco='BANCOMER', numero='0103783189', saldo=0, saldo_inicial=0)
        db.session.add(cuenta)

    try:
        Cuentas.query.filter(Cuentas.nombre == 'BBVA 196').all()[0].id
    except:
        cuenta = Cuentas(nombre='BBVA 196', banco='AMERICAN EXPRESS', numero='0443850196', saldo=0, saldo_inicial=0)
        db.session.add(cuenta)

    try:
        Cuentas.query.filter(Cuentas.nombre == 'BMX').all()[0].id
    except:
        cuenta = Cuentas(nombre='BMX', banco='BANAMEX', numero='0055637', saldo=0, saldo_inicial=0)
        db.session.add(cuenta)

    try:
        Cuentas.query.filter(Cuentas.nombre == 'BB Clasica').all()[0].id
    except:
        cuenta = Cuentas(nombre='BB Clasica', banco='BAJIO', numero='0001615466', saldo=0, saldo_inicial=0)
    db.session.add(cuenta)


    try:
        Cuentas.query.filter(Cuentas.nombre == 'BB Inversion').all()[0].id
    except:
        cuenta = Cuentas(nombre='BB Inversion', banco='BAJIO', numero='', saldo=0, saldo_inicial=0)
        db.session.add(cuenta)

    try:
        Cuentas.query.filter(Cuentas.nombre == 'BX+').all()[0].id
    except:
        cuenta = Cuentas(nombre='BX+',banco='VE POR MAS', numero='28384', saldo=0, saldo_inicial=0)
        db.session.add(cuenta)

    try:
        Cuentas.query.filter(Cuentas.nombre == 'BBVA 6646').all()[0].id
    except:
        cuenta = Cuentas(nombre='BBVA 6646',banco='Ecommerce', numero='0100906646', saldo=0, saldo_inicial=0)
        db.session.add(cuenta)

    try:
        Cuentas.query.filter(Cuentas.nombre == 'Oficina Efectivo').all()[0].id
    except:
        cuenta = Cuentas(nombre='Oficina Efectivo',banco='Oficina', numero='01', saldo=0, saldo_inicial=0)
        db.session.add(cuenta)



    # CATEGORIAS
    try: Categorias.query.filter(Categorias.nombre == 'Comprass').all()[0].id
    except:
        categoria = Categorias(nombre="Compras", tipo='egreso')
        db.session.add(categoria)

    try: Categorias.query.filter(Categorias.nombre == 'Ventas').all()[0].id
    except:
        categoria = Categorias(nombre="Ventas", tipo='ingreso')
        db.session.add(categoria)

    # CONCEPTOS
    try: Conceptos.query.filter(Conceptos.nombre == 'Zapato').all()[0].id
    except:
        concepto = Conceptos(nombre='Zapato', categoria_id=1)
        db.session.add(concepto)

    try: Conceptos.query.filter(Conceptos.nombre == 'Tiendas').all()[0].id
    except:
        concepto = Conceptos(nombre='Tiendas', categoria_id=2)
        db.session.add(concepto)

    try: Conceptos.query.filter(Conceptos.nombre == 'Ecommerce').all()[0].id
    except:
        concepto = Conceptos(nombre='Ecommerce', categoria_id=2)
        db.session.add(concepto)

    try: Conceptos.query.filter(Conceptos.nombre == 'Adicionales').all()[0].id
    except:
        concepto = Conceptos(nombre='Adicionales', categoria_id=2)
        db.session.add(concepto)

    # FORMAS DE PAGO

    try: FormasPago.query.filter(FormasPago.nombre == 'Efectivo').all()[0].id
    except:
        forma_pago = FormasPago(nombre='Efectivo')
        db.session.add(forma_pago)

    try: FormasPago.query.filter(FormasPago.nombre == 'Transferencia').all()[0].id
    except:
        forma_pago = FormasPago(nombre='Transferencia')
        db.session.add(forma_pago)

    try: FormasPago.query.filter(FormasPago.nombre == 'Cheque').all()[0].id
    except:
        forma_pago = FormasPago(nombre='Cheque')
        db.session.add(forma_pago)

    # CENTRO DE NEGOCIOS
    try: CentrosNegocio.query.filter(CentrosNegocio.nombre == 'SinDefinir').all()[0].id
    except:
        centro_negocios = CentrosNegocio(nombre='SinDefinir')
        db.session.add(centro_negocios)

    db.session.commit()















# PAGE APPENDIX:

#   1. Random Functions (Utils)
#   2. Initialize Variables
#   3. Translations
#   4. Write Item
#   5. Migrate table
#   6. Write initial conditions




########## MAIN FUNCTION ##########


def run_all_migrations():

    variables = ['empresas', 'beneficiarios', 'centros_negocio', 'empleados', 'egresos', 'ingresos']


    con_GEZ, con_rdm = get_connections()
    print('0. Connections Initiated \n')

    write_inital_conditions()



    # Generar Variables Globales
    for variable in variables[:-1]:

        print('Variable! = ',variable)
        initialize_global_var(con_GEZ, variable)
        print('1. Gloabl varables Initiated \n')

        # Migrate all of the records in GEZ for varaible
        migrate_table(con_GEZ, con_rdm, variable)
        print('2.Table Migrated succesfully \n')



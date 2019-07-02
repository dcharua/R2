import pyodbc

import pandas as pd
import numpy as np
import sys
from flask import Flask, url_for
#from app.db_models.models import *






# Create connection
con_GEZ = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=gez;uid=gezsa001;pwd=gez9105ru2")
con_rdm = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=rdm;uid=gezsa001;pwd=gez9105ru2")
#con_R2 = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};server=localhost;PORT=3306;database=R2;uid=root;pwd=Adri*83224647")

def get_data(con,sql,filename = ''):
    data = pd.read_sql(sql,con)
    if filename != '': data.to_csv(filename,index = False)
    return data



# TODO: Ver como haverle para que funcione esto

def agregar_beneficiario():
    if request.form:
        data = request.form
        beneficiario = Beneficiarios(nombre=data["nombre"], RFC=data["RFC"], 
            direccion=data["direccion"], razon_social=data["razon_social"],
            cuenta_banco=data["cuenta_banco"], saldo = 0, status = 'liquidado', banco=data["banco"])
        for i in range(len(data.getlist("nombre_contacto"))):
            contacto = ContactoBeneficiario(nombre=data.getlist("nombre_contacto")[i], correo=data.getlist("correo_contacto")[i],
            telefono=data.getlist("telefono_contacto")[i], extension=data.getlist("extension_contacto")[i], puesto=data.getlist("puesto_contacto")[i])
            beneficiario.contacto.append(contacto) 
        for i in range(len(data.getlist("categoria"))):
                categoria = Categorias.query.get(data.getlist("categoria")[i])
                beneficiario.categorias.append(categoria)          
        db.session.add(beneficiario)
        db.session.commit()   
        return redirect("/administracion/beneficiarios")

    

def define_egreso_R2():
    columns = ['id','fecha_documento','fecha_vencimiento','fecha_programada_pago','numero_documento',
    'monto_total','monto_pagado','monto_solicitado','monto_por_conciliar','referencia','comentario','pagado',
    'status','beneficiario_id','empresa_id','iva','descuento','nota_credito']
    egreso = pd.DataFrame(columns = columns)
    return egreso




def migrate_egresos(con):

    filename = "recepcion_documentos.csv"

    try: 
        data = pd.read_csv(filename)
    
    except:
        print('No file name found: ',filename)
        data = get_data(con,"SELECT * FROM dbo.recepcion_documentos",filename)


    egreso = define_egreso_R2()

    print(len(data))
    print(data.head())


def get_mapping(GEZ_id,name):

    # Leer tabla de mapping
    try: 
        mapping_table = pd.read_csv(name+'_mapping.csv')
        
    except:
        mapping_table = pd.DataFrame(columns = ['GEZ_id','R2_id'])
        mapping_table.to_csv(name+'_mapping.csv',index = False)
        mapping_table = pd.read_csv(name+'_mapping.csv')
    
    # Checar is el proveedor esta registrado
    R2_id = mapping_table[mapping_table['GEZ_id'] == GEZ_id].R2_id
    
    # Si no, hacer lo siguiente
    if len(R2_id) == 0:
        R2_id = int(max(mapping_table['R2_id']) + 1)

        # TODO: Manera de agregar a MySQL
        mapping_table.loc[len(mapping_table)+1] = [int(GEZ_id),int(R2_id)]
        mapping_table.to_csv(name+'_mapping.csv',index = False)


    print(mapping_table.head())
    return R2_id


def get_direccion(proveedor):

    calle = str(proveedor['pro_calle'])
    colonia = str(proveedor['pro_colonia'])
    cp = str(proveedor['pro_cp'])
    
    #TODO: mapear el estado y pais
    estado = str(proveedor['pro_estado'])
    pais = str(proveedor['pro_pais'])
    return calle + ' ' + colonia + ' ' + cp + ' ' + estado + ' ' + pais


def get_contactos(proveedor):

    #TODO Combnar en una lista
    contacto = pd.DataFrame(columns = ['nombre','email','telefono','extension','Puesto'])
    contacto.loc[0] = [proveedor['pro_creycobranza'], 
                 'pro_cobranza_email',
                 proveedor['pro_cobranza_tel'],
                 '',
                 'Cobranza']

    contacto.loc[1] = [proveedor['pro_director'], 
                 '',
                 '',
                 '',
                 'Director']

    contacto.loc[2] = ['SRITA. SILVIA VALDEZ, FRANCISCA JUAREZ', 
                 '',
                 proveedor['pro_telefonos'],
                 '',
                 'Otros']

    return contacto


def translate_proveedor(proveedor):

    GEZ_id = int(proveedor['pro_numero'])

    R2_id = get_mapping(GEZ_id,'proveedor')
    nombre = proveedor['pro_razon']
    RFC = proveedor['pro_rfc']
    direccion = get_direccion(proveedor)
    comentarios = proveedor['pro_observaciones']

    # Estas no encontre en GEZ
    razon_social = ''
    cuenta_banco = ''
    banco = ''

    # PREGUNTA: Saldo es 0 para empezar? Hay saldos en GEZ que hay que checar
    saldo = 0

    # PREGUNTA: status es liquidado? en GEZ, hay status True y false, checar que es eso
    status = 'liquidado'
    
    contactos = get_contactos(proveedor)
    print(contactos.head())



def get_detalles_egreso(egreso):


    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    centro_negocios_id = Column(Integer, ForeignKey('centros_negocio.id'))
    centro_negocios = relationship("CentrosNegocio", back_populates="detalles_egresos")
    proveedor_id = Column(Integer, ForeignKey('beneficiarios.id'))
    proveedor = relationship("Beneficiarios", back_populates="detalles_egresos")
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    categoria = relationship("Categorias", back_populates="detalles_egresos")
    concepto_id = Column(Integer, ForeignKey('conceptos.id'))
    concepto = relationship("Conceptos", back_populates="detalles_egresos")
    monto = Column(Numeric(10, 2))
    numero_control = Column(String(200))
    descripcion = Column(String(200)) 
    egreso_id = Column(Integer, ForeignKey('egresos.id'))

    return 

def translate_egreso(egreso):

    GEZ_id = int(egreso['rcep_numero'])

    R2_id = get_mapping(GEZ_id,'egresos')


    id = R2_id
    fecha_documento = egreso['rcep_fechadoc']
    fecha_vencimiento = egreso['rcep_vence']  # Como crear esto? En proveedores, hay que crear una columna nueva con 'pro_diascredito'
    fecha_programada_pago = egreso['rcep_fechapago'] # Como crear esto? usar lo de arriba y hacer el martes
    numero_documento = egreso['rcep_documento']


    monto_total =  egreso['rcep_grandtotal'] + egreso['rcep_impuesto']  # Seguro? Algo se ve raro....
    monto_pagado =  0
    monto_solicitado =  0
    monto_por_conciliar = 0
    referencia = 'N/A'  #Preguntar a Uri que poner de referencia
    comentario = egreso['rcep_obsevaciones']
    pagado = False    
    status = 'pendiente' 

    beneficiario_id = get_mapping_name(egreso['rcep_proveedor'],'proveedor')  
    # (Otra pregunta: queremos usar marca?)

    empresa_id = get_mapping(egreso['rcep_empresa'],'empresa') # De donde hago el mapping para empresas?
    
    # Agregamos algo con estos?
        #detalles = relationship("DetallesEgreso")
        #pagos = relationship("Pagos", secondary='egresos_has_pagos')

    # NUEVAS COLUMNAS!!!
    iva = get_mapping(egreso['rcep_impuesto'],'impuestos')
    descuento = egreso['rcep_descuento']
    monto_documento = monto_total - descuento
    #QUe hacer con notas de credito??
    nota_credito = 0



def migrate_proveedor(con):

    filename = "proveedores.csv"
    sql = "SELECT * FROM dbo." + filename[:-4]
    print(sql)

    # Leer la informacion de proveedores de GEZ
    # TODO: quitar el try y solo leer de la base de datos, solo usamos el read csv para hacerlo mas rapido.
    try: 
        data = pd.read_csv(filename)
    
    except:
        print('No file name found: ',filename)
        data = get_data(con,"SELECT * FROM dbo.proveedores",filename)

    data = data.sort_values(by = 'pro_numero')



    #for i in range(len(data)):

    # Get proveedor from GEZ data
    proveedor = data.iloc[1,:]

    #get data for proveedor
    proveedor_data = translate_proveedor(proveedor)
    
    

def migrate_egresos(con):

    filename = "recepcion_documentos.csv"
    sql = "SELECT * FROM dbo." + filename[:-4]
    print(sql)

    # Leer la informacion de proveedores de GEZ
    # TODO: quitar el try y solo leer de la base de datos, solo usamos el read csv para hacerlo mas rapido.
    try: 
        data = pd.read_csv(filename)
        data = data[data.rcep_cancelado == False]
        data = data[data.rcep_cxp == True]
    
    except:
        print('No file name found: ',filename)
        data = get_data(con,sql,filename)
        data = data[data.rcep_cancelado == False]
        data = data[data.rcep_cxp == True]
        data.to_csv(filename,index = False)

    #for i in range(len(data)):

    # Get proveedor from GEZ data
    egreso = data.iloc[1,:]
    print(egreso.head())
    #get data for each egreso
    #proveedor_data = translate_egreso(egreso)



def migrate_ingresos(con):
    sql = "SELECT * FROM dbo.ingresos"
    #data = pd.read_sql(sql,con)
    #data.to_csv('ingresos.csv',index = False)
    #print(len(data))
    #print(data.head())

    sql = "SELECT * FROM dbo.ventasdiario_c_cta_deposito_rdm"
    data = pd.read_sql(sql,con)
    data.to_csv('ventasdiario.csv',index = False)
    print(len(data))
    print(data.head())











#migrate_proveedor(con_GEZ)
migrate_egresos(con_GEZ)




from sqlalchemy import Binary, Column, Integer, String, Date, Numeric, Table, ForeignKey, Boolean, not_, event
from app import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from flask import flash, redirect

Base = declarative_base()


beneficiario_has_categorias = Table('beneficiario_has_categorias', db.Model.metadata,
    Column('beneficiario_id', Integer, ForeignKey('beneficiarios.id'), primary_key=True),
    Column('categoria_id', Integer, ForeignKey('categorias.id'), primary_key=True)
)

#Tables in alpha order

class Beneficiarios(db.Model):
    __tablename__ = 'beneficiarios'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer,unique=True, nullable=False, primary_key=True)
    nombre = Column(String(50))
    RFC = Column(String(20))
    direccion = Column(String(150))
    razon_social = Column(String(50))
    cuenta_banco = Column(String(20))
    banco = Column(String(30))
    saldo = Column(Numeric(10, 2)) 
    status = Column(String(20))
    comentarios = Column(String(250))
    categorias = relationship("Categorias", secondary=beneficiario_has_categorias)
    
    egresos = relationship("Egresos")
    detalles_egresos = relationship("DetallesEgreso")
    
    pagos = relationship("Pagos")
    
    contacto=relationship("ContactoBeneficiario") 

    def __repr__(self):
        return self.nombre 

    def get_beneficiario_by_id(self, id):
        print(id)
        return Beneficiarios.query.get(id)

class Categorias(db.Model):
    __tablename__ = 'categorias'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    nombre = Column(String(50))
    conceptos = relationship("Conceptos")
    detalles_egresos = relationship("DetallesEgreso")
    detalles_ingresos = relationship("DetallesIngreso")
    beneficiarios = relationship("Beneficiarios", secondary=beneficiario_has_categorias)
    def __repr__(self):
        return self.nombre        



class CentrosNegocio(db.Model):
    __tablename__ = 'centros_negocio'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    nombre = Column(String(50))
    numero = Column(String(20))
    tipo = Column(String(50))
    direccion =  Column(String(50))
    arrendadora = Column(String(50))
    comentario = Column(String(250))
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    empresa = relationship("Empresas", back_populates="centro")
    detalles_egresos = relationship("DetallesEgreso")
    detalles_ingresos = relationship("DetallesIngreso")

    def __repr__(self):
        return self.nombre


class Clientes(db.Model):
    __tablename__ = 'clientes'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    RFC = Column(String(50))
    direccion = Column(String(50))
    razon_social = Column(String(50))
    cuenta_banco = Column(String(50))
    saldo = Column(Numeric(10, 2))
    status = Column(String(50))
    comentarios = Column(String(50))
    banco = Column(String(50))
    
    contacto = relationship("ContactoCliente") 
    
    ingresos = relationship("Ingresos")
    detalles_ingresos = relationship("DetallesIngreso")
    pagos_ingresos = relationship("Pagos_Ingresos")
    
    def __repr__(self):
        return self.nombre

class Conceptos(db.Model):
    __tablename__ = 'conceptos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    nombre = Column(String(50))
    detalles_egresos = relationship("DetallesEgreso")
    detalles_ingresos = relationship("DetallesIngreso")
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    def __repr__(self):
        return self.nombre       

class ContactoBeneficiario(db.Model):
    __tablename__ = 'contacto_beneficiario'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    nombre = Column(String(50))
    correo = Column(String(50))
    telefono = Column(String(30))
    extension = Column(String(10))
    puesto = Column(String(30))
    beneficiario_id= Column(Integer, ForeignKey('beneficiarios.id'))

    def __repr__(self):
        return self.nombre  
    
class ContactoCliente(db.Model):
    __tablename__ = 'contacto_cliente'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    nombre = Column(String(50))
    correo = Column(String(50))
    telefono = Column(String(30))
    extension = Column(String(10))
    puesto = Column(String(30))
    cliente_id = Column(Integer, ForeignKey('clientes.id'))

    def __repr__(self):
        return self.nombre


class Cuentas(db.Model):
    __tablename__ = 'cuentas'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    nombre = Column(String(50))
    banco = Column(String(50))
    numero = Column(String(50))
    comentario = Column(String(250))
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    empresa = relationship("Empresas", back_populates="cuenta")
    saldo = Column(Numeric(10, 2))  
    numero_cheque = Column(Numeric(10, 2))     
    pagos = relationship("Pagos")
    pagos_ingresos = relationship("Pagos_Ingresos")

    def __repr__(self):
        return self.banco + ' / ' + self.numero       


class DetallesEgreso(db.Model):
    __tablename__ = 'egresos_detalles'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    centro_negocios_id = Column(Integer, ForeignKey('centros_negocio.id'))
    centro_negocios = relationship("CentrosNegocio", back_populates="detalles_egresos")
    proveedor_id = Column(Integer, ForeignKey('beneficiarios.id'))
    proveedor = relationship("Beneficiarios", back_populates="detalles_egresos")
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    categoria = relationship("Categorias", back_populates="detalles_egresos")
    concepto_id = Column(Integer, ForeignKey('conceptos.id'))
    concepto = relationship("Conceptos", back_populates="detalles_egresos")
    monto = Column(Numeric(asdecimal=True))
    numero_control = Column(String(200))
    descripcion = Column(String(200)) 
    egreso_id = Column(Integer, ForeignKey('egresos.id'))

    def __repr__(self):
        return '<DetallesEgreso {}>'.format(self.id) 
    
class DetallesIngreso(db.Model):
    __tablename__ = 'ingresos_detalles'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
   
    
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    cliente = relationship("Clientes", back_populates="detalles_ingresos")
    
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    categoria = relationship("Categorias", back_populates="detalles_ingresos")
    concepto_id = Column(Integer, ForeignKey('conceptos.id'))
    concepto = relationship("Conceptos", back_populates="detalles_ingresos")
    centro_negocios_id = Column(Integer, ForeignKey('centros_negocio.id'))
    centro_negocios = relationship("CentrosNegocio", back_populates="detalles_ingresos")

    monto = Column(Numeric(10, 2))
    numero_control = Column(String(200))
    descripcion = Column(String(200)) 
    ingreso_id = Column(Integer, ForeignKey('ingresos.id'))
    

    def __repr__(self):
        return '<DetallesIngreso {}>'.format(self.id) 

class EgresosHasPagos(db.Model):
    __tablename__ = 'egresos_has_pagos'

    egreso_id = Column(Integer, ForeignKey('egresos.id'), primary_key=True)
    pago_id = Column(Integer, ForeignKey('pagos_egresos.id'), primary_key=True)
    monto = Column(Numeric(10, 2))
    egreso = relationship("Egresos", backref=backref("pagos_assoc"))
    pago =  relationship("Pagos", backref=backref("egresos_assoc"))


class Egresos(db.Model):

    __tablename__ = 'egresos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    fecha_vencimiento = Column(Date)
    fecha_programada_pago = Column(Date)
    numero_documento = Column(String(20))
    monto_total =  Column(Numeric(10, 2))
    monto_pagado =  Column(Numeric(10, 2))
    monto_solicitado =  Column(Numeric(10, 2))
    monto_por_conciliar = Column(Numeric(10, 2))
    referencia = Column(String(40))
    comentario = Column(String(200))
    pagado = Column(Boolean)
    status = Column(String(20))
    detalles = relationship("DetallesEgreso")
    beneficiario_id= Column(Integer, ForeignKey('beneficiarios.id'))
    beneficiario = relationship("Beneficiarios", back_populates="egresos")
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    empresa = relationship("Empresas", back_populates="egresos")
    pagos = relationship("Pagos", secondary='egresos_has_pagos')

    def setStatus(self, pagos=None):
        egreso = self.query.get(self.id)
        pagos = egreso.query.join(Egresos.pagos).filter_by(id = self.id) 
        m_pagado = egreso.monto_pagado + egreso.monto_solicitado
        m_pendiente = egreso.monto_total - egreso.monto_pagado
        if m_pagado == 0:
            egreso.status='pendiente'
        elif m_pendiente != 0 and egreso.monto_solicitado !=0 and (m_pendiente - egreso.monto_solicitado == 0):
            egreso.status = 'solicitado'
        elif m_pagado == egreso.monto_total:
            if egreso.monto_por_conciliar == 0:
                egreso.status = 'liquidado'
            else:
                egreso.status ='por_conciliar'

        elif m_pagado < egreso.monto_total:
            egreso.status = 'parcial'
 
      

    def __repr__(self):
        return '<Egreso {}>'.format(self.id)    

    def get_egreso_id(self, id):
        return Egresos.query.filter_by(id=id).first()
    
    
 

class Empresas(db.Model):
    __tablename__ = 'empresas'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    egresos = relationship("Egresos")
    centro = relationship("CentrosNegocio")
    cuenta = relationship("Cuentas")
    ingresos = relationship("Ingresos")
    
    def __repr__(self):
        return self.nombre 


class FormasPago(db.Model):
    __tablename__ = 'formas_pago'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    pagos = relationship("Pagos")
    pagos_ingresos = relationship("Pagos_Ingresos")

    def __repr__(self):
        return self.nombre  




#########3#########3#########3#########3#########3#########3
#########3#########3#########3#########3#########3#########3

class Ingresos(db.Model):

    __tablename__ = 'ingresos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    status = Column(String(20))
    tipo_ingreso_id = Column(Integer, ForeignKey('tipo_ingre.id'))
    tipo_ingreso = relationship("Tipo_Ingreso", back_populates="ingresos")
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    cliente = relationship("Clientes", back_populates="ingresos") 
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    empresa = relationship("Empresas", back_populates="ingresos") 
    referencia = Column(String(200))
    fecha_vencimiento = Column(Date)
    fecha_programada_pago = Column(Date)
    numero_documento = Column(String(20))
    monto_total = Column(Numeric(10, 2))
    monto_pagado = Column(Numeric(10, 2))
    monto_solicitado = Column(Numeric(10, 2))
    monto_por_conciliar = Column(Numeric(10, 2))
    detalles = relationship("DetallesIngreso")
    comentario = Column(String(200))
    pagado = Column(Boolean)
    pagos_ingresos = relationship("Pagos_Ingresos", secondary='ingresos_has_pagos')

    def setStatus(self, pagos_ingresos=None):
        if pagos_ingresos is None:
            ingreso = self.query.get(self.id)
            pagos_ingresos = ingreso.query.join(Ingresos.pagos_ingresos).filter_by(id = self.id) 
        monto_pagos = 0


        if (self.monto_pagado == 0):
            self.status = 'pendiente'
            
        elif ((self.monto_pagado > 0) and (self.monto_pagado < self.monto_total)):
            self.status = 'parcial'
            
            if(self.monto_pagado == self.monto_total):
                self.status = 'por_conciliar'

        elif (self.monto_pagado == self.monto_total):
             self.status = 'liquidado'
            


    def __repr__(self):
        return '<ingreso {}>'.format(self.id)    

    
    
    
class IngresosHasPagos(db.Model):
    __tablename__ = 'ingresos_has_pagos'

    ingreso_id = Column(Integer, ForeignKey('ingresos.id'), primary_key=True)
    pago_id = Column(Integer, ForeignKey('pagos_ingresos.id'), primary_key=True)
    monto = Column(Numeric(10, 2))
    ingreso = relationship("Ingresos", backref=backref("pagos_assoc"))
    pago =  relationship("Pagos_Ingresos", backref=backref("ingresos_assoc"))  
    

class Pagos_Ingresos(db.Model):
    __tablename__ = 'pagos_ingresos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    referencia_pago = Column(String(20))
    fecha_pago = Column(Date)
    fecha_conciliacion = Column(String(20))
    status = Column(String(20))
    referencia_conciliacion = Column(String(20))
    monto_total = Column(Numeric(10, 2))
    comentario = Column(String(200))
    cuenta_id = Column(Integer, ForeignKey('cuentas.id'))
    cuenta = relationship("Cuentas", back_populates="pagos_ingresos")
    
    forma_pago_id = Column(Integer, ForeignKey('formas_pago.id'))
    forma_pago = relationship("FormasPago", back_populates="pagos_ingresos")
    
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    cliente = relationship("Clientes", back_populates="pagos_ingresos")
    
    ingresos = relationship("Ingresos", secondary='ingresos_has_pagos')


    def __repr__(self):
        return '<Pago {}>'.format(self.id) 




class Pagos(db.Model):
    __tablename__ = 'pagos_egresos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    referencia_pago = Column(String(40))
    fecha_pago = Column(Date)
    fecha_conciliacion = Column(Date)
    status = Column(String(20))
    referencia_conciliacion = Column(String(40))
    monto_total = Column(Numeric(10, 2))
    comentario = Column(String(200))
    cuenta_id = Column(Integer, ForeignKey('cuentas.id'))
    cuenta = relationship("Cuentas", back_populates="pagos")
    forma_pago_id = Column(Integer, ForeignKey('formas_pago.id'))
    forma_pago = relationship("FormasPago", back_populates="pagos")
    beneficiario_id = Column(Integer, ForeignKey('beneficiarios.id'))
    beneficiario = relationship("Beneficiarios", back_populates="pagos")
    egresos = relationship("Egresos", secondary='egresos_has_pagos')

    def __repr__(self):
        return '<Pago {}>'.format(self.id)           




class Tipo_Ingreso(db.Model):
    __tablename__ = 'tipo_ingre'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    tipo = Column(String(50))
    ingresos = relationship("Ingresos")

    def __repr__(self):
        return self.tipo
    

#After insert events
def after_insert_listener(mapper, connection, target):
    flash('Egreso con id %i ingresado' %(target.id), 'success')
    return redirect("egresos/perfil_egreso/%i" % (target.id))
    
event.listen(Egresos, 'after_insert', after_insert_listener)


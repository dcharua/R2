from sqlalchemy import Binary, Column, Integer, String, Date, Numeric, Table, ForeignKey, Boolean
from app import db
from sqlalchemy.orm import relationship
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

#Association tables 

egresos_has_pagos = Table('egresos_has_pagos', db.Model.metadata,
    Column('egreso_id', Integer, ForeignKey('egresos.id'), primary_key=True),
    Column('pago_id', Integer, ForeignKey('pagos_egresos.id'), primary_key=True)
)


#Tables
class Egresos(db.Model):

    __tablename__ = 'egresos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    fecha_vencimiento = Column(Date)
    fecha_programada_pago = Column(Date)
    numero_documento = Column(String(20))
    monto_total = Column(Numeric)
    referencia = Column(String(40))
    comentario = Column(String(200))
    detalles = relationship("DetallesEgreso")
    beneficiario_id= Column(Integer, ForeignKey('beneficiarios.id'))
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    pagos = relationship("Pagos", secondary=egresos_has_pagos)


    def __repr__(self):
        return '<Egreso {}>'.format(self.id)    

    def get_egreso_id(self, id):
        return Egresos.query.filter_by(id=id).first()

class DetallesEgreso(db.Model):
    __tablename__ = 'egresos_detalles'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    centro_negocios_id = Column(Integer, ForeignKey('centros_negocio.id'))
    proveedor_id = Column(Integer, ForeignKey('beneficiarios.id'))
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    concepto_id = Column(Integer, ForeignKey('conceptos.id'))
    monto = Column(Numeric)
    numero_control = Column(String(200))
    descripcion = Column(String(200)) 
    egreso_id= Column(Integer, ForeignKey('egresos.id'))

    def __repr__(self):
        return '<DetallesEgreso {}>'.format(self.id)   


class Pagos(db.Model):
    __tablename__ = 'pagos_egresos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer,  unique=True, nullable=False, primary_key=True)
    referencia_pago = Column(String(20))
    fecha_pago = Column(Date)
    conciliado = Column(Boolean)
    referencia_conciliacion= Column(String(20))
    monto_total = Column(Numeric)
    comentario = Column(String(200))
    cuenta_id = Column(Integer, ForeignKey('cuentas.id'))
    forma_pago_id = Column(Integer, ForeignKey('formas_pago.id'))
    beneficiario_id= Column(Integer, ForeignKey('beneficiarios.id'))

    def __repr__(self):
        return '<Pago {}>'.format(self.id)           


class Beneficiarios(db.Model):
    __tablename__ = 'beneficiarios'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    RFC = Column(String(20))
    direccion = Column(String(150))
    razon_social = Column(String(20))
    cuenta_banco = Column(String(20))
    banco = Column(String(30))
    saldo = Column(Numeric) 
    egresos = relationship("Egresos")
    pagos = relationship("Pagos")
   

    def __repr__(self):
        return self.nombre 

    def get_beneficiario_by_id(self, id):
        print(id)
        return Beneficiarios.query.get(id)


class ContactoBeneficiario(db.Model):
    __tablename__ = 'contacto_beneficiario'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    correo = Column(String(50))
    telefono = Column(String(30))
    extension = Column(String(10))
    puesto = Column(String(30))
    beneficiario_id= Column(Integer, ForeignKey('beneficiarios.id'))

    def __repr__(self):
        return self.nombre 

class Empresas(db.Model):
    __tablename__ = 'empresas'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    egresos = relationship("Egresos")

    def __repr__(self):
        return self.nombre 


class CentrosNegocio(db.Model):
    __tablename__ = 'centros_negocio'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    detalles_egresos = relationship("DetallesEgreso")

    def __repr__(self):
        return self.nombre

class Categorias(db.Model):
    __tablename__ = 'categorias'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    detalles_egresos = relationship("DetallesEgreso")

    def __repr__(self):
        return self.nombre


class Conceptos(db.Model):
    __tablename__ = 'conceptos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    detalles_egresos = relationship("DetallesEgreso")

    def __repr__(self):
        return self.nombre       

class Cuentas(db.Model):
    __tablename__ = 'cuentas'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    banco = Column(String(50))
    numero = Column(String(50))
    saldo = Column(Numeric)    
    pagos = relationship("Pagos")

    def __repr__(self):
        return self.banco 


class FormasPago(db.Model):
    __tablename__ = 'formas_pago'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    pagos = relationship("Pagos")

    def __repr__(self):
        return self.nombre        
#Event listeners
def after_insert_listener(mapper, connection, target):
    # 'target' is the inserted object
    print(target.id)

event.listen(Egresos, 'after_insert', after_insert_listener)


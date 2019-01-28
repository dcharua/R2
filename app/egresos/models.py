from sqlalchemy import Binary, Column, Integer, String, Date, Numeric, Table, ForeignKey
from app import db
from sqlalchemy.orm import relationship
from sqlalchemy import event


class Egresos(db.Model):

    __tablename__ = 'egresos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    beneficiario = Column(String(20))
    fecha_vencimiento = Column(Date)
    fecha_programada_pago = Column(Date)
    numero_documento = Column(String(20))
    monto_total = Column(Numeric)
    referencia = Column(String(40))
    empresa = Column(String(40))
    comentario = Column(String(200))
    detalles = relationship("DetallesEgreso")

    def __repr__(self):
        return '<Egreso {}>'.format(self.id)    

    def get_egreso_id(self, id):
        return Egresos.query.filter_by(id=id).first()

class DetallesEgreso(db.Model):
    __tablename__ = 'egresos_detalles'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    centro_negocios = Column(String(20))
    proveedor = Column(String(50))
    categoria = Column(String(50))
    concepto = Column(String(50))
    monto = Column(Numeric)
    numero_control = Column(String(200))
    descripcion = Column(String(200)) 
    egreso_id= Column(Integer, ForeignKey('egresos.id'))

    def __repr__(self):
        return '<DetallesEgreso {}>'.format(self.id)   



def after_insert_listener(mapper, connection, target):
    # 'target' is the inserted object
    print(target.id)

event.listen(Egresos, 'after_insert', after_insert_listener)


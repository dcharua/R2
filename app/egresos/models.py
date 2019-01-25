from sqlalchemy import Binary, Column, Integer, String, Date, Numeric
from app import db


class Egresos(db.Model):

    __tablename__ = 'egresos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    beneficiario = Column(String(20))
    fecha_vencimiento = Column(Date)
    fecha_programada_pago = Column(Date)
    numero_documento = Column(String)
    monto = Column(Numeric)

    def __init__(self, beneficiario, fecha_vencimiento, fecha_programada_pago, numero_documento, monto):
        self.beneficiario=beneficiario
        self.fecha_vencimiento=fecha_vencimiento
        self.fecha_programada_pago=fecha_programada_pago
        self.numero_documento=numero_documento
        self.monto=monto;
   

    def get_egreso_id(self, id):
        return Egresos.query.filter_by(id=id).first()


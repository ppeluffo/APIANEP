import db as db

from sqlalchemy import Column, Integer, String, Float, DateTime

class Datos(db.Base):
    '''
    Clase que representa a la tabla de datos 
    '''
    __tablename__ = 'datos'

    id = Column(Integer, primary_key=True)
    fechadata = Column(DateTime)
    fechasys = Column(DateTime)
    equipo = Column(String)
    tag = Column(String)
    valor = Column(Float)

    def __repr__(self):
        return f"{self.id},{self.fechadata},{self.fechasys},{self.equipo},{self.tag},{self.valor}"
    

class ControlAcceso(db.Base):
    '''
    Clase que representa a la tabla control_acceso
    donde guardamos el ultimo id que servimos
    '''
    __tablename__ = 'control_acceso'

    id = Column(Integer, primary_key=True)
    access_token = Column(String)
    last_row = Column(Integer)


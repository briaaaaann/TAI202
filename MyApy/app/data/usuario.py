from sqlalchemy import Column, Integer, String
from app.data.db import Base

class usuario(Base):
    __tablename__="tb-usuarios"
    id = Column(Integer, primary_key = True, index = True)
    nombre = Column(String)
    edad = Column(Integer)


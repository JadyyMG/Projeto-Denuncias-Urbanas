from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..database import Base

# Entidade Usuário (RF01 / Item 5.3)
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha = Column(String) # RNF02: Segurança [cite: 108]

# Entidade Denúncia (RF02 / UC01)
class Denuncia(Base):
    __tablename__ = "denuncias"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String) # RF02 [cite: 94]
    foto_url = Column(String)  # UC02 [cite: 114]
    status = Column(String, default="Pendente") # RF03 [cite: 96]
    data_criacao = Column(DateTime, default=datetime.now)

# Entidade Logs (RF08 / UC07)
class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    acao = Column(String) # RF08 [cite: 102]
    data = Column(DateTime, default=datetime.now)
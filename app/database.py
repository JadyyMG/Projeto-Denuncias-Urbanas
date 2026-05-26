from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuração do Banco de Dados SQLite
# Conforme Item 5.3 da Documentação - Persistência de Dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./denuncias_urbanas.db"

# O engine é o ponto de entrada para o banco de dados
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cada instância da classe SessionLocal será uma sessão de banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para a criação dos modelos declarativos
Base = declarative_base()
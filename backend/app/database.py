from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
load_dotenv()

# Parametros da configuracao da conexao
user = os.getenv('user')
senha = os.getenv('senha')
host = os.getenv('host')
port = os.getenv('port')
banco = os.getenv('banco')

# Conexao
DATABASE_URL = f'postgresql+psycopg://{user}:{senha}@{host}:{port}/{banco}'

# enginde de conexao com o db
engine = create_engine(DATABASE_URL)

# configuracao de sessao
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db
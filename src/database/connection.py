from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# URL de conexão com o banco de dados
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://autonowrite_user:autonowrite_pass@localhost/autonowrite_db"
)

# Cria a engine do SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Sessão do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Dependência para injeção de dependência
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

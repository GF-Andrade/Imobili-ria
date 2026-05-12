import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- O PULO DO GATO PARA O EXECUTÁVEL ---
# Verifica se está rodando como .exe (frozen) ou como script .py
if getattr(sys, 'frozen', False):
    # Caminho da pasta onde o arquivo .exe está
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Caminho da pasta onde o script .py está
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Monta o caminho completo para o banco de dados na pasta do projeto
DB_PATH = os.path.join(BASE_DIR, "imobiliaria.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Log para te ajudar a debugar (vai aparecer na janela preta)
print(f"DEBUG: Banco de dados esperado em: {DB_PATH}")

# 2. Criamos o engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 3. Sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base
Base = declarative_base()

# 5. Dependência
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
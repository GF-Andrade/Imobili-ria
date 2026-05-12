from passlib.context import CryptContext

# Define o algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash_senha(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha_pura: str, senha_hash: str):
    return pwd_context.verify(senha_pura, senha_hash)
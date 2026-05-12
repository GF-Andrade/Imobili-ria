from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# --- SCHEMAS DE IMÓVEL ---
class ImovelBase(BaseModel):
    titulo: str
    tipo: str
    bairro: str
    regiao: str
    quartos: int
    banheiros: int
    vagas: int
    valor: float
    fotos: Optional[str] = None
    # --- NOVOS CAMPOS PARA O MAPA E OBSERVAÇÕES ---
    endereco_rua: Optional[str] = None
    endereco_numero: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    descricao: Optional[str] = None  # Usaremos este para as Observações

class ImovelCreate(ImovelBase):
    pass

class ImovelOut(ImovelBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True


# --- SCHEMAS DE CLIENTE ---
class ClienteBase(BaseModel):
    nome: str
    telefone: str
    email: Optional[str] = None # Tornamos opcional caso o cliente não tenha e-mail

class ClienteCreate(ClienteBase):
    # Adicionamos aqui também se quiser salvar observações sobre o cliente no futuro
    tipo_interesse: Optional[str] = None
    observacoes: Optional[str] = None

class ClienteOut(ClienteBase):
    id: int
    tipo_interesse: Optional[str] = None
    observacoes: Optional[str] = None

    class Config:
        from_attributes = True


# --- SCHEMAS DE CORRETOR ---
class CorretorCreate(BaseModel):
    nome: str
    email: EmailStr 
    senha: str

class CorretorOut(BaseModel):
    id: int
    nome: str
    email: EmailStr

    class Config:
        from_attributes = True


# --- SCHEMA DE LOGIN ---
class Login(BaseModel):
    email: EmailStr
    senha: str
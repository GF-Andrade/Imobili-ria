from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Imovel(Base):
    __tablename__ = "imoveis"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    tipo = Column(String)  # Ex: Casa, Apartamento, Lote
    bairro = Column(String, index=True)
    regiao = Column(String) # Ex: Leste, Sul, etc.
    quartos = Column(Integer)
    banheiros = Column(Integer)
    vagas = Column(Integer)
    valor = Column(Float)
    fotos = Column(String) # URLs das imagens separadas por vírgula
    
    # --- NOVOS CAMPOS PARA O MAPA E ENDEREÇO ---
    endereco_rua = Column(String, nullable=True)
    endereco_numero = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Usamos 'Text' para descrição pois observações podem ser longas
    descricao = Column(Text, nullable=True) 
    
    criado_em = Column(DateTime, server_default=func.now())


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    telefone = Column(String)
    email = Column(String, nullable=True)
    
    # --- CAMPOS PARA GESTÃO DE INTERESSE ---
    tipo_interesse = Column(String, nullable=True) # Ex: Compra ou Aluguel
    observacoes = Column(Text, nullable=True)


class Corretor(Base):
    __tablename__ = "corretores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha = Column(String)
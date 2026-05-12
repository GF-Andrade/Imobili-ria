from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
import os, shutil, uuid, sys

if getattr(sys, 'frozen', False):
    # Se estiver rodando como executável
    bundle_dir = sys._MEIPASS
else:
    # Se estiver rodando como script normal
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

if bundle_dir not in sys.path:
    sys.path.insert(0, bundle_dir)

# Imports do seu projeto
from database import engine, get_db, Base
from models import Base, Imovel, Cliente, Corretor
from schemas import ImovelCreate, ClienteCreate, CorretorCreate, Login
from auth import gerar_hash_senha, verificar_senha

# ==========================================
# GESTÃO DE CAMINHOS (CRÍTICO PARA PYINSTALLER)
# ==========================================
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    INTERNAL_STATIC_DIR = os.path.join(sys._MEIPASS, "static")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INTERNAL_STATIC_DIR = os.path.join(BASE_DIR, "static")

UPLOAD_DIR = os.path.join(BASE_DIR, "fotos_imoveis")
if not os.path.exists(UPLOAD_DIR): 
    os.makedirs(UPLOAD_DIR)

# ==========================================
# INICIALIZAÇÃO
# ==========================================
app = FastAPI(title="Andrade Tech Imóveis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ==========================================
# ROTAS DE NAVEGAÇÃO
# ==========================================

@app.get("/")
async def root():
    return RedirectResponse(url="/static/login.html")

@app.get("/home")
async def carregar_home():
    dashboard_path = os.path.join(INTERNAL_STATIC_DIR, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    raise HTTPException(status_code=404, detail="dashboard.html não encontrado")

# ==========================================
# MONTAGEM DE PASTAS ESTÁTICAS
# ==========================================

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

if os.path.exists(INTERNAL_STATIC_DIR):
    app.mount("/static", StaticFiles(directory=INTERNAL_STATIC_DIR), name="static")

# ==========================================
# ROTAS DE APOIO
# ==========================================

@app.get("/favicon.ico", include_in_schema=False)
async def favicon(): return Response(status_code=204)

BAIRROS = ["Aclimação", "Alto Umuarama", "Alvorada", "Carajás", "Chácaras Panorama", "Chácaras Tubalina", "Cidade Jardim", "Custódio Pereira", "Distrito Industrial", "Dona Zulmira", "Gávea", "Granada", "Grand Ville", "Granja Marileusa", "Guarani", "Jaraguá", "Jardim Brasília", "Jardim Canaã", "Jardim das Palmeiras", "Jardim Europa", "Jardim Holanda", "Jardim Inconfidência", "Jardim Ipanema", "Jardim Karaíba", "Jardim Patrícia", "Jardim Sul", "Lagoinha", "Laranjeiras", "Luizote de Freitas", "Mansões Aeroporto", "Mansour", "Maravilha", "Marta Helena", "Minas Gerais", "Monte Hebron", "Morada da Colina", "Morada do Sol", "Morada dos Pássaros", "Morada Nova", "Morumbi", "Nossa Senhora das Graças", "Nova Uberlândia", "Novo Mundo", "Pacaembu", "Pampulha", "Patrimônio", "Planalto", "Portal do Vale", "Presidente Roosevelt", "Residencial Gramado", "Residencial Integração", "Residencial Pequis", "Santa Luzia", "Santa Mônica", "Santa Rosa", "São Jorge", "São José", "Saraiva", "Segismundo Pereira", "Shopping Park", "Taiaman", "Tibery", "Tocantins", "Tubalina", "Umuarama", "Vigilato Pereira"] 
REGIOES = ["Centro", "Norte", "Sul", "Leste", "Oeste"]

@app.get("/bairros")
def listar_bairros(): return BAIRROS

@app.get("/regioes")
def listar_regioes(): return REGIOES

# --- AUTENTICAÇÃO ---

@app.post("/auth/registrar")
def cadastrar_corretor(dados: CorretorCreate, db: Session = Depends(get_db)):
    if db.query(Corretor).filter(Corretor.email == dados.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    dados_dict = dados.model_dump()
    dados_dict["senha"] = gerar_hash_senha(dados_dict["senha"])
    novo = Corretor(**dados_dict)
    db.add(novo); db.commit()
    return {"msg": "ok"}

@app.post("/auth/login")
def login(dados: Login, db: Session = Depends(get_db)):
    user = db.query(Corretor).filter(Corretor.email == dados.email).first()
    if not user or not verificar_senha(dados.senha, user.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"usuario": {"nome": user.nome, "email": user.email}}

# --- IMÓVEIS ---

@app.post("/imoveis")
def criar_imovel(dados: ImovelCreate, db: Session = Depends(get_db)):
    try:
        novo = Imovel(**dados.model_dump())
        db.add(novo); db.commit(); db.refresh(novo)
        return {"msg": "ok", "id": novo.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/imoveis")
def listar_imoveis(db: Session = Depends(get_db)):
    return db.query(Imovel).all()

@app.get("/imoveis/busca")
def buscar_imoveis(tipo: str = None, bairro: str = None, valor_max: float = None, t: str = None, db: Session = Depends(get_db)):
    query = db.query(Imovel)
    if tipo: query = query.filter(Imovel.tipo == tipo)
    if bairro: query = query.filter(Imovel.bairro == bairro)
    if valor_max: query = query.filter(Imovel.valor <= valor_max)
    return query.all()

@app.get("/imoveis/{id}")
def buscar_imovel_por_id(id: int, db: Session = Depends(get_db)):
    imovel = db.query(Imovel).filter(Imovel.id == id).first()
    if not imovel: raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return imovel

@app.delete("/imoveis/{id}")
def deletar_imovel(id: int, db: Session = Depends(get_db)):
    imovel = db.query(Imovel).filter(Imovel.id == id).first()
    if imovel: 
        db.delete(imovel); db.commit()
    return {"msg": "ok"}

# --- CLIENTES (CORRIGIDO E COMPLETO) ---

@app.post("/clientes")
def criar_cliente(dados: ClienteCreate, db: Session = Depends(get_db)):
    novo = Cliente(**dados.model_dump())
    db.add(novo); db.commit()
    return {"msg": "ok"}

@app.get("/clientes")
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).all()

@app.get("/clientes/{id}")
def buscar_cliente_por_id(id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente: 
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@app.put("/clientes/{id}")
def atualizar_cliente(id: int, dados: ClienteCreate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    for key, value in dados.model_dump().items():
        setattr(cliente, key, value)
    
    try:
        db.commit()
        return {"msg": "ok"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar")

@app.delete("/clientes/{id}")
def deletar_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if cliente: 
        db.delete(cliente); db.commit()
    return {"msg": "ok"}

# --- UPLOAD ---

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    nome = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, nome)
    with open(path, "wb") as buffer: 
        shutil.copyfileobj(file.file, buffer)
    return {"url": f"/uploads/{nome}"}

if __name__ == "__main__":
    import uvicorn
    import webview
    import multiprocessing
    from threading import Thread

    # 1. Configuração para o servidor rodar em segundo plano
    def start_server():
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

    # 2. Suporte para o executável Windows
    multiprocessing.freeze_support()

    # 3. Inicia o servidor em uma thread separada
    t = Thread(target=start_server)
    t.daemon = True
    t.start()

    # 4. Cria a janela "fechada" do sistema
    # O parâmetro 'url' aponta para o servidor que acabamos de subir
    webview.create_window(
        'Andrade Tech Imóveis', 
        'http://127.0.0.1:8001/',
        width=1200,
        height=800,
        resizable=True,
        confirm_close=True
    )
    
    # 5. Inicia a interface (o ícone da janela será o mesmo do .exe automaticamente)
    webview.start()
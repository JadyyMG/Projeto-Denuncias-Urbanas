# main.py — API FastAPI corrigida
# Correções: rota /usuarios duplicada removida, CORS adicionado para o Flutter

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import tabelas

# Cria as tabelas no banco
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Denúncias Urbanas API")

# ── CORS — necessário para o Flutter conseguir chamar a API ────────────────
# Libera requisições de qualquer origem (ajuste em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependência: abre e fecha sessão do banco automaticamente
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── ROTA DE STATUS ─────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"status": "Servidor e Banco de Dados Ativos"}


# ── ROTA DE CADASTRO (RF01) ────────────────────────────────────────────────
@app.post("/usuarios")
def cadastrar_usuario(nome: str, email: str, senha: str, db: Session = Depends(get_db)):
    # Verifica se email já existe
    existente = db.query(tabelas.Usuario).filter(tabelas.Usuario.email == email).first()
    if existente:
        return {"erro": "E-mail já cadastrado"}

    novo_usuario = tabelas.Usuario(nome=nome, email=email, senha=senha)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {"mensagem": "Usuário cadastrado com sucesso!", "id": novo_usuario.id}


# ── ROTA DE LOGIN (RF01) ───────────────────────────────────────────────────
@app.post("/login")
def login(email: str, senha: str, db: Session = Depends(get_db)):
    usuario = db.query(tabelas.Usuario).filter(tabelas.Usuario.email == email).first()

    if not usuario or usuario.senha != senha:
        return {"erro": "E-mail ou senha incorretos"}

    return {
        "mensagem": "Login realizado com sucesso!",
        "usuario": {"id": usuario.id, "nome": usuario.nome}
    }


# ── ROTA DE CRIAR DENÚNCIA (UC01) ─────────────────────────────────────────
@app.post("/denuncias")
def criar_denuncia(usuario_id: int, descricao: str, foto: str = "", db: Session = Depends(get_db)):
    nova_denuncia = tabelas.Denuncia(
        usuario_id=usuario_id,
        descricao=descricao,
        foto_url=foto
    )
    db.add(nova_denuncia)
    db.commit()
    db.refresh(nova_denuncia)

    # Log da ação (RF08)
    novo_log = tabelas.Log(acao=f"Denúncia {nova_denuncia.id} criada pelo usuário {usuario_id}")
    db.add(novo_log)
    db.commit()

    return {"mensagem": "Denúncia registrada!", "protocolo": nova_denuncia.id}


# ── ROTA DE LISTAR DENÚNCIAS (UC06) ───────────────────────────────────────
@app.get("/denuncias")
def listar_denuncias(db: Session = Depends(get_db)):
    denuncias = db.query(tabelas.Denuncia).all()
    return denuncias


# ── ROTA DE ATUALIZAR STATUS (RF03) ───────────────────────────────────────
@app.patch("/denuncias/{denuncia_id}/status")
def atualizar_status(denuncia_id: int, status: str, db: Session = Depends(get_db)):
    denuncia = db.query(tabelas.Denuncia).filter(tabelas.Denuncia.id == denuncia_id).first()

    if not denuncia:
        return {"erro": "Denúncia não encontrada"}

    denuncia.status = status
    db.commit()

    # Log da atualização
    log = tabelas.Log(acao=f"Status da denúncia {denuncia_id} atualizado para '{status}'")
    db.add(log)
    db.commit()

    return {"mensagem": "Status atualizado!", "id": denuncia_id, "status": status}

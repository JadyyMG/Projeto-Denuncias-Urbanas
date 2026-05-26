from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import tabelas

# Cria as tabelas no banco (ISO/IEC 12207)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Denúncias Urbanas API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROTA DE HOME ---
@app.get("/")
def home():
    return {"status": "Servidor e Banco de Dados Ativos"}

# --- ROTA DE DENÚNCIAS (UC01) ---
@app.post("/denuncias")
def criar_denuncia(usuario_id: int, descricao: str, foto: str, db: Session = Depends(get_db)):
    nova_denuncia = tabelas.Denuncia(usuario_id=usuario_id, descricao=descricao, foto_url=foto)
    db.add(nova_denuncia)
    db.commit()
    db.refresh(nova_denuncia)
    
    # Registro de Log (RF08)
    novo_log = tabelas.Log(acao=f"Denúncia {nova_denuncia.id} criada")
    db.add(novo_log)
    db.commit()
    
    return {"mensagem": "Denúncia registrada!", "protocolo": nova_denuncia.id}

# --- ADICIONE A ROTA DE LOGIN AQUI (RF01) ---
@app.post("/login")
def login(email: str, senha: str, db: Session = Depends(get_db)):
    # Busca o usuário pelo email no banco de dados
    usuario = db.query(tabelas.Usuario).filter(tabelas.Usuario.email == email).first()
    
    # Validação simples (RNF02 - Segurança)
    if not usuario or usuario.senha != senha:
        return {"erro": "E-mail ou senha incorretos"}
    
    return {
        "mensagem": "Login realizado com sucesso!",
        "usuario": {"id": usuario.id, "nome": usuario.nome}
    }

# --- ADICIONE A ROTA DE CADASTRO ABAIXO (Para teste) ---
@app.post("/usuarios")
def cadastrar_usuario(nome: str, email: str, senha: str, db: Session = Depends(get_db)):
    novo_usuario = tabelas.Usuario(nome=nome, email=email, senha=senha)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {"mensagem": "Usuário criado!", "id": novo_usuario.id}

# Rota para Criar Novo Usuário (Necessário para testar o Login)
@app.post("/usuarios")
def cadastrar_usuario(nome: str, email: str, senha: str, db: Session = Depends(get_db)):
    # 1. Cria a instância do novo usuário
    novo_usuario = tabelas.Usuario(
        nome=nome, 
        email=email, 
        senha=senha # Lembrete: RNF02 sugere criptografia futura
    )
    
    # 2. Salva no banco de dados
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return {
        "mensagem": "Usuário cadastrado com sucesso!", 
        "id": novo_usuario.id
    }

# UC06: Visualizar histórico de denúncias
@app.get("/denuncias")
def listar_denuncias(db: Session = Depends(get_db)):
    # Busca todas as denúncias no banco de dados
    denuncias = db.query(tabelas.Denuncia).all()
    return denuncias
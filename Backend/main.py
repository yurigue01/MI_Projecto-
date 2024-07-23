from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import smtplib
from json import dumps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from io import BytesIO
from hashing import Hash
from fastapi.encoders import jsonable_encoder
from json import JSONEncoder
from bson import ObjectId
from custom_json_encoder import CustomJSONEncoder  # Importa o CustomJSONEncoder do módulo jsonencoder
from decimal import Decimal
from datetime import datetime
from typing import Optional
from jwttoken import create_access_token
from fastapi.encoders import jsonable_encoder
from pandas import read_csv, read_excel 
from typing import List



# Função para enviar e-mails
def send_email(to_email, subject, body):
    smtp_server = "sandbox.smtp.mailtrap.io"
    smtp_port = 587
    smtp_login = "92463ddfaf41ea"
    smtp_password = "7a3617bc2177ef"
    from_email = "yurigue2104@gmail.com"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_login, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")

send_email("a39358@alunos.ipb.pt", "Assunto do E-mail", "Corpo do E-mail")


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)  # Convert ObjectId to string
        return super().default(o)

app = FastAPI()

# Configuração do CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do MongoDB
mongodb_uri = 'mongodb+srv://yuri:Bibi_1234@cluster0.0ejlijv.mongodb.net/?retryWrites=true&w=majority'
port = 8000
client = MongoClient(mongodb_uri, port)
db = client["User"]

# Modelos Pydantic
class User(BaseModel):
    username: str
    name: str
    email: str
    password: str
    is_active: bool = False
    is_email_verified: bool = False

class Candidatura(BaseModel):
    tipo: str
    pagamento: Decimal
    data: datetime
    epoca: str
    ano_lect: str
    estado: str
    observacao: str
    responsavel: str
    nome: str
    tipo_doc: str
    num_doc: int
    validade: str
    data_nasc: str
    sexo: str
    nif: int
    email: str
    pais_resid: str
    cod_postal: str
    localidade: str
    telemovel: str
    pais: str
    id_curso: str

class Analise(BaseModel):
    classif: int
    inf_result: str
    observacao: str
    resultado: str
    nota_curri: Decimal
    nota_forma: Decimal
    id_cand: str

class Curso(BaseModel):
    cod_curso: int
    n_plano: int
    nome: str
    id_escol: str

class Escola(BaseModel):
    cod_escola: str
    nome: str

class Formacao(BaseModel):
    grau: str
    nome: str
    id_instit: str

class Anexo(BaseModel):
    nome: str
    tipo: str
    id_cand: str
    id_analis: str

class Instituicao(BaseModel):
    cod: str
    nome: str
    id_pais: str

class Pais(BaseModel):
    sigla: str
    nome: str

class Afinidade(BaseModel):
    afinidade: bool
    id_curso: str
    id_form: str

class Classificacao(BaseModel):
    nota: Decimal
    escala: str
    obsevacao: str
    nota_convert: Decimal

class Login(BaseModel):
    email_or_username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Função para enviar e-mail de verificação
@app.post('/send_verification_email')
def send_verification_email(email: str):
    user = db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No user found with this {email} email')
    subject = "Verificação de E-mail"
    message = f"Por favor, clique no link para verificar o seu e-mail: http://localhost:3000/verify_email/{user['email']}"
    try:
        print("Enviando email e-mail de verificação...")
    except Exception as e:
        print(f"Erro ao enviar o e-mail:{e}")
    send_email(email, subject, message)
    return {"message": "E-mail de verificação enviado com sucesso"}

# Função para verificar e-mail
@app.get('/verify_email/{email}')
def verify_email(email: str):
    user = db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No user found with this {email} email')

    if user.get("is_email_verified"):
        return {"message": "E-mail já verificado"}

    db["users"].update_one({"email": email}, {"$set": {"is_email_verified": True}})
    return {"message": "E-mail verificado com sucesso"}

# Rota raiz
@app.get("/")
def read_root():
    return {"data": "Hello World"}

# Função para registrar usuário
@app.post('/register')
def create_user(request: User):
    try:
        print("Criando novo utilizador...")
        hashed_pass = Hash.bcrypt(request.password)
        user_object = dict(request)
        user_object["password"] = hashed_pass
        user_object["is_email_verified"] = False
        user_id = db["users"].insert_one(user_object)
        send_verification_email(request.email)
        print("Utilizador registado com sucesso. Por favor, verifique o seu e-mail.")
        return {"message": "Utilizador registado com sucesso. Por favor, verifique o seu e-mail."}
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return {"message": f"Erro ao criar usuário: {e}"}

# Função de login
@app.post('/login')
def login(request: Login):
    user = db["users"].find_one({"email": request.email_or_username})
    if not user:
        user = db["users"].find_one({"username": request.email_or_username})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not Hash.verify(user["password"], request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer", "username": user["username"]}

# Rota para upload de arquivos
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = None
    
    # Determine o tipo de arquivo e carregue os dados
    if file.filename.endswith('.csv'):
        df = read_csv(BytesIO(contents))
    elif file.filename.endswith('.xlsx'):
        df = read_excel(BytesIO(contents))
    else:
        raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")

    # Converta o DataFrame para uma lista de dicionários
    data = df.to_dict(orient="records")
    
    # Serialize os dados manualmente usando seu CustomJSONEncoder
    data_serializable = dumps(data, cls=CustomJSONEncoder)
    
    # Opcional: Salve os dados no MongoDB
    try:
        db["candidaturas"].insert_many(data)
        print(f"Dados inseridos no MongoDB: {data}")
    except Exception as e:
        print(f"Erro ao salvar dados no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar dados no banco de dados")
    
    # Retorne os dados serializados como resposta
    return JSONResponse(content=data_serializable) 
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

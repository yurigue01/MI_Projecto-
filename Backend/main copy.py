from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from hashing import Hash
from jwttoken import create_access_token
from oauth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from pymongo import MongoClient

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import smtplib
from email.message import EmailMessage
# configurar servidor SMTP e login

smtp_server = "sandbox.smtp.mailtrap.io"
smtp_port = 587
smtp_login = "92463ddfaf41ea"
smtp_password = "7a3617bc2177ef"

app = FastAPI()
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


mongodb_uri = 'mongodb+srv://yuri:Bibi_1234@cluster0.0ejlijv.mongodb.net/?retryWrites=true&w=majority'
port = 8000
client = MongoClient(mongodb_uri, port)
db = client["User"]


class User(BaseModel):
    username: str
    name: str
    email: str
    password: str
    is_active: bool = False


class Login(BaseModel):
	email: str
	password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


def send_email_confirmation(to_email, confirmation_token):
    # configurar a mensagem de email
    message = MIMEMultipart()
    message["Subject"] = "Confirme a sua conta!"
    message["From"] = smtp_login

    # corpo da mensagem
    text = "Clique no link abaixo para confirmar a sua conta:\n\n"
    confirmation_url = f"http://link.com/confirmar-email?token={confirmation_token}"
    text += confirmation_url
    message.attach(MIMEText(text))

    # enviar o email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_login, smtp_password)
        server.sendmail(smtp_login, to_email, message.as_string())


@app.get("/")
def read_root(current_user: User = Depends(get_current_user)):
	return {"data": "Hello OWrldgggg"}


@app.post('/register')
def create_user(request: User):

	hashed_pass = Hash.bcrypt(request.password)
	user_object = dict(request)
	user_object["password"] = hashed_pass
	user_id = db["users"].insert_one(user_object)
    #send_email_confirmation("yurigue2104@gmail.com", "tttthss")
	return {"res":"created"}

@app.post('/login')
def login(request: Login):
    user = db["users"].find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Wrong email or password')
    
    if not Hash.verify(user["password"], request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Wrong email or password')
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    return {"access_token": access_token, "token_type": "bearer", "username": user["username"]}




    
    
    

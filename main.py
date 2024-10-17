from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()  # Inicializa la aplicación FastAPI

# Middleware para habilitar CORS (Cross-Origin Resource Sharing) que es necesario para permitir solicitudes desde un dominio diferente al de la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las direcciones
    allow_credentials=True,  # Permite credenciales
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los encabezados
)

# Monta archivos estáticos para servir desde el directorio "static"
app.mount("/static", StaticFiles(directory="static"), name="static")

# Base de datos simulada para almacenar transacciones
transactions_db = []
current_balance = 0  # Balance actual

# Variables para rastrear el mayor gasto
max_expense = 0
max_expense_date = ""

# Modelo para transacciones, utilizando Pydantic para validación
class Transaction(BaseModel):
    description: str  # Descripción de la transacción
    amount: float     # Monto de la transacción
    transaction_type: str  # Tipo de transacción: "ingreso" o "gasto"
    date: str         # Fecha de la transacción

# Modelo para el balance inicial
class InitialBalance(BaseModel):
    balance: float    # Balance inicial

# Endpoint para establecer el balance inicial
@app.post("/initial_balance/")
async def set_initial_balance(balance: InitialBalance):
    global current_balance  # Utiliza la variable global
    current_balance = balance.balance  # Establece el balance actual
    return {"message": "Balance inicial establecido", "balance": current_balance}

# Endpoint para agregar una transacción
@app.post("/transactions/")
async def add_transaction(transaction: Transaction):
    global current_balance, max_expense, max_expense_date  # Utiliza variables globales para actualizar el estado de la aplicación
    transactions_db.append(transaction)  # Agrega la transacción a la base de datos

    # Actualiza el balance según el tipo de transacción
    if transaction.transaction_type == "ingreso":
        current_balance += transaction.amount  # Suma al balance
    else:
        current_balance -= transaction.amount  # Resta del balance

        # Verifica si esta transacción es el mayor gasto
        if transaction.amount > max_expense:
            max_expense = transaction.amount  # Actualiza el mayor gasto
            max_expense_date = transaction.date  # Guarda la fecha del mayor gasto

    return {"message": "Transacción añadida", "balance": current_balance}  # Devuelve el mensaje y el balance

# Endpoint para obtener todas las transacciones
@app.get("/transactions/", response_model=List[Transaction])
async def get_transactions():
    return transactions_db  # Devuelve la lista de transacciones

# Endpoint para obtener el balance actual
@app.get("/balance/")
async def get_balance():
    return {"balance": current_balance}  # Devuelve el balance actual

# Endpoint para obtener el mayor gasto registrado
@app.get("/max_expense/")
async def get_max_expense():
    return {"max_expense": max_expense, "date": max_expense_date}  # Devuelve el mayor gasto y su fecha

# Endpoint raíz para servir el archivo HTML principal
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with open("templates/index.html") as f:  # Abre el archivo HTML
        return f.read()  # Devuelve el contenido del archivo


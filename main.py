from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Middleware para CORS que permite que la API sea consumida por cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")  # Para montar archivos en la ruta /static

# Simulación de base de datos
transactions_db = []
current_balance = 0
max_expense = 0
max_expense_date = ""


# Modelos
class Transaction(BaseModel):
    description: str
    amount: float
    transaction_type: str  # "ingreso" o "gasto"
    date: str


class InitialBalance(BaseModel):
    balance: float


# Rutas para la aplicación financiera
@app.post("/initial_balance/")
async def set_initial_balance(balance: InitialBalance):
    global current_balance
    current_balance = balance.balance
    return {"message": "Balance inicial establecido", "balance": current_balance}


@app.post("/transactions/")
async def add_transaction(transaction: Transaction):
    global current_balance, max_expense, max_expense_date
    transactions_db.append(transaction)

    if transaction.transaction_type == "ingreso":
        current_balance += transaction.amount
    else:
        current_balance -= transaction.amount
        if transaction.amount > max_expense:
            max_expense = transaction.amount
            max_expense_date = transaction.date

    return {"message": "Transacción añadida", "balance": current_balance}


@app.get("/transactions/", response_model=List[Transaction])
async def get_transactions(sort: str = "default"):
    if sort == "date":
        # Ordenar por fecha (asumiendo que la fecha está en formato 'YYYY-MM-DD')
        return sorted(transactions_db, key=lambda x: x.date)
    elif sort == "amount":
        # Ordenar por monto
        return sorted(transactions_db, key=lambda x: x.amount)
    else:
        # Por defecto: devolver en el orden original
        return transactions_db


@app.get("/balance/")
async def get_balance():
    return {"balance": current_balance}


@app.get("/max_expense/")
async def get_max_expense():
    return {"max_expense": max_expense, "date": max_expense_date}


# Rutas para servir las páginas HTML
@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    with open("templates/index.html") as f:
        return f.read()


@app.get("/app", response_class=HTMLResponse)
async def read_app(request: Request):
    with open("templates/app.html") as f:
        return f.read()

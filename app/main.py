from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import engine, SessionLocal, Base
from app import models
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ledger API", version="0.1.0")

# --------------------------
# DB Dependency
# --------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------
# Pydantic Schemas
# --------------------------
class AccountCreate(BaseModel):
    name: str
    balance: Optional[Decimal] = 0.0
    currency: Optional[str] = "USD"

class AccountResponse(BaseModel):
    id: int
    name: str
    balance: Decimal
    currency: str

    class Config:
        orm_mode = True

class TransactionCreate(BaseModel):
    type: str
    source_account_id: Optional[int] = None
    destination_account_id: Optional[int] = None
    amount: Decimal
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    type: str
    source_account_id: Optional[int]
    destination_account_id: Optional[int]
    amount: Decimal
    status: str

    class Config:
        orm_mode = True

# --------------------------
# Account Endpoints
# --------------------------
@app.post("/accounts/", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    db_account = models.Account(
        name=account.name,
        balance=account.balance,
        currency=account.currency
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@app.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.get("/accounts/", response_model=list[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(models.Account).all()

# --------------------------
# Transaction Endpoints
# --------------------------
@app.post("/transactions/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    # Validate accounts
    if transaction.type in ["transfer", "withdrawal"]:
        source_account = db.query(models.Account).filter(models.Account.id == transaction.source_account_id).first()
        if not source_account:
            raise HTTPException(status_code=404, detail="Source account not found")
        if source_account.balance < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

    if transaction.type in ["transfer", "deposit"]:
        if transaction.destination_account_id:
            dest_account = db.query(models.Account).filter(models.Account.id == transaction.destination_account_id).first()
            if not dest_account:
                raise HTTPException(status_code=404, detail="Destination account not found")

    # Create transaction
    db_transaction = models.Transaction(
        type=transaction.type,
        source_account_id=transaction.source_account_id,
        destination_account_id=transaction.destination_account_id,
        amount=transaction.amount,
        description=transaction.description,
        status=models.TransactionStatus.completed
    )
    db.add(db_transaction)

    # Ledger entries & balances
    if transaction.type == "deposit" and transaction.destination_account_id:
        dest_account.balance += transaction.amount
        db.add(models.LedgerEntry(
            account_id=transaction.destination_account_id,
            transaction=db_transaction,
            entry_type=models.EntryType.credit,
            amount=transaction.amount
        ))
    elif transaction.type == "withdrawal" and transaction.source_account_id:
        source_account.balance -= transaction.amount
        db.add(models.LedgerEntry(
            account_id=transaction.source_account_id,
            transaction=db_transaction,
            entry_type=models.EntryType.debit,
            amount=transaction.amount
        ))
    elif transaction.type == "transfer":
        source_account.balance -= transaction.amount
        dest_account.balance += transaction.amount
        db.add(models.LedgerEntry(
            account_id=transaction.source_account_id,
            transaction=db_transaction,
            entry_type=models.EntryType.debit,
            amount=transaction.amount
        ))
        db.add(models.LedgerEntry(
            account_id=transaction.destination_account_id,
            transaction=db_transaction,
            entry_type=models.EntryType.credit,
            amount=transaction.amount
        ))

    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# --------------------------
# Ledger Endpoints
# --------------------------

@app.get("/ledger/{account_id}")
def get_ledger_entries(account_id: int, db: Session = Depends(get_db)):
    entries = (
        db.query(models.LedgerEntry)
        .filter(models.LedgerEntry.account_id == account_id)
        .all()
    )

    if not entries:
        raise HTTPException(status_code=404, detail="No ledger entries found")

    return [
        {
            "id": entry.id,
            "transaction_id": entry.transaction_id,
            "entry_type": entry.entry_type,
            "amount": str(entry.amount),
            "timestamp": entry.timestamp
        }
        for entry in entries
    ]

# --------------------------
# Root Endpoint
# --------------------------
@app.get("/")
def root():
    return {"message": "Ledger API is running"}

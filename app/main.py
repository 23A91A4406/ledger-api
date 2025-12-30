from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db import get_db, engine
from app import models, schemas
from app.services import (
    create_transfer,
    create_deposit,
    create_withdrawal,
    InsufficientFundsError
)
from app.utils import calculate_account_balance

app = FastAPI(title="Financial Ledger API")

# Create tables
models.Base.metadata.create_all(bind=engine)

# ------------------ ACCOUNTS ------------------

@app.post("/accounts", response_model=schemas.AccountResponse)
def create_account(
    account: schemas.AccountCreate,
    db: Session = Depends(get_db)
):
    new_account = models.Account(
        user_name=account.user_name,
        account_type=account.account_type,
        currency=account.currency
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    # ✅ RETURN WITH BALANCE
    return {
        "id": new_account.id,
        "user_name": new_account.user_name,
        "account_type": new_account.account_type,
        "currency": new_account.currency,
        "status": new_account.status,
        "balance": calculate_account_balance(db, new_account.id)
    }


@app.get("/accounts/{account_id}", response_model=schemas.AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.get(models.Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "id": account.id,
        "user_name": account.user_name,
        "account_type": account.account_type,
        "currency": account.currency,
        "status": account.status,
        "balance": calculate_account_balance(db, account.id)
    }


# ------------------ LEDGER ------------------

@app.get(
    "/accounts/{account_id}/ledger",
    response_model=list[schemas.LedgerEntryResponse]
)
def get_ledger(account_id: int, db: Session = Depends(get_db)):
    account = db.get(models.Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return (
        db.query(models.LedgerEntry)
        .filter(models.LedgerEntry.account_id == account_id)
        .order_by(models.LedgerEntry.created_at)
        .all()
    )


# ------------------ TRANSACTIONS ------------------

@app.post("/transfers", response_model=schemas.TransactionResponse)
def transfer_funds(
    payload: schemas.TransferCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_transfer(
            db,
            payload.source_account_id,
            payload.destination_account_id,
            Decimal(payload.amount),
            payload.description
        )
    except InsufficientFundsError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Insufficient funds"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/deposits", response_model=schemas.TransactionResponse)
def deposit_funds(
    payload: schemas.DepositCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_deposit(
            db,
            payload.destination_account_id,
            Decimal(payload.amount),
            payload.description
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/withdrawals", response_model=schemas.TransactionResponse)
def withdraw_funds(
    payload: schemas.WithdrawalCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_withdrawal(
            db,
            payload.source_account_id,
            Decimal(payload.amount),
            payload.description
        )
    except InsufficientFundsError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Insufficient funds"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

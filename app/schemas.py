from pydantic import BaseModel, Field
from app.models import AccountType, AccountStatus
from decimal import Decimal
from typing import Optional, List
from datetime import datetime

from app.models import (
    AccountType,
    AccountStatus,
    TransactionType,
    TransactionStatus,
    LedgerEntryType
)


# ---------------- ACCOUNTS ---------------- #

class AccountCreate(BaseModel):
    user_name: str
    account_type: AccountType
    currency: str = "USD"

class AccountWithBalance(BaseModel):
    id: int
    user_name: str
    account_type: AccountType
    currency: str
    status: AccountStatus
    balance: Decimal

    class Config:
        orm_mode = True

class AccountResponse(BaseModel):
    id: int
    user_name: str
    account_type: AccountType
    currency: str
    status: AccountStatus
    balance: Decimal

    class Config:
        from_attributes = True


# ---------------- TRANSACTIONS ---------------- #

class TransferCreate(BaseModel):
    source_account_id: int
    destination_account_id: int
    amount: Decimal = Field(gt=0)
    description: Optional[str] = None


class DepositCreate(BaseModel):
    destination_account_id: int
    amount: Decimal = Field(gt=0)
    description: Optional[str] = None


class WithdrawalCreate(BaseModel):
    source_account_id: int
    amount: Decimal = Field(gt=0)
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    type: TransactionType
    amount: Decimal
    currency: str
    status: TransactionStatus
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------- LEDGER ---------------- #

class LedgerEntryResponse(BaseModel):
    id: int
    account_id: int
    transaction_id: int
    entry_type: LedgerEntryType
    amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

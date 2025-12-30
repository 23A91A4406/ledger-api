from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db import Base


# ---------------- ENUMS ---------------- #

class AccountStatus(str, enum.Enum):
    active = "active"
    frozen = "frozen"


class AccountType(str, enum.Enum):
    checking = "checking"
    savings = "savings"


class TransactionType(str, enum.Enum):
    transfer = "transfer"
    deposit = "deposit"
    withdrawal = "withdrawal"


class TransactionStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class LedgerEntryType(str, enum.Enum):
    debit = "debit"
    credit = "credit"


# ---------------- MODELS ---------------- #

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)

    account_type = Column(Enum(AccountType), nullable=False)
    currency = Column(String, default="USD")
    status = Column(Enum(AccountStatus), default=AccountStatus.active)

    created_at = Column(DateTime, default=datetime.utcnow)

    ledger_entries = relationship(
        "LedgerEntry",
        back_populates="account",
        cascade="all, delete-orphan"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(TransactionType), nullable=False)

    source_account_id = Column(
        Integer, ForeignKey("accounts.id"), nullable=True
    )
    destination_account_id = Column(
        Integer, ForeignKey("accounts.id"), nullable=True
    )

    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String, default="USD")

    status = Column(
        Enum(TransactionStatus),
        default=TransactionStatus.pending
    )

    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    ledger_entries = relationship(
        "LedgerEntry",
        back_populates="transaction"
    )


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)

    account_id = Column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=False
    )

    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id"),
        nullable=False
    )

    entry_type = Column(
        Enum(LedgerEntryType),
        nullable=False
    )
    amount = Column(Numeric(12, 2), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="ledger_entries")
    transaction = relationship("Transaction", back_populates="ledger_entries")

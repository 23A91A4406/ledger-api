from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
from app.db import Base
import enum

# --------------------------
# Account Model
# --------------------------
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    balance = Column(Numeric(precision=18, scale=2), default=0)
    currency = Column(String, default="USD")

    ledger_entries = relationship("LedgerEntry", back_populates="account")


# --------------------------
# Transaction Types and Status
# --------------------------
class TransactionType(str, enum.Enum):
    transfer = "transfer"
    deposit = "deposit"
    withdrawal = "withdrawal"

class TransactionStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


# --------------------------
# Transaction Model
# --------------------------
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(TransactionType), nullable=False)
    source_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    destination_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    currency = Column(String, default="USD")
    status = Column(Enum(TransactionStatus), default=TransactionStatus.pending)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source_account = relationship("Account", foreign_keys=[source_account_id])
    destination_account = relationship("Account", foreign_keys=[destination_account_id])
    ledger_entries = relationship("LedgerEntry", back_populates="transaction")


# --------------------------
# Ledger Entry Types
# --------------------------
class EntryType(str, enum.Enum):
    debit = "debit"
    credit = "credit"


# --------------------------
# LedgerEntry Model
# --------------------------
class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    entry_type = Column(Enum(EntryType), nullable=False)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="ledger_entries")
    transaction = relationship("Transaction", back_populates="ledger_entries")

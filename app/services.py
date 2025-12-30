from sqlalchemy.orm import Session
from decimal import Decimal

from app.models import (
    Account,
    Transaction,
    LedgerEntry,
    TransactionType,
    TransactionStatus,
    LedgerEntryType
)
from app.utils import calculate_account_balance


class InsufficientFundsError(Exception):
    pass


def create_transfer(
    db: Session,
    source_account_id: int,
    destination_account_id: int,
    amount: Decimal,
    description: str | None = None
):
    """Executes an atomic transfer using double-entry bookkeeping."""
    with db.begin():
        source = db.get(Account, source_account_id)
        destination = db.get(Account, destination_account_id)

        if not source or not destination:
            raise ValueError("Invalid account ID")

        source_balance = calculate_account_balance(db, source.id)
        if source_balance < amount:
            raise InsufficientFundsError("Insufficient funds")

        txn = Transaction(
            type=TransactionType.transfer,
            source_account_id=source.id,
            destination_account_id=destination.id,
            amount=amount,
            status=TransactionStatus.pending,
            description=description
        )
        db.add(txn)
        db.flush()

        db.add(
            LedgerEntry(
                account_id=source.id,
                transaction_id=txn.id,
                entry_type=LedgerEntryType.debit,
                amount=amount
            )
        )
        db.add(
            LedgerEntry(
                account_id=destination.id,
                transaction_id=txn.id,
                entry_type=LedgerEntryType.credit,
                amount=amount
            )
        )

        txn.status = TransactionStatus.completed

    return txn


def create_deposit(
    db: Session,
    destination_account_id: int,
    amount: Decimal,
    description: str | None = None
):
    with db.begin():
        account = db.get(Account, destination_account_id)
        if not account:
            raise ValueError("Invalid account ID")

        txn = Transaction(
            type=TransactionType.deposit,
            destination_account_id=account.id,
            amount=amount,
            status=TransactionStatus.pending,
            description=description
        )
        db.add(txn)
        db.flush()

        db.add(
            LedgerEntry(
                account_id=account.id,
                transaction_id=txn.id,
                entry_type=LedgerEntryType.credit,
                amount=amount
            )
        )

        txn.status = TransactionStatus.completed

    return txn


def create_withdrawal(
    db: Session,
    source_account_id: int,
    amount: Decimal,
    description: str | None = None
):
    with db.begin():
        account = db.get(Account, source_account_id)
        if not account:
            raise ValueError("Invalid account ID")

        balance = calculate_account_balance(db, account.id)
        if balance < amount:
            raise InsufficientFundsError("Insufficient funds")

        txn = Transaction(
            type=TransactionType.withdrawal,
            source_account_id=account.id,
            amount=amount,
            status=TransactionStatus.pending,
            description=description
        )
        db.add(txn)
        db.flush()

        db.add(
            LedgerEntry(
                account_id=account.id,
                transaction_id=txn.id,
                entry_type=LedgerEntryType.debit,
                amount=amount
            )
        )

        txn.status = TransactionStatus.completed

    return txn

from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.models import LedgerEntry, LedgerEntryType


def calculate_account_balance(
    db: Session,
    account_id: int
) -> Decimal:
    """
    Calculate current balance for an account by summing ledger entries.
    Credits add money, debits subtract money.
    """

    credit_sum = (
        db.query(func.coalesce(func.sum(LedgerEntry.amount), 0))
        .filter(
            LedgerEntry.account_id == account_id,
            LedgerEntry.entry_type == LedgerEntryType.credit
        )
        .scalar()
    )

    debit_sum = (
        db.query(func.coalesce(func.sum(LedgerEntry.amount), 0))
        .filter(
            LedgerEntry.account_id == account_id,
            LedgerEntry.entry_type == LedgerEntryType.debit
        )
        .scalar()
    )

    return Decimal(credit_sum) - Decimal(debit_sum)

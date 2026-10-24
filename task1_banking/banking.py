"""Task 1: OOP banking and ledger engine. Educational in-memory implementation."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from threading import RLock
from typing import Dict, List


def money(value) -> Decimal:
    """Convert values to Decimal safely; callers should preferably pass strings."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Amount must be a valid number") from exc
    if not amount.is_finite():
        raise ValueError("Amount must be finite")
    return amount.quantize(Decimal("0.01"))


@dataclass(frozen=True)
class LedgerEntry:
    account_id: str
    kind: str
    amount: Decimal
    currency: str
    balance_after: Decimal
    note: str = ""


class Ledger:
    """Append-only in-memory transaction log."""
    def __init__(self):
        self._entries: List[LedgerEntry] = []
        self._lock = RLock()

    def record(self, entry: LedgerEntry) -> None:
        with self._lock:
            self._entries.append(entry)

    def entries(self, account_id: str | None = None) -> tuple[LedgerEntry, ...]:
        with self._lock:
            rows = self._entries[:]
        if account_id is not None:
            rows = [row for row in rows if row.account_id == account_id]
        return tuple(rows)


class Account(ABC):
    """Abstract account. Name-mangled fields discourage direct external access."""
    def __init__(self, account_id: str, owner: str, currency: str, opening_balance=0, ledger=None):
        if not account_id.strip():
            raise ValueError("account_id cannot be empty")
        if not owner.strip():
            raise ValueError("owner cannot be empty")
        currency = currency.upper().strip()
        if len(currency) != 3 or not currency.isalpha():
            raise ValueError("currency must be a 3-letter code, e.g. KES or USD")
        opening = money(opening_balance)
        if opening < 0:
            raise ValueError("Opening balance cannot be negative")
        self.__account_id = account_id
        self.__owner = owner
        self.__currency = currency
        self.__balance = opening
        self.__ledger = ledger if ledger is not None else Ledger()
        self.__lock = RLock()
        if opening:
            self.__record("opening_deposit", opening, "Opening balance")

    @property
    def account_id(self): return self.__account_id
    @property
    def owner(self): return self.__owner
    @property
    def currency(self): return self.__currency
    @property
    def balance(self):
        with self.__lock:
            return self.__balance
    @property
    def ledger(self): return self.__ledger

    def __record(self, kind, amount, note=""):
        self.__ledger.record(LedgerEntry(self.__account_id, kind, amount, self.__currency, self.__balance, note))

    def deposit(self, amount):
        amount = money(amount)
        if amount <= 0:
            raise ValueError("Deposit must be greater than zero")
        with self.__lock:
            self.__balance += amount
            self.__record("deposit", amount)
            return self.__balance

    def withdraw(self, amount):
        amount = money(amount)
        if amount <= 0:
            raise ValueError("Withdrawal must be greater than zero")
        with self.__lock:
            if amount > self.__balance:
                raise ValueError("Insufficient funds")
            self.__balance -= amount
            self.__record("withdrawal", amount)
            return self.__balance

    def transfer_to(self, other: "Account", amount):
        """Transfer only between accounts using the same currency."""
        if not isinstance(other, Account):
            raise TypeError("Destination must be an Account")
        if other is self:
            raise ValueError("Cannot transfer to the same account")
        if self.currency != other.currency:
            raise ValueError("Cross-currency transfers require an explicit FX service")
        amount = money(amount)
        if amount <= 0:
            raise ValueError("Transfer must be greater than zero")
        # Stable lock ordering avoids deadlock when transfers run concurrently.
        first, second = sorted((self, other), key=lambda account: account.account_id)
        with first._Account__lock:
            with second._Account__lock:
                if amount > self.__balance:
                    raise ValueError("Insufficient funds")
                self.__balance -= amount
                other._Account__balance += amount
                self.__record("transfer_out", amount, f"to {other.account_id}")
                other._Account__record("transfer_in", amount, f"from {self.account_id}")
        return self.balance, other.balance

    @abstractmethod
    def accrue_interest(self) -> Decimal:
        """Calculate and credit interest according to the account type."""

    @abstractmethod
    def deduct_fees(self) -> Decimal:
        """Deduct account-specific fees and return the fee charged."""

    def _credit_adjustment(self, amount, kind, note=""):
        amount = money(amount)
        if amount < 0:
            raise ValueError("Adjustment cannot be negative")
        with self.__lock:
            self.__balance += amount
            if amount:
                self.__record(kind, amount, note)
        return amount

    def _debit_adjustment(self, amount, kind, note=""):
        amount = money(amount)
        if amount < 0:
            raise ValueError("Adjustment cannot be negative")
        with self.__lock:
            if amount > self.__balance:
                raise ValueError("Insufficient funds to cover fee")
            self.__balance -= amount
            if amount:
                self.__record(kind, amount, note)
        return amount


class SavingsAccount(Account):
    def __init__(self, *args, annual_interest_rate="0.03", monthly_fee="0", **kwargs):
        self._annual_interest_rate = Decimal(str(annual_interest_rate))
        self._monthly_fee = money(monthly_fee)
        if not (Decimal("0") <= self._annual_interest_rate <= Decimal("1")):
            raise ValueError("Interest rate must be between 0 and 1")
        if self._monthly_fee < 0: raise ValueError("Fee cannot be negative")
        super().__init__(*args, **kwargs)

    def accrue_interest(self):
        interest = money(self.balance * self._annual_interest_rate / Decimal("12"))
        return self._credit_adjustment(interest, "interest", "Savings monthly interest")

    def deduct_fees(self):
        return self._debit_adjustment(self._monthly_fee, "fee", "Savings monthly fee")


class CheckingAccount(Account):
    def __init__(self, *args, transaction_fee="10.00", free_transactions=5, **kwargs):
        self._transaction_fee = money(transaction_fee)
        if self._transaction_fee < 0: raise ValueError("Fee cannot be negative")
        if not isinstance(free_transactions, int) or free_transactions < 0:
            raise ValueError("free_transactions must be a non-negative integer")
        self._free_transactions = free_transactions
        self._monthly_transaction_count = 0
        super().__init__(*args, **kwargs)

    def deposit(self, amount):
        result = super().deposit(amount)
        self._monthly_transaction_count += 1
        return result

    def withdraw(self, amount):
        result = super().withdraw(amount)
        self._monthly_transaction_count += 1
        return result

    def accrue_interest(self):
        return self._credit_adjustment(Decimal("0"), "interest", "Checking account has no interest")

    def deduct_fees(self):
        chargeable = max(0, self._monthly_transaction_count - self._free_transactions)
        fee = money(self._transaction_fee * chargeable)
        charged = self._debit_adjustment(fee, "fee", "Checking transaction fees")
        self._monthly_transaction_count = 0
        return charged


class HighYieldAccount(SavingsAccount):
    def __init__(self, *args, annual_interest_rate="0.06", minimum_balance="1000", monthly_fee="0", **kwargs):
        self._minimum_balance = money(minimum_balance)
        if self._minimum_balance < 0: raise ValueError("Minimum balance cannot be negative")
        super().__init__(*args, annual_interest_rate=annual_interest_rate, monthly_fee=monthly_fee, **kwargs)

    def accrue_interest(self):
        if self.balance < self._minimum_balance:
            return self._credit_adjustment(Decimal("0"), "interest", "Below high-yield minimum balance")
        interest = money(self.balance * self._annual_interest_rate / Decimal("12"))
        return self._credit_adjustment(interest, "interest", "High-yield monthly interest")


class TransactionProcessor:
    """Polymorphic dispatch: callers use the Account interface, not concrete types."""
    @staticmethod
    def process_month_end(accounts):
        results = []
        for account in accounts:
            interest = account.accrue_interest()
            fee = account.deduct_fees()
            results.append({"account_id": account.account_id, "interest": interest, "fee": fee,
                            "balance": account.balance, "currency": account.currency})
        return results

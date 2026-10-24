import unittest
from decimal import Decimal
from .banking import Account, Ledger, SavingsAccount, CheckingAccount, HighYieldAccount, TransactionProcessor

class BankingTests(unittest.TestCase):
    def test_account_is_abstract(self):
        with self.assertRaises(TypeError):
            Account("x", "owner", "KES")

    def test_deposit_withdraw_and_ledger(self):
        ledger = Ledger()
        account = SavingsAccount("a", "Owner", "KES", "100", ledger=ledger)
        account.deposit("10.25")
        account.withdraw("5")
        self.assertEqual(account.balance, Decimal("105.25"))
        self.assertEqual(len(ledger.entries("a")), 3)

    def test_invalid_amount_and_overdraft(self):
        account = SavingsAccount("a", "Owner", "KES", "10")
        for bad in ("0", "-1"):
            with self.assertRaises(ValueError): account.deposit(bad)
        with self.assertRaises(ValueError): account.withdraw("11")

    def test_cross_currency_transfer_rejected(self):
        a = SavingsAccount("a", "A", "KES", "100")
        b = SavingsAccount("b", "B", "USD", "10")
        with self.assertRaises(ValueError): a.transfer_to(b, "10")

    def test_transfer_updates_both_accounts(self):
        a = SavingsAccount("a", "A", "KES", "100")
        b = SavingsAccount("b", "B", "KES", "0")
        a.transfer_to(b, "25")
        self.assertEqual(a.balance, Decimal("75.00"))
        self.assertEqual(b.balance, Decimal("25.00"))

    def test_polymorphic_month_end(self):
        savings = SavingsAccount("s", "S", "KES", "12000", annual_interest_rate="0.12")
        checking = CheckingAccount("c", "C", "KES", "1000", transaction_fee="5", free_transactions=0)
        checking.deposit("10")
        result = TransactionProcessor.process_month_end([savings, checking])
        self.assertEqual(result[0]["interest"], Decimal("120.00"))
        self.assertEqual(result[1]["fee"], Decimal("5.00"))

    def test_high_yield_minimum(self):
        account = HighYieldAccount("h", "H", "KES", "500", minimum_balance="1000")
        self.assertEqual(account.accrue_interest(), Decimal("0.00"))

if __name__ == "__main__": unittest.main()

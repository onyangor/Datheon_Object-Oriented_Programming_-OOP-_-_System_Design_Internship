from banking import Ledger, SavingsAccount, CheckingAccount, HighYieldAccount, TransactionProcessor

ledger = Ledger()
accounts = [
    SavingsAccount("S-001", "Amina", "KES", "50000", ledger=ledger),
    CheckingAccount("C-001", "Brian", "KES", "12000", ledger=ledger),
    HighYieldAccount("H-001", "Chao", "KES", "100000", ledger=ledger),
]
accounts[0].deposit("2500")
accounts[1].withdraw("500")
for result in TransactionProcessor.process_month_end(accounts):
    print(result)
print(f"Ledger rows: {len(ledger.entries())}")

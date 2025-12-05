import pandas as pd
import uuid
import random
from faker import Faker

fake = Faker()

def generate_transactions(account_ids, num_transactions_per_account=10):
    """Generates a DataFrame of synthetic transactions linked to accounts."""
    if not account_ids:
        raise ValueError("Account IDs list cannot be empty")

    transactions = []
    for account_id in account_ids:
        # Randomize number of transactions
        num_tx = random.randint(0, num_transactions_per_account + 5)
        
        for _ in range(num_tx):
            tx_type = fake.random_element(elements=("Deposit", "Withdrawal", "Transfer", "Payment", "Fee"))
            
            # Logic for amount based on type
            if tx_type in ["Deposit", "Transfer"]:
                 amount = round(random.uniform(10.0, 5000.0), 2)
            elif tx_type == "Fee":
                 amount = round(random.uniform(1.0, 50.0), 2)
                 amount = -amount # Deduct
            else:
                 amount = round(random.uniform(5.0, 1000.0), 2)
                 amount = -amount # Deduct

            transaction = {
                "transaction_id": str(uuid.uuid4()),
                "account_id": account_id,
                "transaction_type": tx_type,
                "amount": amount,
                "timestamp": fake.date_time_between(start_date="-1y", end_date="now"),
                "description": fake.sentence(nb_words=3),
                "merchant_name": fake.company() if tx_type in ["Payment", "Withdrawal"] else None
            }
            transactions.append(transaction)
            
    return pd.DataFrame(transactions)

if __name__ == "__main__":
    # Test with dummy IDs
    dummy_ids = [str(uuid.uuid4()) for _ in range(3)]
    df = generate_transactions(dummy_ids)
    print(df.head())

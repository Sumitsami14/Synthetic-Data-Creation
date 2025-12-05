import pandas as pd
import uuid
import random
from faker import Faker

fake = Faker()

def generate_accounts(customer_ids, num_accounts_per_customer=1):
    """Generates a DataFrame of synthetic accounts linked to customers."""
    if not customer_ids:
        raise ValueError("Customer IDs list cannot be empty")
        
    accounts = []
    for customer_id in customer_ids:
        # Randomize number of accounts per customer slightly
        num_accounts = random.randint(1, num_accounts_per_customer + 1)
        
        for _ in range(num_accounts):
            account = {
                "account_id": str(uuid.uuid4()),
                "customer_id": customer_id,
                "account_type": fake.random_element(elements=("Savings", "Checking", "Business")),
                "current_balance": round(random.uniform(100.0, 50000.0), 2),
                "open_date": fake.date_between(start_date="-5y", end_date="today"),
                "status": fake.random_element(elements=("Active", "Dormant", "Closed"))
            }
            accounts.append(account)
    return pd.DataFrame(accounts)

if __name__ == "__main__":
    # Test with dummy IDs
    dummy_ids = [str(uuid.uuid4()) for _ in range(3)]
    df = generate_accounts(dummy_ids)
    print(df.head())

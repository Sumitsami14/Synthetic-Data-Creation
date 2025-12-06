
import os
import shutil
import uuid
import pandas as pd
from generators.customer import generate_customers
from generators.account import generate_accounts
from generators.transaction import generate_transactions
from utils.exporters import export_to_csv, export_to_json

def test_account_generation():
    print("Testing Account Generation Flow...")
    count = 5
    job_id = "test_fix_" + str(uuid.uuid4())
    output_dir = os.path.join('data', 'exports', job_id)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Replicating logic from agent.py
        customers_df = generate_customers(count)
        accounts_df = generate_accounts(customers_df['customer_id'].tolist())
        
        if len(accounts_df) > count:
            accounts_df = accounts_df.head(count)
            
        transactions_df = generate_transactions(accounts_df['account_id'].tolist())
        
        print(f"Generated {len(customers_df)} customers")
        print(f"Generated {len(accounts_df)} accounts")
        print(f"Generated {len(transactions_df)} transactions")
        
        # Test Export
        export_to_json(customers_df, 'customers.json', output_dir=output_dir)
        print("Export successful")
        
        # Cleanup
        shutil.rmtree(output_dir)
        print("Test Passed!")
        
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_account_generation()

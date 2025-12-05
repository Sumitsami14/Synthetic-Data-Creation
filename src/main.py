import argparse
from generators.customer import generate_customers
from generators.account import generate_accounts
from generators.transaction import generate_transactions
from utils.exporters import export_to_csv, export_to_json
from utils.logger import logger

def main():
    parser = argparse.ArgumentParser(description="Synthetic Banking Data Generator")
    parser.add_argument("--customers", type=int, default=10, help="Number of customers to generate")
    parser.add_argument("--format", type=str, choices=["csv", "json"], default="csv", help="Output format (csv or json)")
    args = parser.parse_args()

    logger.info(f"Starting data generation for {args.customers} customers...")
    
    try:
        # 1. Generate Customers
        logger.info("Generating customers...")
        customers_df = generate_customers(args.customers)
        logger.info(f"Generated {len(customers_df)} customers.")

        # 2. Generate Accounts (linked to customers)
        logger.info("Generating accounts...")
        customer_ids = customers_df["customer_id"].tolist()
        accounts_df = generate_accounts(customer_ids)
        logger.info(f"Generated {len(accounts_df)} accounts.")

        # 3. Generate Transactions (linked to accounts)
        logger.info("Generating transactions...")
        account_ids = accounts_df["account_id"].tolist()
        transactions_df = generate_transactions(account_ids)
        logger.info(f"Generated {len(transactions_df)} transactions.")

        # 4. Export Data
        logger.info(f"Exporting data to {args.format.upper()} format...")
        ext = args.format
        if ext == "csv":
            export_to_csv(customers_df, "customers.csv")
            export_to_csv(accounts_df, "accounts.csv")
            export_to_csv(transactions_df, "transactions.csv")
        elif ext == "json":
            export_to_json(customers_df, "customers.json")
            export_to_json(accounts_df, "accounts.json")
            export_to_json(transactions_df, "transactions.json")
            
        logger.info("Data generation complete successfully!")
        
    except Exception as e:
        logger.error(f"Data generation failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()

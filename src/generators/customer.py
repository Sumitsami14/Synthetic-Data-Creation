from faker import Faker
import pandas as pd
import uuid

fake = Faker()

def generate_customers(num_customers):
    """Generates a DataFrame of synthetic customers."""
    if num_customers <= 0:
        raise ValueError("Number of customers must be greater than 0")

    customers = []
    for _ in range(num_customers):
        customer = {
            "customer_id": str(uuid.uuid4()),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "phone_number": fake.phone_number(),
            "address": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "zip_code": fake.zipcode(),
            "kyc_status": fake.random_element(elements=("Verified", "Pending", "Failed"))
        }
        customers.append(customer)
    return pd.DataFrame(customers)

if __name__ == "__main__":
    df = generate_customers(5)
    print(df.head())

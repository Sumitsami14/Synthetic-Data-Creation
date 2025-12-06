from flask import Blueprint, request, jsonify, url_for
from services.nlp_engine import NLPEngine
from models import db
from datetime import datetime
import threading
import uuid
import os
import pandas as pd
# Import your generator functions
from generators.customer import generate_customers
from generators.account import generate_accounts
from generators.transaction import generate_transactions
from utils.exporters import export_to_csv, export_to_json
from utils.logger import logger

agent_bp = Blueprint('agent', __name__)

def run_generation_job(job_id, command):
    """
    Background task to run generation based on NLP command.
    """
    try:
        count = command['count']
        data_type = command['type']
        fmt = command['format']
        
        # Define output directory
        output_dir = os.path.join('data', 'exports', job_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate Data based on type
        # Note: Ideally we should generate linked data, but for simple commands we might generating isolated datasets
        # or defaults. For now, let's trigger the full flow if possible, or just specific parts.
        # To keep it simple and consistent with current app logic, we'll generate the full set 
        # but scale the primary requested entity.
        
        if data_type == 'customer':
            customers_df = generate_customers(count)
            accounts_df = generate_accounts(customers_df['customer_id'].tolist())
            transactions_df = generate_transactions(accounts_df['account_id'].tolist())
        elif data_type == 'account':
            # Generate enough customers to ensure we have enough accounts
            # each customer gets 1-2 accounts, so generating 'count' customers is safe surplus
            customers_df = generate_customers(count) 
            accounts_df = generate_accounts(customers_df['customer_id'].tolist())
            
            # Slice to requested count
            if len(accounts_df) > count:
                accounts_df = accounts_df.head(count)
                
            transactions_df = generate_transactions(accounts_df['account_id'].tolist())
        else:
             # Default full flow
            customers_df = generate_customers(count)
            accounts_df = generate_accounts(customers_df['customer_id'].tolist())
            transactions_df = generate_transactions(accounts_df['account_id'].tolist())

        # Export
        if fmt == 'csv':
            export_to_csv(customers_df, 'customers.csv', output_dir=output_dir)
            export_to_csv(accounts_df, 'accounts.csv', output_dir=output_dir)
            export_to_csv(transactions_df, 'transactions.csv', output_dir=output_dir)
        else:
            export_to_json(customers_df, 'customers.json', output_dir=output_dir)
            export_to_json(accounts_df, 'accounts.json', output_dir=output_dir)
            export_to_json(transactions_df, 'transactions.json', output_dir=output_dir)

        # Zip it
        import shutil
        shutil.make_archive(output_dir, 'zip', output_dir)
        
        # Log success (In a real app, update DB status)
        logger.info(f"Agent Job {job_id} completed successfully.")

    except Exception as e:
        logger.error(f"Agent Job {job_id} failed: {e}")

@agent_bp.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint to receive natural language commands.
    """
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
        
    # Process Intent
    result = NLPEngine.process_request(message)
    command = result['command']
    
    # Trigger Job
    job_id = str(uuid.uuid4())
    
    # Run in background
    thread = threading.Thread(target=run_generation_job, args=(job_id, command))
    thread.start()
    
    return jsonify({
        "response": result['message'],
        "job_id": job_id,
        "command": command
    })

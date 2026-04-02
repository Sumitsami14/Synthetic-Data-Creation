from flask import Blueprint, request, jsonify, send_file, current_app
from models import db, RequestLog
from generators.customer import generate_customers
from generators.account import generate_accounts
from generators.transaction import generate_transactions
from utils.exporters import export_to_csv, export_to_json
from utils.logger import logger
import uuid
import os
import shutil
import threading

api_bp = Blueprint('api', __name__)

def run_generation_task(app, request_id, customers_count, fmt):
    with app.app_context():
        req = RequestLog.query.get(request_id)
        req.status = "Processing"
        db.session.commit()
        
        try:
            job_id = str(uuid.uuid4())
            output_dir = os.path.join("data", "exports", job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"Starting generation job {job_id} for {customers_count} customers.")

            # Generation
            customers_df = generate_customers(customers_count)
            customer_ids = customers_df["customer_id"].tolist()
            accounts_df = generate_accounts(customer_ids)
            account_ids = accounts_df["account_id"].tolist()
            transactions_df = generate_transactions(account_ids)
            
            # Save the transaction count to the request log
            req.transactions_count = len(transactions_df)
            db.session.commit()

            # Export
            if fmt == "csv":
                export_to_csv(customers_df, "customers.csv", output_dir)
                export_to_csv(accounts_df, "accounts.csv", output_dir)
                export_to_csv(transactions_df, "transactions.csv", output_dir)
            else:
                export_to_json(customers_df, "customers.json", output_dir)
                export_to_json(accounts_df, "accounts.json", output_dir)
                export_to_json(transactions_df, "transactions.json", output_dir)
                
            # Zip
            shutil.make_archive(output_dir, 'zip', output_dir)
            zip_path = f"{output_dir}.zip"
            
            req.status = "Completed"
            req.file_path = zip_path
            db.session.commit()
            logger.info(f"Job {job_id} completed. File: {zip_path}")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            req.status = "Failed"
            db.session.commit()

@api_bp.route('/generate', methods=['POST'])
def generate():
    data = request.json
    customers = data.get('customers', 10)
    fmt = data.get('format', 'csv')
    
    # Create DB Entry
    new_req = RequestLog(customers_count=customers, status="Queued")
    db.session.add(new_req)
    db.session.commit()
    
    # Run in background thread (simple async for Flask)
    thread = threading.Thread(target=run_generation_task, args=(current_app._get_current_object(), new_req.id, customers, fmt))
    thread.start()
    
    return jsonify({"message": "Generation started", "job_id": new_req.id}), 202

@api_bp.route('/history', methods=['GET'])
def history():
    logs = RequestLog.query.order_by(RequestLog.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs])

@api_bp.route('/download/<int:job_id>', methods=['GET'])
def download(job_id):
    req = RequestLog.query.get(job_id)
    if not req or not req.file_path:
        return jsonify({"error": "File not found"}), 404
    
    # Need absolute path for send_file
    abs_path = os.path.abspath(req.file_path)
    return send_file(abs_path, as_attachment=True, download_name=f"synthetic_data_{job_id}.zip")

@api_bp.route('/stats', methods=['GET'])
def stats():
    """
    Return summary statistics for the dashboard.
    """
    total_requests = RequestLog.query.count()
    completed_requests = RequestLog.query.filter_by(status='Completed').count()
    failed_requests = RequestLog.query.filter_by(status='Failed').count()
    
    # Calculate total records generated (approximate based on logs)
    # real implementation would store this in DB properly
    total_customers = db.session.query(db.func.sum(RequestLog.customers_count)).scalar() or 0
    total_transactions = db.session.query(db.func.sum(RequestLog.transactions_count)).scalar() or 0
    
    return jsonify({
        "total_requests": total_requests,
        "completed_requests": completed_requests,
        "failed_requests": failed_requests,
        "total_customers_generated": total_customers,
        "total_transactions_generated": total_transactions
    })

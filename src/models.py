from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class RequestLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    customers_count = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    file_path = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'customers_count': self.customers_count,
            'status': self.status,
            'file_path': self.file_path
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

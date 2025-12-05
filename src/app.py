from flask import Flask, render_template
from models import init_db
from routes.main import api_bp
from routes.agent import agent_bp
import os

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///requests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
init_db(app)

# Register Blueprints
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(agent_bp, url_prefix='/api/agent')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

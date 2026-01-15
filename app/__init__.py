from flask import Flask
from app.db import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    init_db()
    
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app

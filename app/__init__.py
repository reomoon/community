from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # models에서 db를 import하여 초기화
    from app.models import db
    db.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
        
        # 스케줄러 시작
        from app.scheduler import get_scheduler
        scheduler = get_scheduler()
        scheduler.start_scheduler()
    
    return app
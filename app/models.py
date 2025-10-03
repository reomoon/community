from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    site = db.Column(db.String(50), nullable=False)  # bobae, ppomppu, fmkorea, dcinside
    category = db.Column(db.String(50), nullable=False)  # economy, humor, entertainment, other
    author = db.Column(db.String(100))
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    crawled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Post {self.title}>'

class SiteVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visit_date = db.Column(db.Date, default=lambda: datetime.utcnow().date())
    visit_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SiteVisit {self.visit_date}: {self.visit_count}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'site': self.site,
            'category': self.category,
            'author': self.author,
            'views': self.views,
            'likes': self.likes,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'crawled_at': self.crawled_at.isoformat() if self.crawled_at else None
        }
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///community_aggregator.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 크롤링 설정
    CRAWL_INTERVAL_HOURS = 1  # 1시간마다 크롤링
    MAX_POSTS_PER_SITE = 20   # 사이트당 최대 게시물 수
    
    # 카테고리 설정
    CATEGORIES = {
        'economy': '경제/금융',
        'humor': '유머',
        'entertainment': '연예/스포츠',
        'tech': '기술/IT',
        'other': '기타'
    }
    
    # 지원 사이트
    SUPPORTED_SITES = {
        'bobae': {
            'name': '보배드림',
            'url': 'https://www.bobae.co.kr',
            'enabled': True
        },
        'ppomppu': {
            'name': '뽐뿌',
            'url': 'https://www.ppomppu.co.kr',
            'enabled': True
        },
        'fmkorea': {
            'name': '에펨코리아',
            'url': 'https://www.fmkorea.com',
            'enabled': True
        },
        'dcinside': {
            'name': '디시인사이드',
            'url': 'https://www.dcinside.com',
            'enabled': True
        }
    }
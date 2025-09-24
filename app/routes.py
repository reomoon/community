from flask import Blueprint, render_template, jsonify, request
from app.models import Post, db
from app.crawlers.crawler_manager import CrawlerManager
from config import Config

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """메인 페이지"""
    categories = Config.CATEGORIES
    sites = Config.SUPPORTED_SITES
    return render_template('index.html', categories=categories, sites=sites)

@main.route('/api/posts')
def get_posts():
    """게시물 API"""
    category = request.args.get('category', 'all')
    site = request.args.get('site', 'all')
    limit = request.args.get('limit', 50, type=int)
    
    query = Post.query
    
    if category != 'all':
        query = query.filter(Post.category == category)
    
    if site != 'all':
        query = query.filter(Post.site == site)
    
    posts = query.order_by(Post.crawled_at.desc()).limit(limit).all()
    
    return jsonify({
        'posts': [post.to_dict() for post in posts],
        'total': len(posts)
    })

@main.route('/api/crawl')
def manual_crawl():
    """수동 크롤링 실행"""
    try:
        crawler_manager = CrawlerManager()
        result = crawler_manager.crawl_all_sites()
        return jsonify({
            'success': True,
            'message': f'{result} 개의 게시물을 수집했습니다.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'크롤링 중 오류가 발생했습니다: {str(e)}'
        }), 500

@main.route('/api/stats')
def get_stats():
    """통계 정보"""
    total_posts = Post.query.count()
    
    stats_by_category = {}
    for category_key in Config.CATEGORIES:
        count = Post.query.filter(Post.category == category_key).count()
        stats_by_category[category_key] = count
    
    stats_by_site = {}
    for site_key in Config.SUPPORTED_SITES:
        count = Post.query.filter(Post.site == site_key).count()
        stats_by_site[site_key] = count
    
    return jsonify({
        'total_posts': total_posts,
        'by_category': stats_by_category,
        'by_site': stats_by_site
    })
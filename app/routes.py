from flask import Blueprint, render_template, jsonify, request
from app.models import Post, SiteVisit, db
from app.crawlers.crawler_manager import CrawlerManager
from config import Config
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """메인 페이지"""
    # 방문자 수 증가
    today = datetime.utcnow().date()
    visit = SiteVisit.query.filter_by(visit_date=today).first()
    if visit:
        visit.visit_count += 1
    else:
        visit = SiteVisit(visit_date=today, visit_count=1)
        db.session.add(visit)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    # 통계 계산
    total_visitors = db.session.query(db.func.sum(SiteVisit.visit_count)).scalar() or 0
    today_visitors = visit.visit_count if visit else 0
    
    categories = Config.CATEGORIES
    sites = Config.SUPPORTED_SITES
    
    return render_template('index.html', 
                         categories=categories, 
                         sites=sites,
                         total_visitors=total_visitors,
                         today_visitors=today_visitors,
                         last_updated=datetime.now().strftime('%Y-%m-%d %H:%M'))

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

@main.route('/generate-static')
def generate_static():
    """GitHub Pages용 정적 HTML 생성"""
    import os
    
    try:
        # 최신 게시물 가져오기
        posts = Post.query.order_by(Post.crawled_at.desc()).limit(50).all()
        
        # 사이트별 통계
        site_stats = {}
        for site_key in Config.SUPPORTED_SITES:
            count = Post.query.filter(Post.site == site_key).count()
            site_stats[site_key] = count
        
        # 방문자 통계
        total_visitors = db.session.query(db.func.sum(SiteVisit.visit_count)).scalar() or 0
        today = datetime.utcnow().date()
        today_visit = SiteVisit.query.filter_by(visit_date=today).first()
        today_visitors = today_visit.visit_count if today_visit else 0
        
        # 정적 HTML 생성
        html_content = generate_static_html(posts, site_stats, total_visitors, today_visitors)
        
        # 루트 디렉토리에 index.html 저장
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        static_file_path = os.path.join(root_path, 'index.html')
        
        with open(static_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return jsonify({
            'success': True,
            'message': f'정적 HTML 생성 완료: {len(posts)}개 게시물',
            'file_path': static_file_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'정적 HTML 생성 오류: {str(e)}'
        }), 500

def generate_static_html(posts, site_stats, total_visitors=0, today_visitors=0):
    """정적 HTML 생성 함수"""
    site_names = {
        'bobae': '보배',
        'dcinside': '디시',
        'ppomppu': '뽐뿌', 
        'fmkorea': '에펨'
    }
    
    posts_html = ""
    for post in posts:
        posts_html += f"""
        <div class="post-card">
            <div class="post-title">
                <span class="site-badge {post.site}">{site_names.get(post.site, post.site)}</span>
                <a href="{post.url}" target="_blank" rel="noopener noreferrer">
                    {post.title}
                </a>
            </div>
            <div class="post-meta">
                <span class="post-author">👤 {post.author or '익명'}</span>
                <div class="post-stats">
                    {f'<span>👀 {post.views:,}</span>' if post.views else ''}
                    {f'<span>❤️ {post.likes:,}</span>' if post.likes else ''}
                    {f'<span>💬 {post.comments:,}</span>' if post.comments else ''}
                </div>
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>한국 커뮤니티 핫이슈</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        /* 스타일 복사 */
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }}
        .post-card {{ background: white; border-radius: 10px; padding: 1rem; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .site-badge {{ padding: 4px 8px; border-radius: 4px; color: white; font-size: 0.9em; }}
        .bobae {{ background: #e74c3c; }}
        .dcinside {{ background: #9b59b6; }}
        .ppomppu {{ background: #3498db; }}
        .fmkorea {{ background: #f39c12; }}
        .post-title a {{ text-decoration: none; color: #333; font-weight: bold; }}
        .post-title a:hover {{ color: #667eea; }}
        .post-meta {{ display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; font-size: 0.9em; color: #666; }}
        .post-stats span {{ margin-right: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1><i class="fas fa-fire"></i> 커뮤니티 핫이슈</h1>
            <p>실시간 업데이트 - 총 {len(posts)}개의 인기 게시물</p>
        </header>
        
        <div class="posts-container">
            {posts_html}
        </div>
        
        <footer style="text-align: center; margin-top: 2rem; color: #666;">
            <p>마지막 업데이트: {posts[0].crawled_at.strftime('%Y-%m-%d %H:%M') if posts else 'N/A'}</p>
            <p><a href="https://github.com/reomoon/community" target="_blank">GitHub</a> | 
               <a href="https://commu.vercel.app" target="_blank">실시간 버전</a></p>
        </footer>
    </div>
</body>
</html>"""
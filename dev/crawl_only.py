#!/usr/bin/env python3
"""
GitHub Actions용 크롤링 전용 스크립트
"""

import json
import os
import sys
from datetime import datetime

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawlers.crawler_manager import CrawlerManager
from app.crawlers.site_crawlers import PpomppuCrawler, FmkoreaCrawler, BobaeCrawler, DcinsideCrawler

def crawl_all_sites():
    """모든 사이트 크롤링 실행"""
    print(f"[{datetime.now()}] 크롤링 시작...")
    
    # Flask 앱 초기화 (데이터베이스 저장용)
    try:
        from app import create_app
        from app.models import Post, db
        app = create_app()
        print("Flask 앱 초기화 성공 - 데이터베이스에 저장됩니다")
        use_database = True
    except Exception as e:
        print(f"Flask 앱 초기화 실패: {e} - JSON 파일로만 저장됩니다")
        use_database = False
    
    # 크롤러들 초기화
    crawlers = {
        'ppomppu': PpomppuCrawler(),
        'fmkorea': FmkoreaCrawler(),
        'bobae': BobaeCrawler(),
        'dcinside': DcinsideCrawler()
    }
    
    all_posts = []
    
    for site_name, crawler in crawlers.items():
        try:
            print(f"{site_name} 크롤링 시작...")
            posts = crawler.crawl_popular_posts()
            
            # 사이트별 결과 저장
            for post in posts:
                post['crawled_time'] = datetime.now().isoformat()
                all_posts.append(post)
            
            print(f"{site_name}: {len(posts)}개 게시물 크롤링 완료")
            
        except Exception as e:
            print(f"{site_name} 크롤링 오류: {e}")
            continue
    
    # 데이터베이스에 저장
    if use_database and all_posts:
        try:
            with app.app_context():
                # 기존 데이터 삭제 (최신 데이터만 유지)
                Post.query.delete()
                
                # 새 데이터 저장
                for post_data in all_posts:
                    post = Post(
                        title=post_data['title'],
                        url=post_data['url'],
                        author=post_data.get('author'),
                        site=post_data['site'],
                        category=post_data.get('category', 'humor'),
                        views=post_data.get('views'),
                        likes=post_data.get('likes'),
                        comments=post_data.get('comments'),
                        crawled_at=datetime.now()
                    )
                    db.session.add(post)
                
                db.session.commit()
                print(f"데이터베이스에 {len(all_posts)}개 게시물 저장 완료")
        except Exception as e:
            print(f"데이터베이스 저장 오류: {e}")
            if 'app' in locals():
                with app.app_context():
                    db.session.rollback()
    
    # output 폴더 생성 (존재하지 않을 경우)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 결과를 JSON 파일로 저장
    output_file = os.path.join(output_dir, f"crawl_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'crawl_time': datetime.now().isoformat(),
            'total_posts': len(all_posts),
            'posts': all_posts
        }, f, ensure_ascii=False, indent=2)
    
    print(f"크롤링 완료: 총 {len(all_posts)}개 게시물")
    print(f"결과 저장: {output_file}")
    
    return all_posts

if __name__ == "__main__":
    crawl_all_sites()
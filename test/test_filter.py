#!/usr/bin/env python3
"""제외 필터 테스트 스크립트"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.crawlers.crawler_manager import CrawlerManager

def test_exclude_filter():
    """제외 필터 테스트"""
    app = create_app()
    
    with app.app_context():
        print("🔄 제외 필터가 적용된 크롤링 테스트를 시작합니다...")
        print("=" * 50)
        
        manager = CrawlerManager()
        
        # 각 사이트별로 개별 테스트
        sites = ['ppomppu', 'fmkorea', 'bobae', 'dcinside']
        
        for site in sites:
            print(f"\n{site} 크롤링 시작...")
            try:
                crawler = manager.crawlers[site]
                posts = crawler.crawl_popular_posts()
                print(f"{site}: {len(posts)}개 게시물 수집")
            except Exception as e:
                print(f"{site} 크롤링 오류: {e}")
        
        print("\n" + "=" * 50)
        print("✅ 제외 필터 테스트 완료!")

if __name__ == "__main__":
    test_exclude_filter()
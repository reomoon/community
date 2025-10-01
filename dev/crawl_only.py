#!/usr/bin/env python3
"""
GitHub Actions용 크롤링 전용 스크립트
"""

import json
import os
from datetime import datetime
from app.crawlers.crawler_manager import CrawlerManager
from app.crawlers.site_crawlers import PpomppuCrawler, FmkoreaCrawler, BobaeCrawler, DcinsideCrawler

def crawl_all_sites():
    """모든 사이트 크롤링 실행"""
    print(f"[{datetime.now()}] 크롤링 시작...")
    
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
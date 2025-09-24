#!/usr/bin/env python3
"""보배드림 크롤링 테스트"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawlers.site_crawlers import BobaeCrawler

def test_bobae():
    """보배드림 크롤링 테스트"""
    print("🔄 보배드림 크롤링 테스트를 시작합니다...")
    print("URL: https://www.bobaedream.co.kr/list?code=best")
    print("=" * 50)
    
    crawler = BobaeCrawler()
    posts = crawler.crawl_popular_posts()
    
    print("=" * 50)
    print(f"✅ 보배드림에서 {len(posts)}개의 게시물을 수집했습니다.")
    
    for i, post in enumerate(posts, 1):
        print(f"{i:2d}. {post['title'][:60]}...")
        print(f"    조회: {post['views']:,}, 추천: {post['likes']:,}, 댓글: {post['comments']:,}")
        print(f"    URL: {post['url']}")
        print()
    
    return posts

if __name__ == "__main__":
    test_bobae()
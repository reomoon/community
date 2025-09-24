#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.crawlers.site_crawlers import FmkoreaCrawler

def test_fmkorea_crawler():
    """FMKorea 크롤러 테스트"""
    
    crawler = FmkoreaCrawler()
    
    print("=== FMKorea 크롤러 테스트 ===")
    posts = crawler.crawl_popular_posts()
    
    print(f"\n총 {len(posts)}개의 게시물을 가져왔습니다:")
    
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post['title']}")
        print(f"   작성자: {post['author']}")
        print(f"   조회수: {post['views']:,}")
        print(f"   추천수: {post['likes']:,}")
        print(f"   댓글수: {post['comments']:,}")
        print(f"   인기도: {post['popularity_score']:,}")
        print(f"   URL: {post['url'][:80]}...")

if __name__ == "__main__":
    test_fmkorea_crawler()
#!/usr/bin/env python3
"""크롤링 테스트 스크립트"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawlers.crawler_manager import CrawlerManager

def test_crawling():
    """크롤링 테스트"""
    print("🔄 커뮤니티 크롤링 테스트를 시작합니다...")
    print("=" * 50)
    
    manager = CrawlerManager()
    results = manager.crawl_all_sites()
    
    print("=" * 50)
    print(f"✅ 크롤링 완료! 총 {sum(results.values())}개의 새로운 게시물을 수집했습니다.")
    print("=" * 50)
    
    return results

if __name__ == "__main__":
    test_crawling()
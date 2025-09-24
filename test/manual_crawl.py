#!/usr/bin/env python3
"""Flask 앱 컨텍스트에서 크롤링 실행"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.crawlers.crawler_manager import CrawlerManager

def manual_crawl():
    """수동 크롤링 실행"""
    app = create_app()
    
    with app.app_context():
        print("🔄 수동 크롤링을 시작합니다...")
        print("=" * 50)
        
        manager = CrawlerManager()
        results = manager.crawl_all_sites()
        
        print("=" * 50)
        print(f"✅ 크롤링 완료! 결과: {results}")
        print("=" * 50)
        
        return results

if __name__ == "__main__":
    manual_crawl()
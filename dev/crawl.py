#!/usr/bin/env python3
"""
수동 크롤링 실행 스크립트
"""

import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # dev 폴더의 상위 폴더
sys.path.insert(0, project_root)

from app import create_app
from app.crawlers.crawler_manager import CrawlerManager

def main():
    app = create_app()
    
    with app.app_context():
        print("🔄 커뮤니티 크롤링을 시작합니다...")
        print("=" * 50)
        
        crawler_manager = CrawlerManager()
        
        try:
            result = crawler_manager.crawl_all_sites()
            print("=" * 50)
            print(f"✅ 크롤링 완료! 총 {result}개의 새로운 게시물을 수집했습니다.")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ 크롤링 중 오류 발생: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()
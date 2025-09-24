#!/usr/bin/env python3
"""
커뮤니티 애그리게이터 개발 서버 실행 스크립트
"""

import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app

if __name__ == '__main__':
    # 개발 환경 설정
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    app = create_app()
    
    print("=" * 50)
    print("🔥 커뮤니티 애그리게이터 시작!")
    print("=" * 50)
    print("📱 웹사이트: http://localhost:5000")
    print("🔧 API 문서: http://localhost:5000/api/posts")
    print("🔄 수동 크롤링: http://localhost:5000/api/crawl")
    print("📊 통계: http://localhost:5000/api/stats")
    print("=" * 50)
    print("💡 Ctrl+C로 서버를 중지할 수 있습니다.")
    print("=" * 50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 서버가 종료되었습니다.")
    except Exception as e:
        print(f"\n❌ 서버 실행 중 오류 발생: {e}")
        sys.exit(1)
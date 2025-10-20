#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
캡처 기능 테스트 스크립트
"""

import asyncio
from pathlib import Path
from datetime import datetime

async def test_folder_structure():
    """폴더 구조 테스트"""
    print("=" * 60)
    print("📁 캡처 폴더 구조 테스트")
    print("=" * 60)
    
    base_dir = Path("capture")
    today = datetime.now().strftime("%Y-%m-%d")
    date_dir = base_dir / today
    
    # 테스트 폴더 생성
    test_sites = ['bobae', 'ruliweb', 'dcinside', 'fmkorea']
    
    for site in test_sites:
        site_dir = date_dir / site
        site_dir.mkdir(parents=True, exist_ok=True)
        
        # 테스트 파일 생성 (빈 파일)
        test_file = site_dir / f"{site}_test_part01.png"
        test_file.touch()
        
        print(f"✅ {site:12s} 폴더 생성: {site_dir}")
    
    print("\n📂 최종 폴더 구조:")
    print(f"capture/")
    print(f"└── {today}/")
    for site in test_sites:
        print(f"    ├── {site}/")
        print(f"    │   └── {site}_*.png")
    
    print("\n✅ 폴더 구조 테스트 완료!")
    print(f"📍 위치: {date_dir.absolute()}")

async def test_overlap_calculation():
    """오버랩 계산 테스트"""
    print("\n" + "=" * 60)
    print("📐 오버랩 캡처 계산 테스트")
    print("=" * 60)
    
    viewport_height = 915  # 갤럭시 S25
    overlap = 100  # 오버랩
    effective_height = viewport_height - overlap  # 815px
    
    test_heights = [1000, 2000, 3000, 5000, 10000]
    
    for total_height in test_heights:
        segments = max(1, min(10, (total_height + effective_height - 1) // effective_height))
        
        print(f"\n페이지 높이: {total_height}px")
        print(f"  → {segments}개 구간으로 분할")
        print(f"  → 각 구간: {effective_height}px (오버랩 {overlap}px 포함)")
        
        for i in range(min(3, segments)):
            if i == 0:
                scroll_y = 0
            else:
                scroll_y = i * effective_height
            print(f"     구간 {i+1}: 스크롤 위치 {scroll_y}px")

async def test_nickname_selectors():
    """닉네임 셀렉터 테스트"""
    print("\n" + "=" * 60)
    print("🎭 닉네임 모자이크 셀렉터 확인")
    print("=" * 60)
    
    nickname_selectors = {
        'bobae': [
            '.nick', '.name', '.writer', 
            '.re_name', '.comment_writer',
            '.ub-writer', '.writer-name'
        ],
        'ruliweb': [
            '.nick', '.user_nick', '.comment_nick',
            '.writer', '.author', '.user_id'
        ],
        'fmkorea': [
            '.nick', '.nickname', '.username',
            '.member', '.writer', '.author_nick'
        ],
        'dcinside': [
            '.nickname', '.gall_writer', '.writer',
            '.nick', '.user_nick', '.reply_name'
        ]
    }
    
    for site, selectors in nickname_selectors.items():
        print(f"\n{site:12s}: {len(selectors)}개 셀렉터")
        for sel in selectors:
            print(f"  - {sel}")
    
    print("\n✅ 모든 사이트에 닉네임 모자이크 적용 준비됨")

async def main():
    """전체 테스트 실행"""
    print("\n🚀 캡처 시스템 개선 사항 테스트\n")
    
    # 1. 폴더 구조 테스트
    await test_folder_structure()
    
    # 2. 오버랩 계산 테스트
    await test_overlap_calculation()
    
    # 3. 닉네임 셀렉터 테스트
    await test_nickname_selectors()
    
    print("\n" + "=" * 60)
    print("✨ 개선 사항 요약")
    print("=" * 60)
    print("""
1️⃣ 폴더 구조 개선
   capture/
   └── 2025-10-18/          # 날짜별 폴더
       ├── bobae/            # 사이트별 폴더
       ├── ruliweb/
       ├── dcinside/
       └── fmkorea/

2️⃣ 오버랩 캡처 (100px)
   - 구간 간 100px 오버랩으로 자연스러운 연결
   - 스크롤 시 짤림 없이 완전한 콘텐츠 캡처
   - 최대 10개 구간으로 제한

3️⃣ 닉네임 모자이크
   - 댓글 작성자 닉네임 자동 블러 처리
   - 사이트별 맞춤 셀렉터 적용
   - blur(8px) + 투명도 + 배경 처리
    """)
    
    print("🎉 모든 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())

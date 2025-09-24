#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re

def analyze_dcinside_structure():
    """디시인사이드 HTML 구조 분석"""
    
    url = "https://gall.dcinside.com/board/lists/?id=dcbest"
    
    # 헤더 추가해서 브라우저처럼 보이게 하기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"응답 상태: {response.status_code}")
        print(f"응답 길이: {len(response.content)} bytes")
        
        # 응답 내용의 일부를 확인
        content_preview = response.text[:2000]
        print(f"응답 내용 미리보기:\n{content_preview}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== 디시인사이드 게시물 구조 분석 ===")
        
        # 다양한 선택자로 게시물 목록 찾기
        selectors = [
            'tr.ub-content',
            'tr[class*="content"]',
            'tr[class*="list"]',
            '.gall_list tr',
            'tbody tr',
            'table tr'
        ]
        
        post_rows = []
        for selector in selectors:
            rows = soup.select(selector)
            print(f"선택자 '{selector}': {len(rows)}개 발견")
            if rows and len(rows) > 5:  # 충분한 수의 행이 있으면 사용
                post_rows = rows
                break
        
        print(f"최종 선택된 게시물: {len(post_rows)}개")
        
        if post_rows:
            for i, row in enumerate(post_rows[:3]):  # 처음 3개만 분석
                print(f"\n--- 게시물 {i+1} ---")
                
                # 제목 셀
                title_cell = row.find('td', class_='gall_tit')
                if title_cell:
                    title_link = title_cell.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                        print(f"제목: {title}")
                        
                        # 댓글수 패턴 찾기
                        comment_patterns = [
                            r'\[(\d+)\]',     # [숫자] 패턴
                            r'\((\d+)\)',     # (숫자) 패턴
                            r'댓글\s*(\d+)',  # 댓글 숫자 패턴
                            r'(\d+)개',       # 숫자개 패턴
                        ]
                        
                        for pattern in comment_patterns:
                            match = re.search(pattern, title)
                            if match:
                                print(f"댓글수 발견 (패턴 {pattern}): {match.group(1)}")
                                break
                        else:
                            print("제목에서 댓글수를 찾을 수 없음")
                
                # 모든 td 요소 분석
                tds = row.find_all('td')
                print(f"총 {len(tds)}개의 셀:")
                
                for j, td in enumerate(tds):
                    class_name = td.get('class', [])
                    text = td.get_text(strip=True)
                    print(f"  셀 {j}: 클래스={class_name}, 텍스트='{text[:30]}...' if len(text) > 30 else text")
                    
                    # 댓글수가 있을 수 있는 셀 찾기
                    if any(keyword in text.lower() for keyword in ['댓글', 'comment', '개']):
                        print(f"    → 댓글 관련 가능성 있음: {text}")
                
                # 특별한 댓글 관련 요소 찾기
                comment_elements = row.find_all(['span', 'em', 'strong'], string=re.compile(r'\d+'))
                if comment_elements:
                    print("댓글 관련 가능 요소들:")
                    for elem in comment_elements:
                        print(f"  {elem.name}: {elem.get_text()} (클래스: {elem.get('class', [])})")
        
        print("\n=== 전체 HTML 구조 ===")
        # 첫 번째 게시물의 전체 HTML 출력 (디버깅용)
        if post_rows:
            first_row = post_rows[0]
            print("첫 번째 게시물 HTML:")
            print(str(first_row)[:1000] + "...")
    
    except Exception as e:
        print(f"분석 중 오류: {e}")

if __name__ == "__main__":
    analyze_dcinside_structure()
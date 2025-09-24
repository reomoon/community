#!/usr/bin/env python3
"""보배드림 HTML 구조 분석"""

import requests
from bs4 import BeautifulSoup
import re

def analyze_bobae():
    """보배드림 HTML 구조 분석"""
    url = "https://www.bobaedream.co.kr/list?code=best"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 보배드림 HTML 구조 분석")
        print("=" * 50)
        
        # .pl14 클래스 게시물들 찾기
        post_cells = soup.select('.pl14')
        
        print(f"총 {len(post_cells)}개의 .pl14 게시물 발견")
        print()
        
        for i, cell in enumerate(post_cells[:5]):
            title_link = cell.select_one('a')
            if title_link:
                title = title_link.get_text(strip=True)
                href = title_link.get('href', '')
                
                print(f"{i+1:2d}. 제목: {title}")
                print(f"    URL: {href}")
                
                # 부모 tr 찾기
                parent_tr = cell.find_parent('tr')
                if parent_tr:
                    tds = parent_tr.find_all('td')
                    print(f"    TR 셀 개수: {len(tds)}")
                    
                    for j, td in enumerate(tds):
                        td_text = td.get_text(strip=True)
                        td_class = td.get('class', [])
                        print(f"      TD[{j}]: '{td_text}' (class: {td_class})")
                
                # 제목에서 댓글 수 패턴 찾기
                comment_patterns = [
                    r'\[(\d+)\]',  # [숫자]
                    r'\((\d+)\)',  # (숫자)
                    r'(\d+)$',     # 끝에 숫자
                ]
                
                for pattern in comment_patterns:
                    match = re.search(pattern, title)
                    if match:
                        print(f"    댓글 패턴 '{pattern}': {match.group(1)}")
                
                print()
                
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    analyze_bobae()
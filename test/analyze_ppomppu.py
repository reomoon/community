#!/usr/bin/env python3
"""뽐뿌 HTML 구조 분석"""

import requests
from bs4 import BeautifulSoup

def analyze_ppomppu():
    """뽐뿌 HTML 구조 분석"""
    url = "https://www.ppomppu.co.kr/hot.php?category=2"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 뽐뿌 HTML 구조 분석")
        print("=" * 50)
        
        # view.php 링크들 찾기
        view_links = soup.find_all('a', href=lambda x: x and 'view.php' in x)
        
        print(f"총 {len(view_links)}개의 view.php 링크 발견")
        print()
        
        for i, link in enumerate(view_links[:10]):
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            print(f"{i+1:2d}. 제목: {title}")
            print(f"    URL: {href}")
            print(f"    부모: {link.parent.name if link.parent else 'None'}")
            
            # 부모 tr 찾기
            parent = link.parent
            for _ in range(5):
                if parent and parent.name == 'tr':
                    tds = parent.find_all('td')
                    td_texts = [td.get_text(strip=True) for td in tds]
                    print(f"    TR 내용: {td_texts}")
                    break
                parent = parent.parent if parent else None
            
            print()
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    analyze_ppomppu()
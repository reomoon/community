#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re

def analyze_fmkorea_structure():
    """FMKorea HTML 구조 분석"""
    
    url = "https://www.fmkorea.com/best2"
    
    # 헤더 추가해서 브라우저처럼 보이게 하기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"응답 상태: {response.status_code}")
        print(f"응답 길이: {len(response.content)} bytes")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== FMKorea 게시물 구조 분석 ===")
        
        # 게시물 목록 찾기
        article_list = soup.select('.fm_best_widget li')
        print(f"총 {len(article_list)}개의 게시물 발견")
        
        if article_list:
            for i, article in enumerate(article_list[:3]):  # 처음 3개만 분석
                print(f"\n--- 게시물 {i+1} ---")
                
                # 제목 찾기
                title_links = article.find_all('a')
                main_link = None
                title = ""
                
                for link in title_links:
                    link_text = link.get_text(strip=True)
                    if len(link_text) > len(title) and len(link_text) > 5:
                        title = link_text
                        main_link = link
                
                print(f"제목: {title}")
                
                # 모든 span 요소 분석
                spans = article.find_all('span')
                print(f"총 {len(spans)}개의 span 요소:")
                
                for j, span in enumerate(spans):
                    class_name = span.get('class', [])
                    text = span.get_text(strip=True)
                    print(f"  span {j}: 클래스={class_name}, 텍스트='{text}'")
                    
                    # 조회수나 숫자가 있을 수 있는 span 찾기
                    if re.search(r'\d+', text):
                        print(f"    → 숫자 포함: {text}")
                
                # 다른 요소들도 확인
                print("\n모든 하위 요소들:")
                for elem in article.find_all():
                    if elem.get_text(strip=True) and re.search(r'\d+', elem.get_text()):
                        print(f"  {elem.name} ({elem.get('class', [])}): {elem.get_text(strip=True)}")
                
                print(f"\n첫 번째 게시물 전체 HTML:\n{str(article)[:1000]}...")
        
    except Exception as e:
        print(f"분석 중 오류: {e}")

if __name__ == "__main__":
    analyze_fmkorea_structure()
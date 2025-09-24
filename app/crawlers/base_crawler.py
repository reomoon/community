import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict
from abc import ABC, abstractmethod

class BaseCrawler(ABC):
    """크롤러 기본 클래스"""
    
    def __init__(self, site_name: str):
        self.site_name = site_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @abstractmethod
    def crawl_popular_posts(self) -> List[Dict]:
        """인기 게시물 크롤링"""
        pass
    
    def categorize_post(self, title: str, content: str = "") -> str:
        """게시물 카테고리 분류 - 단순히 '인기' 카테고리로 통일"""
        return '인기'
    
    def should_exclude_post(self, title: str, content: str = "") -> bool:
        """게시물 제외 여부 판단"""
        title_lower = title.lower()
        content_lower = content.lower()
        text = f"{title_lower} {content_lower}"
        
        # 제외 키워드 목록
        exclude_keywords = [
            # 광고성 키워드
            '광고', '홍보', '이벤트', '쿠폰', '할인', '무료배송', '적립', '캐시백',
            '포인트', '마케팅', '스폰서', '협찬', 'pr', '프로모션',
            
            # 쇼핑몰/판매 키워드
            '[g마켓]', '[쿠팡]', '[11번가]', '[티몬]', '[위메프]', '[ssg]', '[지마켓]',
            '[옥션]', '[인터파크]', '[롯데온]', '[네이버쇼핑]',
            '원/무료', '원/무배', '무료)', '배송비', '택배',
            
            # 기타 제외 키워드
            '공지사항', '갤러리 이용 안내',
            '청소년보호정책', '개인정보처리방침', '이용약관'
            
            # 반복성 키워드
            'live', '라이브', '실시간', '방송', '스트리밍'
        ]
        
        # 키워드 매칭 확인
        for keyword in exclude_keywords:
            if keyword in text:
                return True
        
        # 제목이 너무 짧거나 긴 경우
        if len(title.strip()) < 5 or len(title.strip()) > 200:
            return True
            
        # 특수문자만 있는 제목
        if re.match(r'^[^\w\s가-힣]+$', title.strip()):
            return True
            
        return False
    
    def extract_numbers(self, text: str) -> int:
        """텍스트에서 숫자 추출"""
        if not text:
            return 0
        
        # 숫자와 쉼표만 추출
        numbers = re.findall(r'[\d,]+', text)
        if numbers:
            # 쉼표 제거 후 정수 변환
            try:
                return int(numbers[0].replace(',', ''))
            except ValueError:
                return 0
        return 0
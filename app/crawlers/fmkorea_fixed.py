from .base_crawler import BaseCrawler
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import re
import requests

class FmkoreaCrawler(BaseCrawler):
    """fmkorea 크롤러 - 강화된 버전"""
    
    def __init__(self):
        super().__init__('fmkorea')
        self.base_url = 'https://www.fmkorea.com'
        
        # 에펨코리아용 특수 헤더 설정
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
    
    def crawl_popular_posts(self) -> List[Dict]:
        """fmkorea 인기 게시물 크롤링"""
        posts = []
        
        # 여러 URL 시도
        urls_to_try = [
            f"{self.base_url}/best2",
            f"{self.base_url}/best",
            f"{self.base_url}/index.php?mid=best2",
            f"{self.base_url}/index.php?mid=best",
            f"{self.base_url}/hotdeal",
            f"{self.base_url}/index.php?mid=hotdeal",
            "https://m.fmkorea.com/best2",  # 모바일 버전
            "https://m.fmkorea.com/best"
        ]
        
        for attempt, url in enumerate(urls_to_try, 1):
            try:
                print(f"에펨코리아 크롤링 시도 {attempt}: {url}")
                
                # 재시도 로직 추가
                response = None
                for retry in range(3):
                    try:
                        response = self.session.get(url, timeout=15, allow_redirects=True)
                        print(f"에펨코리아 응답 상태: {response.status_code}")
                        response.raise_for_status()
                        break
                    except requests.exceptions.RequestException as e:
                        print(f"에펨코리아 요청 실패 (재시도 {retry+1}/3): {e}")
                        if retry == 2:
                            raise
                        time.sleep(2)
                
                if not response:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                print(f"에펨코리아 HTML 길이: {len(response.content)}")
                
                # Cloudflare 차단 확인
                if 'Checking your browser' in response.text or 'Just a moment' in response.text:
                    print("에펨코리아 Cloudflare 차단 감지")
                    continue
                
                # 게시물 목록 파싱 (여러 셀렉터 시도)
                article_list = soup.select('.fm_best_widget li')
                
                # 대체 셀렉터들 시도
                if not article_list:
                    article_list = soup.select('.best-list li')
                if not article_list:
                    article_list = soup.select('.widget li')
                if not article_list:
                    article_list = soup.select('.fm_best li')
                if not article_list:
                    article_list = soup.select('article')
                
                # 더 넓은 범위로 찾기
                if not article_list:
                    article_list = soup.select('li a')
                if not article_list:
                    article_list = soup.select('a')
                    
                print(f"에펨코리아 게시물 찾음: {len(article_list)}개")
                
                post_list = []
                for article in article_list[:50]:  # 처음 50개만 처리
                    try:
                        # 제목 링크 찾기
                        if article.name == 'a':
                            title_links = [article]
                        else:
                            title_links = article.find_all('a')
                        
                        main_link = None
                        title = ""
                        
                        # 가장 긴 텍스트를 가진 링크를 제목으로 사용
                        for link in title_links:
                            link_text = link.get_text(strip=True)
                            if len(link_text) > len(title) and len(link_text) > 5:
                                title = link_text
                                main_link = link
                        
                        if not main_link or not title:
                            continue
                        
                        # 제외 단어 필터링
                        if self.should_exclude_post(title):
                            continue
                        
                        # URL 구성
                        href = main_link.get('href', '')
                        if href.startswith('/'):
                            post_url = self.base_url + href
                        elif href.startswith('http'):
                            post_url = href
                        else:
                            post_url = f"{self.base_url}/{href}"
                        
                        # 작성자 정보
                        author = 'fmkorea'
                        if article.name != 'a':
                            author_elem = article.find('span', class_='author')
                            if author_elem:
                                author = author_elem.get_text(strip=True).replace('/', '').strip()
                        
                        # 추천수, 댓글수 등 기본값
                        likes = 0
                        comments = 0
                        views = 0
                        
                        # 인기도 점수 계산
                        popularity_score = views + (likes * 2) + (comments * 3)
                        
                        post_data = {
                            'title': title,
                            'url': post_url,
                            'site': self.site_name,
                            'category': '인기',
                            'author': author,
                            'views': views,
                            'likes': likes,
                            'comments': comments,
                            'popularity_score': popularity_score
                        }
                        
                        post_list.append(post_data)
                        
                        # 충분히 모았으면 중단
                        if len(post_list) >= 10:
                            break
                        
                    except Exception as e:
                        print(f"에펨코리아 게시물 파싱 오류: {e}")
                        continue
                
                # 게시물을 찾았으면 더 이상 다른 URL 시도하지 않음
                if post_list:
                    print(f"에펨코리아 게시물 파싱 성공: {len(post_list)}개")
                    posts = post_list[:10]
                    
                    for post in posts:
                        print(f"에펨코리아 게시물 추가: {post['title'][:50]}...")
                    break
                    
            except Exception as e:
                print(f"에펨코리아 크롤링 오류 (시도 {attempt}): {e}")
                continue
        
        if not posts:
            print("⚠️ 에펨코리아 크롤링 완전 실패 - 모든 URL 시도 실패")
        
        return posts
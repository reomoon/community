from .base_crawler import BaseCrawler
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import re
import requests

class PpomppuCrawler(BaseCrawler):
    """뽐뿌 크롤러"""
    
    def __init__(self):
        super().__init__('ppomppu')
        self.base_url = 'https://www.ppomppu.co.kr'
    
    def crawl_popular_posts(self) -> List[Dict]:
        """뽐뿌 인기 게시물 크롤링"""
        posts = []
        
        try:
            # 뽐뿌 HOT 게시판 (자유게시판)
            url = f"{self.base_url}/hot.php?category=2"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            post_list = []
            seen_titles = set()  # 중복 제목 방지
            
            # 뽐뿌의 테이블 구조를 이용해 정확히 파싱
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    tds = row.find_all('td')
                    if len(tds) < 6:  # 충분한 셀이 없으면 제외
                        continue
                    
                    # 제목 셀 (3번째 셀, 인덱스 2)
                    title_cell = tds[2]
                    title_link = title_cell.find('a', href=lambda x: x and 'view.php' in x)
                    
                    if not title_link:
                        continue
                    
                    href = title_link.get('href', '')
                    full_title = title_cell.get_text(strip=True)
                    
                    # 빈 제목이나 너무 짧은 제목 제외
                    if not full_title or len(full_title) < 5:
                        continue
                    
                    # 중복 제목 체크
                    if full_title in seen_titles:
                        continue
                    seen_titles.add(full_title)
                    
                    # 광고/제휴 제외
                    if any(word in full_title.lower() for word in ['광고', '홍보', '스폰서', '협찬', 'ad', '제휴']):
                        print(f"뽐뿌 게시물 제외: {full_title[:30]}...")
                        continue
                    
                    # URL 구성
                    if href.startswith('/'):
                        post_url = f"{self.base_url}{href}"
                    elif not href.startswith('http'):
                        post_url = f"{self.base_url}/{href}"
                    else:
                        post_url = href
                    
                    # TR 구조: ['카테고리', '아이콘', '제목+댓글수', '작성자', '시간', '추천-비추천', '조회수']
                    
                    # 작성자 (4번째 셀, 인덱스 3)
                    author = tds[3].get_text(strip=True) if len(tds) > 3 else "뽐뿌"
                    
                    # 조회수 (7번째 셀, 인덱스 6)
                    views = 0
                    if len(tds) > 6:
                        views_text = tds[6].get_text(strip=True)
                        if views_text.isdigit():
                            views = int(views_text)
                    
                    # 추천수 (6번째 셀, 인덱스 5) - "9 - 0" 형태에서 첫 번째 숫자
                    likes = 0
                    if len(tds) > 5:
                        likes_text = tds[5].get_text(strip=True)
                        likes_match = re.search(r'^(\d+)', likes_text)
                        if likes_match:
                            likes = int(likes_match.group(1))
                    
                    # 댓글수 (제목 끝의 숫자)
                    comments = 0
                    title_end_number = re.search(r'(\d+)$', full_title)
                    if title_end_number:
                        comments = int(title_end_number.group(1))
                        # 제목에서 댓글수 제거
                        title = re.sub(r'\d+$', '', full_title).strip()
                    else:
                        title = full_title
                    
                    # 인기도 점수 계산
                    popularity_score = views + (likes * 2) + (comments * 3)
                    
                    post_data = {
                        'title': title,
                        'url': post_url,
                        'author': author,
                        'site': self.site_name,
                        'category': '인기',
                        'views': views,
                        'likes': likes,
                        'comments': comments,
                        'popularity_score': popularity_score
                    }
                    
                    post_list.append(post_data)
            
            # 인기도 순으로 정렬하고 상위 10개만 선택
            post_list.sort(key=lambda x: x['popularity_score'], reverse=True)
            posts = post_list[:10]
            
            for post in posts:
                print(f"뽐뿌 게시물 추가: {post['title'][:50]}... (조회:{post['views']}, 추천:{post['likes']}, 댓글:{post['comments']})")
                    
        except Exception as e:
            print(f"뽐뿌 크롤링 오류: {e}")
        
        return posts


class FmkoreaCrawler(BaseCrawler):
    """fmkorea 크롤러 - 강화된 버전"""
    
    def __init__(self):
        super().__init__('fmkorea')
        self.base_url = 'https://www.fmkorea.com'
        
        # 에펨코리아용 간단한 헤더 설정 (430 오류 방지)
        self.session.headers.clear()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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


class BobaeCrawler(BaseCrawler):
    """보배드림 크롤러"""
    
    def __init__(self):
        super().__init__('bobae')
        self.base_url = 'https://www.bobaedream.co.kr'
    
    def crawl_popular_posts(self) -> List[Dict]:
        """보배드림 인기 게시물 크롤링"""
        posts = []
        
        try:
            # 베스트 게시판
            url = f"{self.base_url}/board/bulletin/list.php?code=best&vdate=w"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # .pl14 클래스로 게시물 찾기
            post_cells = soup.select('.pl14')
            
            post_list = []
            for cell in post_cells:  # 모든 게시물 처리
                try:
                    title_link = cell.select_one('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # 제외 단어 필터링
                    if self.should_exclude_post(title):
                        print(f"보배드림 게시물 제외: {title[:30]}...")
                        continue
                    
                    # URL 구성
                    href = title_link.get('href', '')
                    if href.startswith('/'):
                        post_url = self.base_url + href
                    else:
                        post_url = href
                    
                    # 부모 tr에서 다른 정보 찾기
                    parent_tr = cell.find_parent('tr')
                    if not parent_tr:
                        continue
                    
                    # 부모 tr에서 정보 추출
                    tds = parent_tr.find_all('td')
                    
                    # TR 구조: [카테고리, 제목+댓글, 작성자, 시간, 추천수, 조회수]
                    
                    # 작성자 (TD[2])
                    author = tds[2].get_text(strip=True) if len(tds) > 2 else '보배드림'
                    
                    # 조회수 (TD[5])
                    views = 0
                    if len(tds) > 5:
                        views_text = tds[5].get_text(strip=True)
                        if views_text.isdigit():
                            views = int(views_text)
                    
                    # 추천수 (TD[4])
                    likes = 0
                    if len(tds) > 4:
                        likes_text = tds[4].get_text(strip=True)
                        if likes_text.isdigit():
                            likes = int(likes_text)
                    
                    # 댓글수 (제목에서 (숫자) 형태로 추출)
                    comments = 0
                    full_title = tds[1].get_text(strip=True) if len(tds) > 1 else title
                    
                    # (숫자) 패턴으로 댓글수 추출
                    comment_match = re.search(r'\((\d+)\)', full_title)
                    if comment_match:
                        comments = int(comment_match.group(1))
                        # 제목에서 댓글수 제거
                        title = re.sub(r'\(\d+\)', '', full_title).strip()
                    else:
                        title = full_title
                    
                    # 인기도 점수 계산 (조회수 + 추천수*2 + 댓글수*3)
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
                    
                except Exception as e:
                    print(f"보배드림 게시물 파싱 오류: {e}")
                    continue
            
            # 인기도 순으로 정렬하고 상위 10개만 선택
            post_list.sort(key=lambda x: x['popularity_score'], reverse=True)
            posts = post_list[:10]
            
            for post in posts:
                print(f"보배드림 게시물 추가: {post['title'][:50]}... (조회:{post['views']}, 추천:{post['likes']}, 댓글:{post['comments']})")
                    
        except Exception as e:
            print(f"보배드림 크롤링 오류: {e}")
        
        return posts


class DcinsideCrawler(BaseCrawler):
    """디시인사이드 크롤러"""
    
    def __init__(self):
        super().__init__('dcinside')
        self.base_url = 'https://gall.dcinside.com'
    
    def crawl_popular_posts(self) -> List[Dict]:
        """디시인사이드 인기 게시물 크롤링"""
        posts = []
        
        try:
            # 실시간 베스트 게시판
            url = f"{self.base_url}/board/lists/?id=dcbest"
            
            # 브라우저처럼 보이게 헤더 추가
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 게시물 목록 찾기 (더 정확한 선택자 사용)
            post_rows = soup.select('tr.ub-content')
            
            post_list = []
            for row in post_rows:  # 모든 게시물 처리
                try:
                    # 제목 링크 찾기
                    title_cell = row.find('td', class_='gall_tit')
                    if not title_cell:
                        continue
                    
                    title_link = title_cell.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # 제외 단어 필터링
                    if self.should_exclude_post(title):
                        print(f"디시인사이드 게시물 제외: {title[:30]}...")
                        continue
                    
                    # URL 구성
                    href = title_link.get('href', '')
                    if href.startswith('/'):
                        post_url = self.base_url + href
                    else:
                        post_url = href
                    
                    # 작성자
                    author_cell = row.find('td', class_='gall_writer')
                    author = author_cell.get_text(strip=True) if author_cell else '디시'
                    
                    # 조회수 찾기
                    views = 0
                    count_cell = row.find('td', class_='gall_count')
                    if count_cell:
                        try:
                            views = int(count_cell.get_text(strip=True))
                        except:
                            views = 0
                    
                    # 추천수 찾기
                    likes = 0
                    recommend_cell = row.find('td', class_='gall_recommend')
                    if recommend_cell:
                        try:
                            likes = int(recommend_cell.get_text(strip=True))
                        except:
                            likes = 0
                    
                    # 댓글수 (span.reply_num에서 추출)
                    comments = 0
                    
                    # 먼저 reply_num 클래스에서 찾기
                    reply_elem = title_cell.find('span', class_='reply_num')
                    if reply_elem:
                        reply_text = reply_elem.get_text(strip=True)
                        # [숫자/숫자] 또는 [숫자] 형태에서 첫 번째 숫자 추출
                        comment_match = re.search(r'\[(\d+)', reply_text)
                        if comment_match:
                            comments = int(comment_match.group(1))
                    
                    # reply_num이 없으면 제목에서 직접 찾기
                    if comments == 0:
                        comment_patterns = [
                            r'\[(\d+)/\d+\]',  # [숫자/숫자] 패턴
                            r'\[(\d+)\]',      # [숫자] 패턴
                        ]
                        
                        for pattern in comment_patterns:
                            comment_match = re.search(pattern, title)
                            if comment_match:
                                comments = int(comment_match.group(1))
                                break
                    
                    # 인기도 점수 계산 (조회수 + 추천수*2 + 댓글수*3)
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
                    
                except Exception as e:
                    print(f"디시인사이드 게시물 파싱 오류: {e}")
                    continue
            
            # 인기도 순으로 정렬하고 상위 10개만 선택
            post_list.sort(key=lambda x: x['popularity_score'], reverse=True)
            posts = post_list[:10]
            
            for post in posts:
                print(f"디시인사이드 게시물 추가: {post['title'][:50]}... (조회:{post['views']}, 추천:{post['likes']}, 댓글:{post['comments']})")
                
        except Exception as e:
            print(f"디시인사이드 크롤링 오류: {e}")
        
        return posts
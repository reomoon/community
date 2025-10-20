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
        
        # 에펨코리아용 다양한 헤더 설정 (430 오류 방지)
        self.session.headers.clear()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 요청 간격을 더 늘리고 타임아웃 설정
        import time
        self._last_request_time = 0
        self.request_delay = 3  # 3초 간격
    
    def crawl_popular_posts(self) -> List[Dict]:
        """fmkorea 인기 게시물 크롤링"""
        posts = []
        
        # GitHub Actions 환경에서는 에펨코리아 크롤링 스킵 (IP 차단 문제)
        import os
        if os.getenv('GITHUB_ACTIONS') == 'true':
            print("에펨코리아: GitHub Actions 환경에서는 IP 차단으로 인해 스킵합니다.")
            return posts
        
        # 여러 URL 시도 (GitHub Actions 환경 고려)
        urls_to_try = [
            "https://m.fmkorea.com/best2",   # 모바일 버전 우선
            "https://m.fmkorea.com/best",
            "https://m.fmkorea.com/hotdeal",
            f"{self.base_url}/best2",
            f"{self.base_url}/best", 
            f"{self.base_url}/hotdeal",
            f"{self.base_url}/index.php?mid=best2",
            f"{self.base_url}/index.php?mid=best",
            f"{self.base_url}/index.php?mid=hotdeal",
            "https://m.fmkorea.com/",  # 모바일 메인
            f"{self.base_url}/"  # 데스크톱 메인
        ]
        
        for attempt, url in enumerate(urls_to_try, 1):
            try:
                print(f"에펨코리아 크롤링 시도 {attempt}: {url}")
                
                # 요청 간격 조절 (Rate Limiting 방지)
                import time
                current_time = time.time()
                if current_time - self._last_request_time < self.request_delay:
                    sleep_time = self.request_delay - (current_time - self._last_request_time)
                    print(f"요청 간격 조절: {sleep_time:.1f}초 대기")
                    time.sleep(sleep_time)
                
                # urllib을 사용한 더 간단한 요청 방식 시도
                response = None
                for retry in range(3):
                    try:
                        # urllib 사용으로 헤더 최소화
                        import urllib.request
                        import urllib.error
                        
                        req = urllib.request.Request(
                            url,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                'Accept': 'text/html,application/xhtml+xml',
                                'Accept-Language': 'ko-KR,ko;q=0.8'
                            }
                        )
                        
                        with urllib.request.urlopen(req, timeout=15) as response_raw:
                            content = response_raw.read()
                            
                        # requests Response 객체처럼 만들기
                        class SimpleResponse:
                            def __init__(self, content):
                                self.content = content
                                self.text = content.decode('utf-8', errors='ignore')
                                self.status_code = 200
                        
                        response = SimpleResponse(content)
                        print(f"에펨코리아 응답 상태: {response.status_code}")
                        self._last_request_time = time.time()
                        break
                        
                    except Exception as e:
                        print(f"에펨코리아 요청 실패 (재시도 {retry+1}/3): {e}")
                        if retry == 2:
                            # urllib 실패시 기존 requests 방식으로 폴백
                            try:
                                response = self.session.get(url, timeout=15, allow_redirects=True)
                                response.raise_for_status()
                                self._last_request_time = time.time()
                                break
                            except:
                                raise e
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
        """보배드림 인기 게시물 크롤링 (베스트 + 실시간 베스트)"""
        posts = []
        
        # 두 개의 URL에서 크롤링하여 총 20개 게시물 수집
        urls = [
            # 기존 베스트 게시판 (20개)
            f"{self.base_url}/board/bulletin/list.php?code=best&vdate=w",
            # # 실시간 베스트 게시판 (10개 추가)
            # f"{self.base_url}/list?code=best"
        ]
        
        all_post_list = []
        
        for url_idx, url in enumerate(urls):
            try:
                print(f"보배드림 크롤링 {url_idx + 1}/2: {url}")
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # URL에 따라 다른 선택자 사용
                if "board/bulletin" in url:
                    # 기존 베스트 게시판 (.pl14 클래스)
                    post_cells = soup.select('.pl14')
                else:
                    # 실시간 베스트 게시판 (다른 구조 시도)
                    post_cells = soup.select('.pl14') or soup.select('.listSub a') or soup.select('.list-table td a') or soup.select('.board-list td a') or soup.select('td a')
                
                print(f"보배드림 게시물 {len(post_cells)}개 발견")
                
                # 각 URL에서 최대 10개씩만 처리
                current_url_posts = []
                for cell in post_cells[:20]:  # 처음 20개만 처리하여 10개 선별
                    try:
                        # cell이 a 태그인지 확인
                        if cell.name == 'a':
                            title_link = cell
                            title = cell.get_text(strip=True)
                        else:
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
                        
                        # 기본값 설정
                        author = '보배드림'
                        views = 0
                        likes = 0
                        comments = 0
                        
                        # 부모 tr에서 다른 정보 찾기 (첫 번째 URL의 경우)
                        if "board/bulletin" in url:
                            parent_tr = cell.find_parent('tr')
                            if parent_tr:
                                # 부모 tr에서 정보 추출
                                tds = parent_tr.find_all('td')
                                
                                # TR 구조: [카테고리, 제목+댓글, 작성자, 시간, 추천수, 조회수]
                                
                                # 작성자 (TD[2])
                                author = tds[2].get_text(strip=True) if len(tds) > 2 else '보배드림'
                                
                                # 조회수 (TD[5])
                                if len(tds) > 5:
                                    views_text = tds[5].get_text(strip=True)
                                    if views_text.isdigit():
                                        views = int(views_text)
                                
                                # 추천수 (TD[4])
                                if len(tds) > 4:
                                    likes_text = tds[4].get_text(strip=True)
                                    if likes_text.isdigit():
                                        likes = int(likes_text)
                                
                                # 댓글수 (제목에서 (숫자) 형태로 추출)
                                full_title = tds[1].get_text(strip=True) if len(tds) > 1 else title
                                
                                # (숫자) 패턴으로 댓글수 추출
                                comment_match = re.search(r'\((\d+)\)', full_title)
                                if comment_match:
                                    comments = int(comment_match.group(1))
                                    # 제목에서 댓글수 제거
                                    title = re.sub(r'\(\d+\)', '', full_title).strip()
                        else:
                            # 실시간 베스트의 경우 기본값 사용
                            # 댓글수만 제목에서 추출 시도
                            comment_match = re.search(r'\((\d+)\)', title)
                            if comment_match:
                                comments = int(comment_match.group(1))
                                title = re.sub(r'\(\d+\)', '', title).strip()
                        
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
                        
                        current_url_posts.append(post_data)
                        
                    except Exception as e:
                        print(f"보배드림 게시물 파싱 오류: {e}")
                        continue
                
                # 현재 URL에서 가져온 게시물들을 인기도순으로 정렬하고 상위 10개만 선택
                current_url_posts.sort(key=lambda x: x['popularity_score'], reverse=True)
                selected_posts = current_url_posts[:10]
                
                print(f"보배드림 URL {url_idx + 1}에서 {len(selected_posts)}개 게시물 선택")
                all_post_list.extend(selected_posts)
                
            except Exception as e:
                print(f"보배드림 크롤링 오류 (URL {url_idx + 1}): {e}")
                continue
        
        # 중복 제거 (URL 기준) - 각 URL에서 이미 10개씩 선택했으므로 최대 20개
        seen_urls = set()
        unique_posts = []
        for post in all_post_list:
            if post['url'] not in seen_urls:
                seen_urls.add(post['url'])
                unique_posts.append(post)
        
        # 최종적으로 20개 또는 중복 제거된 모든 게시물 반환
        posts = unique_posts
        
        for post in posts:
            print(f"보배드림 게시물 추가: {post['title'][:50]}... (조회:{post['views']}, 추천:{post['likes']}, 댓글:{post['comments']})")
        
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


class RuliwebCrawler(BaseCrawler):
    """루리웹 크롤러 (유머게시판 베스트)"""
    
    def __init__(self):
        super().__init__('ruliweb')
        self.base_url = 'https://bbs.ruliweb.com'
    
    def crawl_popular_posts(self) -> List[Dict]:
        """루리웹 유머 베스트 게시물 크롤링"""
        posts = []
        
        try:
            url = f"{self.base_url}/best/humor_only?orderby=recommend&range=24h"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 게시물 목록 파싱 (루리웹 베스트 게시판 구조)
            post_items = soup.select('tr.table_body')
            
            # 대체 선택자들 시도
            if not post_items:
                post_items = soup.select('.board_list_wrapper tr')
            if not post_items:
                post_items = soup.select('tbody tr')
            if not post_items:
                post_items = soup.select('table tr')
            
            post_list = []
            for row in post_items[:20]:  # 처음 20개만 처리하여 10개 선별
                try:
                    # 테이블 구조에서 각 셀 찾기
                    cells = row.find_all('td')
                    if len(cells) < 4:  # 충분한 셀이 없으면 스킵
                        continue
                    
                    # 제목 셀에서 링크 찾기 (보통 2번째 또는 3번째 셀)
                    title_cell = None
                    title_link = None
                    
                    for cell in cells:
                        link = cell.find('a', class_='deco')
                        if not link:
                            link = cell.find('a')
                        if link and link.get_text(strip=True) and len(link.get_text(strip=True)) > 5:
                            title_cell = cell
                            title_link = link
                            break
                    
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # 제외 단어 필터링
                    if self.should_exclude_post(title):
                        print(f"루리웹 게시물 제외: {title[:30]}...")
                        continue
                    
                    # URL 구성
                    href = title_link.get('href', '')
                    if href.startswith('/'):
                        post_url = f"https://bbs.ruliweb.com{href}"
                    elif href.startswith('http'):
                        post_url = href
                    else:
                        post_url = f"https://bbs.ruliweb.com/{href}"
                    
                    # 루리웹 테이블 구조: [분류, 제목, 작성자, 날짜, 추천, 조회]
                    # 기본값 설정
                    views = 0
                    likes = 0
                    comments = 0
                    author = '루리웹'
                    author_found = False
                    
                    # 루리웹 테이블 구조에 따른 정확한 파싱
                    # 셀[0]:ID, 셀[1]:제목, 셀[2]:작성자, 셀[3]:추천수, 셀[4]:조회수, 셀[5]:시간
                    try:
                        if len(cells) >= 6:
                            # 작성자 (셀[2])
                            nick_elem = cells[2].find('span', class_='nick')
                            if nick_elem:
                                author = nick_elem.get_text(strip=True)
                            
                            # 추천수 (셀[3])
                            likes_text = cells[3].get_text(strip=True)
                            if likes_text.isdigit():
                                likes = int(likes_text)
                            
                            # 조회수 (셀[4])
                            views_text = cells[4].get_text(strip=True)
                            if views_text.isdigit():
                                views = int(views_text)
                                
                        elif len(cells) >= 4:
                            # 셀이 적은 경우 fallback 로직
                            for i, cell in enumerate(cells):
                                cell_text = cell.get_text(strip=True)
                                
                                # 작성자 찾기
                                if i <= 2:
                                    nick_elem = cell.find('span', class_='nick')
                                    if nick_elem and not author_found:
                                        author = nick_elem.get_text(strip=True)
                                        author_found = True
                                
                                # 숫자 셀 처리 - ID 제외하고 처리
                                if cell_text.isdigit() and i > 0:  # 첫번째 셀(ID) 제외
                                    cell_num = int(cell_text)
                                    
                                    if cell_num > 1000 and views == 0:
                                        views = cell_num
                                    elif cell_num < 1000 and likes == 0:
                                        likes = cell_num
                    except Exception as e:
                        print(f"루리웹 셀 파싱 오류: {e}")
                    
                    # 작성자가 없으면 기본값
                    author_found = False
                    if not author:
                        author = '루리웹'
                    
                    # 댓글수는 제목에서 추출 시도 - 여러 패턴 시도
                    comment_patterns = [
                        r'\((\d+)\)',  # (숫자) 패턴
                        r'\[(\d+)\]',  # [숫자] 패턴  
                        r'(\d+)$'      # 끝에 숫자
                    ]
                    
                    for pattern in comment_patterns:
                        comment_match = re.search(pattern, title)
                        if comment_match:
                            comments = int(comment_match.group(1))
                            # 제목에서 댓글수 제거
                            title = re.sub(pattern, '', title).strip()
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
                    print(f"루리웹 게시물 파싱 오류: {e}")
                    continue
            
            # 인기도 순으로 정렬하고 상위 10개만 선택
            post_list.sort(key=lambda x: x['popularity_score'], reverse=True)
            posts = post_list[:10]
            
            for post in posts:
                print(f"루리웹 게시물 추가: {post['title'][:50]}... (조회:{post['views']}, 추천:{post['likes']}, 댓글:{post['comments']})")
                
        except Exception as e:
            print(f"루리웹 크롤링 오류: {e}")
        
        return posts
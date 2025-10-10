#!/usr/bin/env python3
"""
모바일 화면 크롤링을 위한 Playwright 기반 크롤러
iPhone 14 Pro 화면으로 에뮬레이션하여 실제 모바일 화면 캡처
페이지 끝까지 크롤링 및 봇 탐지 우회 강화
"""

import time
import random
from typing import List, Dict
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class MobileCrawler:
    """모바일 화면 크롤링을 위한 기본 클래스"""
    
    def __init__(self, site_name: str):
        self.site_name = site_name
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def setup_mobile_browser(self):
        """모바일 브라우저 환경 설정 (iPhone 14 Pro 에뮬레이션)"""
        try:
            print(f"📱 {self.site_name} 모바일 브라우저 설정 중...")
            
            # Playwright 초기화
            self.playwright = sync_playwright().start()
            
            # 브라우저 실행 (headless 모드)
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # iPhone 14 Pro 디바이스로 컨텍스트 생성
            self.context = self.browser.new_context(**self.playwright.devices['iPhone 14 Pro'])
            
            # 새 페이지 생성
            self.page = self.context.new_page()
            
            # 타임아웃 설정
            self.page.set_default_timeout(30000)  # 30초
            
            print(f"✅ {self.site_name} 모바일 브라우저 설정 완료")
            return True
            
        except Exception as e:
            print(f"❌ {self.site_name} 브라우저 설정 실패: {e}")
            self.cleanup()
            return False
    
    def get_mobile_page_source(self, url: str) -> str:
        """모바일 화면에서 페이지 소스 가져오기 (페이지 끝까지)"""
        if not self.setup_mobile_browser():
            return None
        
        try:
            print(f"📱 {self.site_name} 모바일 페이지 접속: {url}")
            
            # 페이지 이동
            response = self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            if response.status != 200:
                print(f"❌ {self.site_name} HTTP 상태: {response.status}")
                return None
            
            # 페이지 로딩 대기
            time.sleep(3)
            
            # 페이지 끝까지 스크롤하여 모든 콘텐츠 로드
            print(f"📜 {self.site_name} 페이지 끝까지 스크롤 중...")
            
            for i in range(15):  # 15번 스크롤
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(random.uniform(1.5, 2.5))  # 1.5~2.5초 대기
                
                # 더 이상 로드할 콘텐츠가 없는지 확인
                current_height = self.page.evaluate("document.body.scrollHeight")
                time.sleep(1)
                new_height = self.page.evaluate("document.body.scrollHeight")
                
                if current_height == new_height and i > 5:
                    print(f"📄 {self.site_name} 모든 콘텐츠 로드 완료 ({i+1}번 스크롤)")
                    break
            
            # 맨 위로 다시 스크롤
            self.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
            
            # 스크린샷 촬영 (페이지가 로드된 상태에서)
            screenshot_path = f"mobile_screenshot_{self.site_name}_{int(time.time())}.png"
            self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 {self.site_name} 모바일 스크린샷 저장: {screenshot_path}")
            
            # 페이지 소스 반환
            page_source = self.page.content()
            print(f"✅ {self.site_name} 모바일 페이지 소스 획득 완료 ({len(page_source)} 문자)")
            
            return page_source
            
        except Exception as e:
            print(f"❌ {self.site_name} 페이지 소스 획득 실패: {e}")
            return None
    
    def should_exclude_post(self, title: str) -> bool:
        """게시물 제외 여부 판단"""
        exclude_keywords = [
            '공지', '안내', '이벤트', '광고', '홍보', '스팸', 'spam', 'ad',
            '관리자', '운영진', '신고', '문의', '건의', '제보',
            '자동', 'bot', '봇', '테스트', 'test', '실험'
        ]
        
        title_lower = title.lower()
        for keyword in exclude_keywords:
            if keyword.lower() in title_lower:
                return True
        return False
    
    def cleanup(self):
        """브라우저 리소스 정리"""
        try:
            if self.page:
                self.page.close()
                self.page = None
            
            if self.context:
                self.context.close()
                self.context = None
            
            if self.browser:
                self.browser.close()
                self.browser = None
            
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            
            print(f"🔌 {self.site_name} 모바일 브라우저 정리 완료")
            
        except Exception as e:
            print(f"❌ {self.site_name} 브라우저 정리 오류: {e}")
    
    def __del__(self):
        """소멸자에서 리소스 정리"""
        self.cleanup()


class MobilePpomppuCrawler(MobileCrawler):
    """Playwright 기반 뽐뿌 모바일 크롤러"""
    
    def __init__(self):
        super().__init__('ppomppu')
        self.base_url = 'https://www.ppomppu.co.kr'
    
    def crawl_popular_posts(self) -> List[Dict]:
        """뽐뿌 모바일 화면에서 인기 게시물 크롤링 (페이지 끝까지)"""
        posts = []
        
        try:
            # 모바일 HOT 게시판 접속
            url = f"{self.base_url}/hot.php?category=2"
            
            # 모바일 페이지 소스 가져오기 (스크린샷 자동 촬영)
            page_source = self.get_mobile_page_source(url)
            if not page_source:
                return posts
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(page_source, 'html.parser')
            
            post_list = []
            seen_titles = set()
            
            # 뽐뿌 모바일 버전 게시물 파싱
            selectors = [
                'table tr td a',
                'a[href*="zboard.php"]',
                'a[href*="view.php"]',
                '.list a'
            ]
            
            print(f"📱 뽐뿌 모바일 페이지 분석 중... (페이지 크기: {len(page_source)} 문자)")
            
            for selector in selectors:
                elements = soup.select(selector)
                print(f"📱 {selector} 선택자로 {len(elements)}개 요소 발견")
                
                if len(elements) > 5:
                    # 제한 없이 모든 요소 처리 (페이지 끝까지)
                    for element in elements:
                        try:
                            title = element.get_text(strip=True)
                            if not title or len(title) < 5:
                                continue
                            
                            if title in seen_titles:
                                continue
                            
                            if self.should_exclude_post(title):
                                continue
                            
                            seen_titles.add(title)
                            
                            # URL 구성
                            href = element.get('href', '')
                            if href.startswith('/'):
                                post_url = self.base_url + href
                            elif href.startswith('http'):
                                post_url = href
                            else:
                                post_url = f"{self.base_url}/{href}"
                            
                            # 게시물인지 확인
                            if not any(pattern in href for pattern in ['zboard', 'view', 'hot']):
                                continue
                            
                            post_data = {
                                'title': title,
                                'url': post_url,
                                'site': self.site_name,
                                'category': '인기',
                                'author': '뽐뿌',
                                'views': 0,
                                'likes': 1,
                                'comments': 0,
                                'popularity_score': 1
                            }
                            
                            post_list.append(post_data)
                            
                        except Exception as e:
                            continue
                    
                    if post_list:
                        break
            
            posts = post_list
            
            if not posts:
                print(f"⚠️  뽐뿌 모바일에서 게시물을 찾지 못했습니다.")
            else:
                print(f"✅ 뽐뿌 모바일에서 {len(posts)}개 게시물 추출 완료")
            
        except Exception as e:
            print(f"❌ 뽐뿌 모바일 크롤링 오류: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
        
        return posts


class MobileBobaeCrawler(MobileCrawler):
    """Playwright 기반 보배드림 모바일 크롤러"""
    
    def __init__(self):
        super().__init__('bobae')
        self.base_url = 'https://www.bobaedream.co.kr'
    
    def crawl_popular_posts(self) -> List[Dict]:
        """보배드림 모바일 화면에서 인기 게시물 크롤링 (페이지 끝까지)"""
        posts = []
        
        try:
            # 모바일 베스트 게시판 접속
            url = f"{self.base_url}/board/bulletin/list.php?code=best&vdate=w"
            
            # 모바일 페이지 소스 가져오기 (스크린샷 자동 촬영)
            page_source = self.get_mobile_page_source(url)
            if not page_source:
                return posts
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(page_source, 'html.parser')
            
            post_list = []
            seen_titles = set()
            
            # 보배드림 모바일 버전 게시물 파싱
            selectors = [
                'table tr td a',
                'a[href*="view"]',
                '.list a',
                'div[class*="list"] a'
            ]
            
            print(f"📱 보배드림 모바일 페이지 분석 중... (페이지 크기: {len(page_source)} 문자)")
            
            for selector in selectors:
                elements = soup.select(selector)
                print(f"📱 {selector} 선택자로 {len(elements)}개 요소 발견")
                
                if len(elements) > 5:
                    # 제한 없이 모든 요소 처리 (페이지 끝까지)
                    for element in elements:
                        try:
                            title = element.get_text(strip=True)
                            if not title or len(title) < 5:
                                continue
                            
                            if title in seen_titles:
                                continue
                            
                            if self.should_exclude_post(title):
                                continue
                            
                            seen_titles.add(title)
                            
                            # URL 구성
                            href = element.get('href', '')
                            if href.startswith('/'):
                                post_url = self.base_url + href
                            elif href.startswith('http'):
                                post_url = href
                            else:
                                post_url = f"{self.base_url}/{href}"
                            
                            # 게시물인지 확인
                            if not any(pattern in href for pattern in ['view', 'read', 'best']):
                                continue
                            
                            post_data = {
                                'title': title,
                                'url': post_url,
                                'site': self.site_name,
                                'category': '인기',
                                'author': '보배드림',
                                'views': 0,
                                'likes': 1,
                                'comments': 0,
                                'popularity_score': 1
                            }
                            
                            post_list.append(post_data)
                            
                        except Exception as e:
                            continue
                    
                    if post_list:
                        break
            
            posts = post_list
            
            if not posts:
                print(f"⚠️  보배드림 모바일에서 게시물을 찾지 못했습니다.")
            else:
                print(f"✅ 보배드림 모바일에서 {len(posts)}개 게시물 추출 완료")
            
        except Exception as e:
            print(f"❌ 보배드림 모바일 크롤링 오류: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
        
        return posts


class MobileDcinsideCrawler(MobileCrawler):
    """Playwright 기반 디시인사이드 모바일 크롤러 (툴팁 제거 강화)"""
    
    def __init__(self):
        super().__init__('dcinside')
        self.base_url = 'https://gall.dcinside.com'
    
    def crawl_popular_posts(self) -> List[Dict]:
        """디시인사이드 모바일 화면에서 인기 게시물 크롤링 (툴팁 제거 + 페이지 끝까지)"""
        posts = []
        
        try:
            # 모바일 실시간 베스트 게시판 접속
            url = f"{self.base_url}/board/lists/?id=dcbest"
            
            # 툴팁 제거가 포함된 페이지 소스 가져오기
            page_source = self.get_mobile_page_source_with_tooltip_removal(url)
            if not page_source:
                return posts
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(page_source, 'html.parser')
            
            post_list = []
            seen_titles = set()
            
            # 디시인사이드 모바일 버전 게시물 파싱
            selectors = [
                'tr.ub-content a',
                '.gall_tit a',
                'a[href*="view"]',
                'td a'
            ]
            
            print(f"📱 디시인사이드 모바일 페이지 분석 중... (페이지 크기: {len(page_source)} 문자)")
            
            for selector in selectors:
                elements = soup.select(selector)
                print(f"📱 {selector} 선택자로 {len(elements)}개 요소 발견")
                
                if len(elements) > 5:
                    # 제한 없이 모든 요소 처리 (페이지 끝까지)
                    for element in elements:
                        try:
                            title = element.get_text(strip=True)
                            if not title or len(title) < 5:
                                continue
                            
                            if title in seen_titles:
                                continue
                            
                            if self.should_exclude_post(title):
                                continue
                            
                            seen_titles.add(title)
                            
                            # URL 구성
                            href = element.get('href', '')
                            if href.startswith('/'):
                                post_url = self.base_url + href
                            elif href.startswith('http'):
                                post_url = href
                            else:
                                post_url = f"{self.base_url}/{href}"
                            
                            # 게시물인지 확인
                            if not any(pattern in href for pattern in ['view', 'board']):
                                continue
                            
                            post_data = {
                                'title': title,
                                'url': post_url,
                                'site': self.site_name,
                                'category': '인기',
                                'author': '디시',
                                'views': 0,
                                'likes': 1,
                                'comments': 0,
                                'popularity_score': 1
                            }
                            
                            post_list.append(post_data)
                            
                        except Exception as e:
                            continue
                    
                    if post_list:
                        break
            
            posts = post_list
            
            if not posts:
                print(f"⚠️  디시인사이드 모바일에서 게시물을 찾지 못했습니다.")
            else:
                print(f"✅ 디시인사이드 모바일에서 {len(posts)}개 게시물 추출 완료")
            
        except Exception as e:
            print(f"❌ 디시인사이드 모바일 크롤링 오류: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
        
        return posts
    
    def get_mobile_page_source_with_tooltip_removal(self, url: str) -> str:
        """툴팁 제거가 포함된 페이지 소스 가져오기"""
        if not self.setup_mobile_browser():
            return None
        
        try:
            print(f"🌐 {self.site_name} 페이지 접속 중...")
            response = self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            if response.status != 200:
                print(f"❌ {self.site_name} HTTP 상태: {response.status}")
                return None
            
            # 툴팁 제거를 위한 마우스 오버 시뮬레이션
            print(f"🖱️ {self.site_name} 툴팁 제거 중...")
            
            try:
                # 이미지 순서 툴팁들을 찾아서 마우스 오버
                tooltip_selectors = [
                    '.list_img img',  # 게시물 이미지
                    '.thumb img',     # 썸네일 이미지
                    'img[alt*="순서"]', # 순서 관련 이미지
                    '.gall_list img'  # 갤러리 리스트 이미지
                ]
                
                for selector in tooltip_selectors:
                    try:
                        elements = self.page.query_selector_all(selector)
                        for i, element in enumerate(elements[:10]):  # 처음 10개만
                            try:
                                # 마우스 오버로 툴팁 제거
                                element.hover()
                                self.page.wait_for_timeout(200)  # 0.2초 대기
                            except:
                                continue
                    except:
                        continue
                
                print(f"✅ {self.site_name} 툴팁 제거 완료")
                
            except Exception as e:
                print(f"⚠️ {self.site_name} 툴팁 제거 중 오류 (계속 진행): {str(e)}")
            
            # 페이지 끝까지 스크롤 (모든 콘텐츠 로드)
            print(f"📜 {self.site_name} 페이지 끝까지 스크롤 중...")
            
            # 여러 번 스크롤해서 모든 게시물 로드
            for i in range(15):  # 15번 스크롤
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(random.uniform(1.5, 2.5))  # 1.5~2.5초 대기
                
                # 더 이상 로드할 콘텐츠가 없는지 확인
                current_height = self.page.evaluate("document.body.scrollHeight")
                time.sleep(1)
                new_height = self.page.evaluate("document.body.scrollHeight")
                
                if current_height == new_height and i > 5:
                    print(f"📄 {self.site_name} 모든 콘텐츠 로드 완료 ({i+1}번 스크롤)")
                    break
            
            # 맨 위로 다시 스크롤
            self.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
            
            # 스크린샷 촬영
            screenshot_path = f"mobile_screenshot_{self.site_name}_{int(time.time())}.png"
            self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 {self.site_name} 스크린샷 저장: {screenshot_path}")
            
            # 페이지 소스 가져오기
            page_source = self.page.content()
            print(f"✅ {self.site_name} 페이지 소스 획득 ({len(page_source)}자)")
            
            return page_source
            
        except Exception as e:
            print(f"❌ {self.site_name} 페이지 소스 가져오기 실패: {str(e)}")
            return None


class MobileFmkoreaCrawler(MobileCrawler):
    """Playwright 기반 에펨코리아 모바일 크롤러 (봇 탐지 우회 강화)"""
    
    def __init__(self):
        super().__init__('fmkorea')
        self.base_url = 'https://www.fmkorea.com'
    
    def crawl_popular_posts(self) -> List[Dict]:
        """에펨코리아 모바일 화면에서 인기 게시물 크롤링 (봇 탐지 우회 + 페이지 끝까지)"""
        posts = []
        
        try:
            # 모바일 베스트 게시판 접속 (봇 탐지 우회 강화)
            url = f"{self.base_url}/best"
            
            # 봇 탐지 우회가 강화된 페이지 소스 가져오기
            page_source = self.get_mobile_page_source_with_antibot(url)
            if not page_source:
                return posts
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(page_source, 'html.parser')
            
            post_list = []
            seen_titles = set()
            
            # 에펨코리아 모바일 버전 게시물 파싱
            selectors = [
                'a.hx',
                'a[href*="/best/"]',
                '.li.li_best a',
                'a[href*="document_srl"]',
                '.title a',
                '.bd_lst a',
                'li a'
            ]
            
            print(f"📱 에펨코리아 모바일 페이지 분석 중... (페이지 크기: {len(page_source)} 문자)")
            
            for selector in selectors:
                elements = soup.select(selector)
                print(f"📱 {selector} 선택자로 {len(elements)}개 요소 발견")
                
                if len(elements) > 5:
                    # 제한 없이 모든 요소 처리 (페이지 끝까지)
                    for element in elements:
                        try:
                            title = element.get_text(strip=True)
                            if not title or len(title) < 5:
                                continue
                            
                            if title in seen_titles:
                                continue
                            
                            if self.should_exclude_post(title):
                                continue
                            
                            seen_titles.add(title)
                            
                            # URL 구성
                            href = element.get('href', '')
                            if href.startswith('/'):
                                post_url = self.base_url + href
                            elif href.startswith('http'):
                                post_url = href
                            else:
                                post_url = f"{self.base_url}/{href}"
                            
                            # 게시물인지 확인
                            if not any(pattern in href for pattern in ['best', 'document_srl', 'free']):
                                continue
                            
                            post_data = {
                                'title': title,
                                'url': post_url,
                                'site': self.site_name,
                                'category': '인기',
                                'author': '에펨코리아',
                                'views': 0,
                                'likes': 1,
                                'comments': 0,
                                'popularity_score': 1
                            }
                            
                            post_list.append(post_data)
                            
                        except Exception as e:
                            continue
                    
                    if post_list:
                        break
            
            posts = post_list
            
            if not posts:
                print(f"⚠️  에펨코리아 모바일에서 게시물을 찾지 못했습니다.")
            else:
                print(f"✅ 에펨코리아 모바일에서 {len(posts)}개 게시물 추출 완료")
            
        except Exception as e:
            print(f"❌ 에펨코리아 모바일 크롤링 오류: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
        
        return posts
    
    def get_mobile_page_source_with_antibot(self, url: str) -> str:
        """봇 탐지 우회가 강화된 페이지 소스 가져오기"""
        if not self.setup_mobile_browser():
            return None
        
        try:
            # 봇 탐지 우회를 위한 추가 헤더 설정
            self.page.set_extra_http_headers({
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Upgrade-Insecure-Requests': '1'
            })
            
            print(f"🌐 {self.site_name} 페이지 접속 중... (봇 탐지 우회 모드)")
            
            # 천천히 페이지 로드
            response = self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            if response.status != 200:
                print(f"❌ {self.site_name} HTTP 상태: {response.status}")
                return None
            
            # 사람처럼 행동하기
            print(f"🤖 {self.site_name} 사람처럼 행동 시뮬레이션...")
            
            # 랜덤 마우스 움직임
            for _ in range(5):
                x = random.randint(100, 300)
                y = random.randint(100, 400)
                self.page.mouse.move(x, y)
                time.sleep(random.uniform(0.5, 1.5))
            
            # 천천히 스크롤
            for i in range(5):
                self.page.evaluate(f"window.scrollTo(0, {i * 200})")
                time.sleep(random.uniform(2, 4))
            
            # 페이지 끝까지 스크롤 (모든 콘텐츠 로드)
            print(f"📜 {self.site_name} 페이지 끝까지 스크롤 중...")
            
            for i in range(15):  # 15번 스크롤
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(random.uniform(2, 4))  # 2~4초 대기
                
                # 더 이상 로드할 콘텐츠가 없는지 확인
                current_height = self.page.evaluate("document.body.scrollHeight")
                time.sleep(1)
                new_height = self.page.evaluate("document.body.scrollHeight")
                
                if current_height == new_height and i > 5:
                    print(f"📄 {self.site_name} 모든 콘텐츠 로드 완료 ({i+1}번 스크롤)")
                    break
            
            # 맨 위로 돌아가기
            self.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
            
            # 스크린샷 촬영
            screenshot_path = f"mobile_screenshot_{self.site_name}_{int(time.time())}.png"
            self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 {self.site_name} 모바일 스크린샷 저장: {screenshot_path}")
            
            # 페이지 소스 가져오기
            page_source = self.page.content()
            print(f"✅ {self.site_name} 페이지 소스 획득 ({len(page_source)}자)")
            
            return page_source
            
        except Exception as e:
            print(f"❌ {self.site_name} 봇 탐지 우회 실패: {str(e)}")
            return None
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모바일 커뮤니티 게시물 캡처 스크립트
Playwright를 사용하여 각 사이트별 상위 2개 게시물을 모바일 화면으로 캡처
"""

import sys
import os
import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import time

# 앱 모듈을 위한 path 추가
sys.path.append('.')
from app import create_app
from app.models import Post

class CommunityScreenshotCapture:
    def __init__(self):
        self.base_dir = Path("capture")
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.capture_dir = self.base_dir / self.today
        
        # 캡처 디렉토리 생성
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        
        # 사이트별 설정
        self.site_configs = {
            'ppomppu': {
                'name': '뽐뿌',
                'wait_selectors': ['.view_contents', '.comment', 'img'],
                'scroll_delay': 2,
                'has_mobile_popup': True  # 모바일 웹 팝업 있음
            },
            'fmkorea': {
                'name': '에펨코리아',
                'wait_selectors': ['.xe_content', '.fdb_lst', 'img'],
                'scroll_delay': 3
            },
            'bobae': {
                'name': '보배드림',
                'wait_selectors': ['.bodys', '.comment', 'img'],
                'scroll_delay': 2
            },
            'dcinside': {
                'name': '디시인사이드',
                'wait_selectors': ['.writing_view_box', '.comment_box', 'img'],
                'scroll_delay': 2
            }
        }
    
    async def capture_post(self, browser, post, site_config):
        """단일 게시물 캡처 - 갤럭시 S25 사이즈로 분할 캡처"""
        try:
            # 갤럭시 S25 화면 설정으로 새 페이지 생성 - 고해상도
            context = await browser.new_context(
                viewport={'width': 412, 'height': 915},  # 갤럭시 S25 크기 (412x915)
                device_scale_factor=3.0,  # 3배 해상도로 선명도 향상
                user_agent='Mozilla/5.0 (Linux; Android 14; SM-S926B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
            )
            
            page = await context.new_page()
            
            print(f"📱 캡처 시작: {post.title[:50]}...")
            
            # 페이지 이동
            await page.goto(post.url, wait_until='networkidle', timeout=30000)
            
            # 페이지 로딩 대기
            await asyncio.sleep(2)
            
            # 뽐뿌 모바일 팝업 처리
            if site_config.get('has_mobile_popup', False):
                await self.handle_ppomppu_mobile_popup(page)
                
            # 팝업 처리 후 추가 로딩 대기
            await asyncio.sleep(1)
            
            # 주요 요소 로딩 대기
            for selector in site_config['wait_selectors']:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                except:
                    continue  # 일부 요소가 없어도 계속 진행
            
            # 고품질 렌더링을 위한 CSS 주입
            await page.add_style_tag(content="""
                * {
                    -webkit-font-smoothing: antialiased !important;
                    -moz-osx-font-smoothing: grayscale !important;
                    text-rendering: optimizeLegibility !important;
                }
                img {
                    image-rendering: -webkit-optimize-contrast !important;
                    image-rendering: crisp-edges !important;
                }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Malgun Gothic', sans-serif !important;
                }
            """)
            
            # 댓글까지 스크롤하여 모든 컨텐츠 로드
            await self.scroll_to_load_content(page, site_config['scroll_delay'])
            
            # 파일명 생성 (안전한 파일명으로 변경)
            safe_title = "".join(c for c in post.title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            
            # 갤럭시 S25 사이즈로 분할 캡처
            captured_files = await self.capture_in_segments(page, post, safe_title)
            
            await context.close()
            return captured_files
            
        except Exception as e:
            print(f"❌ 캡처 실패 - {post.title[:30]}: {str(e)}")
            if 'context' in locals():
                await context.close()
            return None
    
    async def capture_in_segments(self, page, post, safe_title):
        """갤럭시 S25 사이즈에 맞게 페이지를 여러 구간으로 나누어 캡처"""
        try:
            # 전체 페이지 높이 확인
            total_height = await page.evaluate('document.body.scrollHeight')
            viewport_height = 915  # 갤럭시 S25 높이
            
            # 캡처할 구간 수 계산
            segments = max(1, (total_height + viewport_height - 1) // viewport_height)
            
            print(f"  📏 전체 높이: {total_height}px, {segments}개 구간으로 분할")
            
            captured_files = []
            
            for i in range(segments):
                # 스크롤 위치 계산
                scroll_y = i * viewport_height
                
                # 스크롤
                await page.evaluate(f'window.scrollTo(0, {scroll_y})')
                await asyncio.sleep(0.8)  # 스크롤 안정화 대기
                
                # 파일명 생성
                if segments == 1:
                    filename = f"{post.site}_{post.id}_{safe_title}.png"
                else:
                    filename = f"{post.site}_{post.id}_{safe_title}_part{i+1:02d}.png"
                
                filepath = self.capture_dir / filename
                
                # 고품질 스크린샷 캡처 (full_page=False)
                await page.screenshot(
                    path=str(filepath),
                    full_page=False,  # 현재 뷰포트만 캡처
                    type='png',
                    scale='device'  # 디바이스 스케일 팩터 적용
                )
                
                captured_files.append(str(filepath))
                print(f"  ✅ 구간 {i+1}/{segments} 캡처: {filename}")
            
            return captured_files
            
        except Exception as e:
            print(f"❌ 분할 캡처 실패: {e}")
            return []
    
    async def handle_ppomppu_mobile_popup(self, page):
        """뽐뿌 사이트의 모바일 웹 팝업 처리"""
        try:
            print("  📱 뽐뿌 모바일 팝업 확인 중...")
            
            # 모바일 웹으로 보기 버튼 찾기 (다양한 셀렉터 시도)
            mobile_button_selectors = [
                'a[href*="mobile"]',  # 모바일 링크
                '.mobile_btn',        # 모바일 버튼 클래스
                'button:has-text("모바일")',  # 모바일 텍스트 포함 버튼
                'a:has-text("모바일웹")',      # 모바일웹 텍스트 포함 링크
                'a:has-text("불편해도")',      # 불편해도 텍스트 포함 링크
                '.popup a',           # 팝업 내의 링크
                '.modal a'            # 모달 내의 링크
            ]
            
            for selector in mobile_button_selectors:
                try:
                    # 버튼이 존재하고 보이는지 확인
                    element = await page.wait_for_selector(selector, timeout=3000)
                    if element and await element.is_visible():
                        print(f"  ✅ 모바일 버튼 발견: {selector}")
                        await element.click()
                        print("  🔘 모바일 웹으로 보기 버튼 클릭 완료")
                        await asyncio.sleep(2)  # 페이지 로딩 대기
                        break
                except:
                    continue
            
            # 팝업 닫기 버튼도 시도
            close_selectors = [
                '.close',
                '.popup_close', 
                '.modal_close',
                '[class*="close"]',
                'button:has-text("닫기")',
                'a:has-text("닫기")'
            ]
            
            for selector in close_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=1000)
                    if element and await element.is_visible():
                        await element.click()
                        print("  ❌ 팝업 닫기 버튼 클릭")
                        await asyncio.sleep(1)
                        break
                except:
                    continue
            
            # JavaScript로 강제 팝업 제거 (최후 수단)
            await page.evaluate("""
                // 모든 팝업 관련 요소 제거
                const popupSelectors = ['.popup', '.modal', '.layer', '.overlay', '[class*="popup"]', '[id*="popup"]'];
                popupSelectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        if (el.style.display !== 'none' && el.offsetParent !== null) {
                            el.style.display = 'none';
                            el.remove();
                        }
                    });
                });
                
                // body 스타일 정상화 (팝업으로 인한 스크롤 방지 해제)
                document.body.style.overflow = 'auto';
                document.documentElement.style.overflow = 'auto';
            """)
                    
            print("  ✅ 뽐뿌 팝업 처리 완료")
            
        except Exception as e:
            print(f"  ⚠️ 뽐뿌 팝업 처리 중 오류 (계속 진행): {e}")
    
    async def scroll_to_load_content(self, page, delay=2):
        """페이지를 스크롤하여 댓글 등 동적 컨텐츠 로드"""
        try:
            # 페이지 높이 확인
            page_height = await page.evaluate('document.body.scrollHeight')
            viewport_height = await page.evaluate('window.innerHeight')
            
            # 스크롤하여 컨텐츠 로드
            scroll_position = 0
            while scroll_position < page_height:
                scroll_position += viewport_height * 0.8
                await page.evaluate(f'window.scrollTo(0, {scroll_position})')
                await asyncio.sleep(0.5)
            
            # 맨 아래까지 스크롤
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(delay)
            
            # 다시 맨 위로 스크롤 (전체 캡처를 위해)
            await page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"⚠️ 스크롤 중 오류: {e}")
    
    async def get_top_posts(self):
        """각 사이트별 랜덤 5개 게시물 조회"""
        import random
        app = create_app()
        posts_by_site = {}
        
        with app.app_context():
            for site in ['bobae', 'dcinside', 'ppomppu', 'fmkorea']:
                # 전체 게시물 중에서 랜덤 선택
                all_posts = Post.query.filter(Post.site == site).all()
                
                if len(all_posts) > 5:
                    # 5개 이상 있으면 랜덤으로 5개 선택
                    posts = random.sample(all_posts, 5)
                else:
                    # 5개 미만이면 모든 게시물 선택
                    posts = all_posts
                
                posts_by_site[site] = posts
                print(f"📋 {self.site_configs[site]['name']}: {len(posts)}개 게시물 (랜덤 선택)")
        
        return posts_by_site
    
    async def capture_all_posts(self):
        """모든 게시물 캡처 실행"""
        print(f"🚀 모바일 캡처 시작 - {self.today}")
        print(f"📁 저장 경로: {self.capture_dir}")
        
        # 게시물 데이터 가져오기
        posts_by_site = await self.get_top_posts()
        
        async with async_playwright() as playwright:
            # Chromium 브라우저 실행 - 고품질 렌더링 옵션
            browser = await playwright.chromium.launch(
                headless=True,  # 백그라운드 실행
                args=[
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--high-dpi-support=1',  # 고DPI 지원
                    '--disable-web-security',  # 웹 보안 비활성화 (캡처 품질 향상)
                    '--font-render-hinting=none',  # 폰트 렌더링 최적화
                    '--disable-gpu-sandbox'
                ]
            )
            
            captured_files = []
            total_posts = sum(len(posts) for posts in posts_by_site.values())
            current_count = 0
            
            try:
                # 사이트별로 순차 캡처
                for site, posts in posts_by_site.items():
                    site_config = self.site_configs[site]
                    print(f"\n🔥 {site_config['name']} 캡처 시작")
                    
                    for i, post in enumerate(posts, 1):
                        current_count += 1
                        print(f"[{current_count}/{total_posts}] ", end="")
                        
                        post_files = await self.capture_post(browser, post, site_config)
                        if post_files:
                            if isinstance(post_files, list):
                                captured_files.extend(post_files)
                                print(f"  📁 {len(post_files)}개 파일 생성")
                            else:
                                captured_files.append(post_files)
                        
                        # 사이트 부하 방지를 위한 딜레이
                        if i < len(posts):
                            await asyncio.sleep(2)
                
                print(f"\n✅ 고해상도 갤럭시 S25 분할 캡처 완료!")
                print(f"📊 총 {len(captured_files)}개 파일 생성 (갤럭시 S25: 412x915 @ 3x DPI)")
                print(f"📁 저장 위치: {self.capture_dir}")
                
                return captured_files
                
            except Exception as e:
                print(f"❌ 캡처 중 오류: {e}")
                return captured_files
                
            finally:
                await browser.close()

async def main():
    """메인 실행 함수"""
    capture = CommunityScreenshotCapture()
    captured_files = await capture.capture_all_posts()
    
    if captured_files:
        print("\n📸 생성된 캡처 파일들:")
        for filepath in captured_files:
            print(f"  - {Path(filepath).name}")
    else:
        print("❌ 캡처된 파일이 없습니다.")

if __name__ == "__main__":
    asyncio.run(main())
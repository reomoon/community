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
        
        # 사이트별 설정 - 뽐뿌 제외, 속도 최적화
        self.site_configs = {
            'fmkorea': {
                'name': '에펨코리아',
                'wait_selectors': ['.xe_content'],  # 필수 요소만
                'scroll_delay': 1  # 3초 → 1초
            },
            'bobae': {
                'name': '보배드림',
                'wait_selectors': ['.bodys'],  # 필수 요소만
                'scroll_delay': 1  # 2초 → 1초
            },
            'dcinside': {
                'name': '디시인사이드',
                'wait_selectors': ['.writing_view_box'],  # 필수 요소만
                'scroll_delay': 1  # 2초 → 1초
            }
        }
    
    async def capture_post(self, browser, post, site_config, playwright_instance=None):
        """단일 게시물 캡처 - 갤럭시 모바일 환경으로 캡처"""
        try:
            print(f"📱 캡처 시작: {post.site} - {post.title[:50]}...")
            
            # 갤럭시 S9+ 모바일 환경 시뮬레이션 (내장 디바이스 사용)
            from playwright.async_api import async_playwright
            
            # 갤럭시 S9+ 디바이스 설정을 수동으로 정의
            mobile_device = {
                'viewport': {'width': 412, 'height': 846},
                'device_scale_factor': 2.6,
                'is_mobile': True,
                'has_touch': True,
                'user_agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
            }
            
            context = await browser.new_context(
                **mobile_device,  # 모바일 디바이스 설정 적용
                locale='ko-KR',
                timezone_id='Asia/Seoul',
                extra_http_headers={
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
                }
            )
            
            page = await context.new_page()
            
            print(f"  🌐 페이지 이동 중: {post.url}")
            
            # 페이지 이동 (더 안정적인 방법)
            try:
                # 먼저 빠른 로딩 시도
                await page.goto(post.url, wait_until='domcontentloaded', timeout=20000)
                print(f"  ✅ 페이지 로딩 완료: {post.site}")
            except Exception as e1:
                print(f"  ⚠️ 첫 번째 시도 실패, 재시도: {post.site}")
                try:
                    # 두 번째 시도: 더 관대한 조건
                    await page.goto(post.url, wait_until='load', timeout=30000)
                    print(f"  ✅ 페이지 로딩 완료 (재시도): {post.site}")
                except Exception as e2:
                    print(f"  ⚠️ 페이지 로딩 지연, 계속 진행: {post.site}")
                    # 타임아웃이어도 페이지가 부분적으로 로딩되었을 수 있으므로 계속 진행
            
            # 페이지 인코딩 및 폰트 강제 설정
            await page.evaluate("""
                // 페이지 인코딩 UTF-8로 강제 설정
                if (document.querySelector('meta[charset]')) {
                    document.querySelector('meta[charset]').setAttribute('charset', 'UTF-8');
                } else {
                    var meta = document.createElement('meta');
                    meta.setAttribute('charset', 'UTF-8');
                    document.head.appendChild(meta);
                }
                
                // 웹폰트 로드
                const link = document.createElement('link');
                link.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap';
                link.rel = 'stylesheet';
                document.head.appendChild(link);
                
                // 폰트 강제 적용
                const applyFont = () => {
                    const elements = document.querySelectorAll('*');
                    elements.forEach(el => {
                        if (el.style) {
                            el.style.fontFamily = 'Noto Sans KR, Malgun Gothic, 맑은 고딕, Apple SD Gothic Neo, sans-serif';
                        }
                    });
                };
                
                // 즉시 적용
                applyFont();
                
                // 폰트 로드 후 다시 적용
                setTimeout(applyFont, 2000);
            """)
            
            # 추가 로딩 대기
            await asyncio.sleep(2)
            
            # 주요 요소 로딩 대기 (선택적)
            print(f"  🔍 요소 대기 중: {site_config['wait_selectors']}")
            element_found = False
            for selector in site_config['wait_selectors']:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    print(f"    ✅ 요소 발견: {selector}")
                    element_found = True
                    break  # 하나라도 찾으면 충분
                except Exception as e:
                    print(f"    ⚠️ 요소 없음: {selector}")
                    continue
            
            if not element_found:
                print(f"    ℹ️ 주요 요소 없지만 계속 진행: {post.site}")
            
            # 한글 폰트 강제 적용을 위한 CSS 주입
            await page.add_style_tag(content="""
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
                
                * {
                    font-family: 'Noto Sans KR', 'Malgun Gothic', '맑은 고딕', 'Apple SD Gothic Neo', sans-serif !important;
                    -webkit-font-smoothing: antialiased !important;
                    -moz-osx-font-smoothing: grayscale !important;
                    text-rendering: optimizeLegibility !important;
                }
                
                body, div, span, p, h1, h2, h3, h4, h5, h6, a, td, th {
                    font-family: 'Noto Sans KR', '맑은 고딕', 'Malgun Gothic' !important;
                    font-weight: 400 !important;
                }
                
                img {
                    image-rendering: -webkit-optimize-contrast !important;
                    image-rendering: crisp-edges !important;
                }
            """)
            
            # 댓글까지 스크롤하여 모든 컨텐츠 로드
            print(f"  📜 페이지 스크롤 시작: {post.site}")
            await self.scroll_to_load_content(page, site_config['scroll_delay'])
            print(f"  ✅ 스크롤 완료: {post.site}")
            
            # 파일명 생성 (한글 인코딩 안전 처리)
            try:
                # 한글을 영문으로 변환하거나 제거
                import re
                # 한글과 특수문자 제거, 영문/숫자만 남김
                safe_title = re.sub(r'[^\w\s-]', '', post.title.encode('ascii', errors='ignore').decode('ascii'))
                safe_title = re.sub(r'[-\s]+', '_', safe_title).strip('_')[:30]
                
                # 빈 문자열이면 기본값 사용
                if not safe_title:
                    safe_title = f"{post.site}_{post.id if hasattr(post, 'id') else 'post'}"
                    
                print(f"  📄 파일명 생성: {safe_title}")
            except Exception as e:
                # 인코딩 오류 시 기본 파일명 사용
                safe_title = f"{post.site}_{datetime.now().strftime('%H%M%S')}"
                print(f"  ⚠️ 파일명 인코딩 오류, 기본명 사용: {safe_title}")
            
            # 갤럭시 S25 사이즈로 분할 캡처
            print(f"  📸 캡처 시작: {post.site}")
            captured_files = await self.capture_in_segments(page, post, safe_title)
            print(f"  ✅ 캡처 완료: {post.site} - {len(captured_files) if captured_files else 0}개 파일")
            
            await context.close()
            return captured_files
            
        except Exception as e:
            print(f"❌ 캡처 실패 - {post.site} - {post.title[:30]}")
            print(f"    오류 상세: {str(e)}")
            print(f"    URL: {post.url}")
            import traceback
            print(f"    스택 트레이스: {traceback.format_exc()}")
            
            if 'context' in locals():
                try:
                    await context.close()
                except:
                    pass
            return None
    
    async def capture_in_segments(self, page, post, safe_title):
        """갤럭시 S25 사이즈에 맞게 페이지를 여러 구간으로 나누어 캡처 (최대 10개 제한)"""
        try:
            # 전체 페이지 높이 확인
            total_height = await page.evaluate('document.body.scrollHeight')
            viewport_height = 915  # 갤럭시 S25 높이
            
            # 캡처할 구간 수 계산 (최대 10개로 제한)
            segments = max(1, min(10, (total_height + viewport_height - 1) // viewport_height))
            
            print(f"  📏 전체 높이: {total_height}px, {segments}개 구간으로 분할 (최대 10개 제한)")
            
            captured_files = []
            
            for i in range(segments):
                # 스크롤 위치 계산
                scroll_y = i * viewport_height
                
                # 스크롤
                await page.evaluate(f'window.scrollTo(0, {scroll_y})')
                await asyncio.sleep(0.4)  # 0.8초 → 0.4초
                
                # 파일명 생성
                if segments == 1:
                    filename = f"{post.site}_{post.id}_{safe_title}.png"
                else:
                    filename = f"{post.site}_{post.id}_{safe_title}_part{i+1:02d}.png"
                
                filepath = self.capture_dir / filename
                
                # 디시인사이드는 하단 136px 잘라서 캡처
                if post.site == 'dcinside':
                    # 디시인사이드: 하단 136px 제외하고 캡처
                    crop_height = viewport_height - 136  # 915 - 136 = 779px
                    await page.screenshot(
                        path=str(filepath),
                        full_page=False,
                        type='png',
                        scale='device',
                        clip={'x': 0, 'y': 0, 'width': 412, 'height': crop_height}  # 하단 136px 자르기
                    )
                else:
                    # 다른 사이트: 일반 캡처
                    await page.screenshot(
                        path=str(filepath),
                        full_page=False,
                        type='png',
                        scale='device'
                    )
                
                captured_files.append(str(filepath))
                print(f"  ✅ 구간 {i+1}/{segments} 캡처: {filename}")
            
            return captured_files
            
        except Exception as e:
            print(f"❌ 분할 캡처 실패: {e}")
            return []
    
    async def handle_ppomppu_mobile_popup(self, page):
        """뽐뿌 사이트의 모바일 웹 팝업 처리 - 강화 버전"""
        try:
            print("  📱 뽐뿌 모바일 팝업 처리 시작...")
            
            # 1. 즉시 JavaScript로 팝업 제거 (선제 공격)
            await page.evaluate("""
                // 모든 팝업 관련 요소 즉시 제거
                const removePopups = () => {
                    const popupSelectors = [
                        '.popup', '.modal', '.layer', '.overlay', '.dimmed',
                        '[class*="popup"]', '[id*="popup"]', '[class*="modal"]', '[id*="modal"]',
                        '.layer_popup', '.modal_popup', '.app_popup', '.mobile_popup'
                    ];
                    
                    popupSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            if (el.offsetParent !== null) {
                                el.style.display = 'none';
                                el.remove();
                            }
                        });
                    });
                    
                    // body 스타일 정상화
                    document.body.style.overflow = 'auto';
                    document.documentElement.style.overflow = 'auto';
                    document.body.style.position = 'static';
                };
                
                // 즉시 실행
                removePopups();
                
                // 주기적으로 실행 (팝업이 지연 로딩될 수 있음)
                setInterval(removePopups, 500);
            """)
            
            # 2. 모바일 웹으로 보기 버튼 찾기 (확장된 셀렉터)
            mobile_button_selectors = [
                'a[href*="mobile"]', 'a[href*="m.ppomppu"]',
                '.mobile_btn', '.btn_mobile', 
                'button:has-text("모바일")', 'a:has-text("모바일웹")', 
                'a:has-text("모바일로")', 'a:has-text("모바일 보기")',
                'a:has-text("불편해도")', 'button:has-text("불편해도")',
                '.popup a', '.modal a', '.layer a',
                '[onclick*="mobile"]', '[onclick*="m.ppomppu"]'
            ]
            
            for selector in mobile_button_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=1000)
                    if element and await element.is_visible():
                        text = await element.text_content()
                        print(f"  ✅ 모바일 버튼 발견: {selector} - '{text}'")
                        await element.click()
                        print("  🔘 모바일 웹으로 보기 버튼 클릭 완료")
                        await asyncio.sleep(1)
                        break
                except:
                    continue
            
            # 3. 팝업 닫기 버튼 시도 (확장된 셀렉터)
            close_selectors = [
                '.close', '.btn_close', '.popup_close', '.modal_close', '.layer_close',
                '[class*="close"]', '[id*="close"]',
                'button:has-text("닫기")', 'a:has-text("닫기")', 'span:has-text("닫기")',
                'button:has-text("×")', 'a:has-text("×")', 'span:has-text("×")',
                'button:has-text("X")', 'a:has-text("X")', '.btn_x', '.close_x'
            ]
            
            for selector in close_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=500)
                    if element and await element.is_visible():
                        await element.click()
                        print(f"  ❌ 팝업 닫기 버튼 클릭: {selector}")
                        await asyncio.sleep(0.5)
                        break
                except:
                    continue
            
            # 4. 최종 강제 팝업 제거 + ESC 키 시도
            await page.evaluate("""
                // 최종 팝업 제거
                const finalRemovePopups = () => {
                    // 모든 가능한 팝업 요소 제거
                    const allElements = document.querySelectorAll('*');
                    allElements.forEach(el => {
                        const style = window.getComputedStyle(el);
                        // z-index가 높거나 fixed/absolute 포지션인 요소 중 팝업 의심 요소 제거
                        if ((style.position === 'fixed' || style.position === 'absolute') && 
                            (parseInt(style.zIndex) > 100 || style.zIndex === 'auto')) {
                            const rect = el.getBoundingClientRect();
                            // 화면을 덮는 크기의 요소는 팝업일 가능성이 높음
                            if (rect.width > window.innerWidth * 0.8 || rect.height > window.innerHeight * 0.8) {
                                el.style.display = 'none';
                                el.remove();
                            }
                        }
                    });
                    
                    // body 속성 완전 정상화
                    document.body.style.cssText = 'overflow: auto !important; position: static !important;';
                    document.documentElement.style.cssText = 'overflow: auto !important;';
                };
                
                finalRemovePopups();
            """)
            
            # ESC 키 눌러서 팝업 닫기 시도
            await page.keyboard.press('Escape')
            await asyncio.sleep(0.3)
                    
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
                await asyncio.sleep(0.3)  # 0.5초 → 0.3초
            
            # 맨 아래까지 스크롤
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(delay)
            
            # 다시 맨 위로 스크롤 (전체 캡처를 위해)
            await page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(0.5)  # 1초 → 0.5초
            
        except Exception as e:
            print(f"⚠️ 스크롤 중 오류: {e}")
    
    async def get_top_posts(self):
        """각 사이트별 랜덤 2개 게시물 조회"""
        import random
        app = create_app()
        posts_by_site = {}
        
        with app.app_context():
            # 뽐뿌 제외하고 3개 사이트만 캡처
            for site in ['bobae', 'dcinside', 'fmkorea']:
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
        
        async with async_playwright() as p:
            # Chromium 브라우저 실행 - 모바일 시뮬레이션 + 한글 지원
            browser = await p.chromium.launch(
                headless=True,  # 백그라운드 실행
                args=[
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--high-dpi-support=1',
                    '--disable-web-security',
                    '--font-render-hinting=none',
                    '--disable-gpu-sandbox',
                    '--lang=ko-KR',
                    '--accept-lang=ko-KR,ko,en-US,en',
                    '--disable-font-subpixel-positioning',
                    '--user-agent=Mozilla/5.0 (Linux; Android 14; SM-S926B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'  # 모바일 UA 강제
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
                        print(f"\n[{current_count}/{total_posts}] {site_config['name']} 캡처 시작")
                        
                        try:
                            post_files = await self.capture_post(browser, post, site_config, p)
                            if post_files:
                                if isinstance(post_files, list):
                                    captured_files.extend(post_files)
                                    print(f"  ✅ {site_config['name']} 성공: {len(post_files)}개 파일 생성")
                                else:
                                    captured_files.append(post_files)
                                    print(f"  ✅ {site_config['name']} 성공: 1개 파일 생성")
                            else:
                                print(f"  ❌ {site_config['name']} 실패: 파일 생성되지 않음")
                        except Exception as e:
                            print(f"  ❌ {site_config['name']} 예외 발생: {str(e)}")
                        
                        # 사이트 부하 방지를 위한 딜레이 (단축)
                        if i < len(posts):
                            await asyncio.sleep(1)  # 2초 → 1초
                
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
from app.crawlers.site_crawlers import FmkoreaCrawler
import traceback

try:
    print("에펨코리아 크롤러 테스트 시작...")
    crawler = FmkoreaCrawler()
    posts = crawler.crawl_popular_posts()
    print(f'에펨코리아 크롤링 결과: {len(posts)}개')
    for i, post in enumerate(posts[:3], 1):
        title = post["title"][:60]
        print(f'{i}. {title}...')
except Exception as e:
    print(f'에펨코리아 크롤링 오류: {e}')
    print(traceback.format_exc())
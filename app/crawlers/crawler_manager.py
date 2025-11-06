from .site_crawlers import PpomppuCrawler, FmkoreaCrawler, BobaeCrawler, DcinsideCrawler, RuliwebCrawler, DogdripCrawler
from app.models import Post, db
from datetime import datetime
from typing import List, Dict

class CrawlerManager:
    """크롤러 관리자 클래스"""
    
    def __init__(self):
        self.crawlers = {
            'ppomppu': PpomppuCrawler(),
            'fmkorea': FmkoreaCrawler(),
            'bobae': BobaeCrawler(),
            'ruliweb': RuliwebCrawler(),
            'dcinside': DcinsideCrawler(),
            'dogdrip': DogdripCrawler()
        }
    
    def crawl_all_sites(self) -> int:
        """모든 사이트 크롤링"""
        total_new_posts = 0
        
        for site_name, crawler in self.crawlers.items():
            try:
                print(f"{site_name} 크롤링 시작...")
                posts = crawler.crawl_popular_posts()
                new_posts = self.save_posts(posts)
                total_new_posts += new_posts
                print(f"{site_name}: {new_posts}개 새 게시물 저장")
                
            except Exception as e:
                print(f"{site_name} 크롤링 오류: {e}")
                continue
        
        return total_new_posts
    
    def crawl_site(self, site_name: str) -> int:
        """특정 사이트 크롤링"""
        if site_name not in self.crawlers:
            raise ValueError(f"지원하지 않는 사이트: {site_name}")
        
        crawler = self.crawlers[site_name]
        posts = crawler.crawl_popular_posts()
        return self.save_posts(posts)
    
    def save_posts(self, posts_data: List[Dict]) -> int:
        """게시물 데이터 저장"""
        new_posts_count = 0
        
        for post_data in posts_data:
            try:
                # 중복 체크 (URL 기준)
                existing_post = Post.query.filter_by(url=post_data['url']).first()
                
                if existing_post:
                    # 기존 게시물 업데이트 (조회수, 추천수 등)
                    existing_post.views = post_data.get('views', existing_post.views)
                    existing_post.likes = post_data.get('likes', existing_post.likes)
                    existing_post.comments = post_data.get('comments', existing_post.comments)
                    existing_post.crawled_at = datetime.utcnow()
                else:
                    # 새 게시물 생성
                    new_post = Post(
                        title=post_data['title'],
                        url=post_data['url'],
                        site=post_data['site'],
                        category=post_data['category'],
                        author=post_data.get('author', ''),
                        views=post_data.get('views', 0),
                        likes=post_data.get('likes', 0),
                        comments=post_data.get('comments', 0),
                        created_at=datetime.utcnow(),
                        crawled_at=datetime.utcnow()
                    )
                    
                    db.session.add(new_post)
                    new_posts_count += 1
                
            except Exception as e:
                print(f"게시물 저장 오류: {e}")
                continue
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"데이터베이스 커밋 오류: {e}")
            raise
        
        return new_posts_count
import schedule
import time
import threading
from datetime import datetime
from app.crawlers.crawler_manager import CrawlerManager

class Scheduler:
    """크롤링 스케줄러"""
    
    def __init__(self):
        self.crawler_manager = CrawlerManager()
        self.running = False
        self.thread = None
    
    def start_scheduler(self):
        """스케줄러 시작"""
        if self.running:
            return
        
        # 매 시간마다 크롤링 실행
        schedule.every().hour.do(self.run_crawling)
        
        # 매일 오전 9시에 전체 크롤링
        schedule.every().day.at("09:00").do(self.run_full_crawling)
        
        self.running = True
        self.thread = threading.Thread(target=self._run_schedule, daemon=True)
        self.thread.start()
        
        print("크롤링 스케줄러가 시작되었습니다.")
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.running = False
        schedule.clear()
        print("크롤링 스케줄러가 중지되었습니다.")
    
    def _run_schedule(self):
        """스케줄 실행 루프"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 체크
    
    def run_crawling(self):
        """일반 크롤링 실행"""
        try:
            print(f"[{datetime.now()}] 크롤링 시작...")
            result = self.crawler_manager.crawl_all_sites()
            print(f"[{datetime.now()}] 크롤링 완료: {result}개 게시물")
        except Exception as e:
            print(f"[{datetime.now()}] 크롤링 오류: {e}")
    
    def run_full_crawling(self):
        """전체 크롤링 실행"""
        try:
            print(f"[{datetime.now()}] 전체 크롤링 시작...")
            result = self.crawler_manager.crawl_all_sites()
            print(f"[{datetime.now()}] 전체 크롤링 완료: {result}개 게시물")
        except Exception as e:
            print(f"[{datetime.now()}] 전체 크롤링 오류: {e}")

# 전역 스케줄러 인스턴스
scheduler_instance = None

def get_scheduler():
    """스케줄러 인스턴스 반환"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = Scheduler()
    return scheduler_instance
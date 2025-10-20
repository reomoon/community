#!/usr/bin/env python3

import sys
sys.path.append('.')
from app import create_app
from app.models import db, SiteVisit
from datetime import datetime

def main():
    app = create_app()
    with app.app_context():
        total = db.session.query(db.func.sum(SiteVisit.visit_count)).scalar()
        today = datetime.utcnow().date()
        today_visit = SiteVisit.query.filter_by(visit_date=today).first()
        
        print(f'총 방문자 수: {total}')
        print(f'오늘 방문자: {today_visit.visit_count if today_visit else 0}')
        
        # 새 방문자 추가 테스트
        if today_visit:
            today_visit.visit_count += 1
            db.session.commit()
            print(f'방문자 수 증가됨: {today_visit.visit_count}')

if __name__ == '__main__':
    main()
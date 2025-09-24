# 한국 커뮤니티 애그리게이터

주요 한국 커뮤니티 사이트(보배드림, 뽐뿌, fmkorea, 디시인사이드)에서 인기 게시물을 수집하여 한 곳에서 볼 수 있는 웹 애플리케이션입니다.

## 주요 기능

- 4개 주요 커뮤니티 사이트의 실시간 인기 게시물 수집
- 인기도 기반 자동 정렬 (조회수 + 추천수 + 댓글수)
- 사이트별 필터링 및 검색 기능
- 깔끔한 반응형 웹 인터페이스
- 1시간마다 자동 업데이트
- 각 사이트별 통계 정보 (조회수, 추천수, 댓글수)

## 설치 및 실행

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 애플리케이션 실행:
```bash
python run.py
```

3. 브라우저에서 `http://localhost:5000` 접속

## 지원 사이트

| 사이트 | URL | 수집 정보 |
|--------|-----|-----------|
| 보배드림 | bobaedream.co.kr | 조회수, 추천수, 댓글수 |
| 뽐뿌 | ppomppu.co.kr | 조회수, 추천수, 댓글수 |
| fmkorea | fmkorea.com | 추천수, 댓글수 |
| 디시인사이드 | dcinside.com | 조회수, 추천수, 댓글수 |

## 스크린샷

![메인 화면](screenshot.png)

## API 엔드포인트

- `GET /api/posts` - 게시물 목록 조회
- `GET /api/stats` - 통계 정보 조회  
- `GET /api/crawl` - 수동 크롤링 실행

## 프로젝트 구조

```
community-aggregator/
├── 📂 app/                     # 메인 애플리케이션
│   ├── crawlers/               # 크롤링 엔진
│   ├── static/                 # CSS, JavaScript  
│   └── templates/              # HTML 템플릿
├── 📂 analyze/                 # 사이트 분석 도구들
│   ├── analyze_dcinside_comments.py
│   ├── analyze_fmkorea_views.py
│   └── __init__.py
├── 📂 dev/                     # 개발/테스트 도구들
│   ├── crawl.py                # 단독 크롤링 테스트
│   ├── crawl_only.py           # 크롤링만 실행
│   ├── dev_server.py           # 개발 서버 설정
│   └── __init__.py
├── 📂 test/                    # 테스트 파일들
│   └── test_*.py
├── 📄 config.py                # 설정 파일
├── 📄 run.py                   # 메인 실행 파일
├── 📄 requirements.txt         # 의존성 패키지
├── 📄 README.md                # 프로젝트 문서
└── 📄 .gitignore               # Git 제외 파일
```

### 개발 도구 사용법

```bash
# 메인 서버 실행
python run.py

# 개발용 크롤링 테스트
python dev/crawl_only.py

# 사이트 구조 분석
python analyze/analyze_dcinside_comments.py
python analyze/analyze_fmkorea_views.py

# 단위 테스트
python test/test_ppomppu.py
python test/test_fmkorea.py
```

## 기술 스택

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **크롤링**: BeautifulSoup4, Requests
- **스케줄링**: Python Schedule
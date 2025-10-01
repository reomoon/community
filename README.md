# 한국 커뮤니티 애그리게이터<<<<<<< HEAD

# community

주요 한국 커뮤니티 사이트(보배드림, 뽐뿌, 에펨코리아, 디시인사이드)에서 인기 게시물을 수집하여 한 곳에서 볼 수 있는 웹 애플리케이션입니다.=======

# 한국 커뮤니티 애그리게이터

🔗 **라이브 사이트**: https://hot-comm.vercel.app/

주요 한국 커뮤니티 사이트(보배드림, 뽐뿌, fmkorea, 디시인사이드)에서 인기 게시물을 수집하여 한 곳에서 볼 수 있는 웹 애플리케이션입니다.

## ✨ 주요 기능

## 주요 기능

### 🔥 실시간 커뮤니티 수집

- 4개 주요 커뮤니티 사이트의 실시간 인기 게시물 수집- 4개 주요 커뮤니티 사이트의 실시간 인기 게시물 수집

- 매일 10:00, 22:00 자동 업데이트 (GitHub Actions)- 인기도 기반 자동 정렬 (조회수 + 추천수 + 댓글수)

- 인기도 기반 자동 정렬 (조회수 + 추천수 + 댓글수)- 사이트별 필터링 및 검색 기능

- 깔끔한 반응형 웹 인터페이스

### 📱 모바일 최적화 캡처- 1시간마다 자동 업데이트

- **갤럭시 S25** 해상도 기준 고품질 스크린샷 자동 생성- 각 사이트별 통계 정보 (조회수, 추천수, 댓글수)

- **3배 해상도** (1236x2745) 초고해상도 모바일 캡처

- 게시물 + 댓글까지 완전 캡처## 설치 및 실행

- 네이버 블로그 포스팅에 최적화된 분할 캡처

1. 필요한 패키지 설치:

### 🎛️ 사용자 친화적 인터페이스```bash

- 사이트별 필터링 (전체, 뽐뿌, 에펨코리아, 보배, 디시)pip install -r requirements.txt

- 정렬 옵션 (최신순, 조회수순, 추천순)```

- 실시간 검색 기능

- 깔끔한 반응형 웹 디자인2. 애플리케이션 실행:

- Font Awesome 아이콘 적용```bash

python run.py

### 🤖 자동화 시스템```

- GitHub Actions 기반 완전 자동화

- 주간 파일 정리 (일요일 오전 6시)3. 브라우저에서 `http://localhost:5000` 접속

- 7일 이상 된 데이터 자동 삭제

- Vercel 자동 배포## 지원 사이트



## 🌐 지원 사이트| 사이트 | URL | 수집 정보 |

|--------|-----|-----------|

| 사이트 | URL | 수집 정보 | 배지 || 보배드림 | bobaedream.co.kr | 조회수, 추천수, 댓글수 |

|--------|-----|-----------|------|| 뽐뿌 | ppomppu.co.kr | 조회수, 추천수, 댓글수 |

| 뽐뿌 | ppomppu.co.kr | 조회수, 추천수, 댓글수 | [뽐뿌] || fmkorea | fmkorea.com | 추천수, 댓글수 |

| 에펨코리아 | fmkorea.com | 추천수, 댓글수 | [에펨코리아] || 디시인사이드 | dcinside.com | 조회수, 추천수, 댓글수 |

| 보배드림 | bobaedream.co.kr | 조회수, 추천수, 댓글수 | [보배] |

| 디시인사이드 | dcinside.com | 조회수, 추천수, 댓글수 | [디시] |## 스크린샷



## 🚀 설치 및 실행![메인 화면](screenshot.png)



1. **저장소 클론**:## API 엔드포인트

```bash

git clone https://github.com/reomoon/community.git- `GET /api/posts` - 게시물 목록 조회

cd community-aggregator- `GET /api/stats` - 통계 정보 조회  

```- `GET /api/crawl` - 수동 크롤링 실행



2. **필요한 패키지 설치**:## 프로젝트 구조

```bash

pip install -r requirements.txt```

playwright install chromiumcommunity-aggregator/

```├── 📂 app/                     # 메인 애플리케이션

│   ├── crawlers/               # 크롤링 엔진

3. **애플리케이션 실행**:│   ├── static/                 # CSS, JavaScript  

```bash│   └── templates/              # HTML 템플릿

python run.py├── 📂 analyze/                 # 사이트 분석 도구들

```│   ├── analyze_dcinside_comments.py

│   ├── analyze_fmkorea_views.py

4. **브라우저에서 접속**: `http://localhost:5000`│   └── __init__.py

├── 📂 dev/                     # 개발/테스트 도구들

## 📸 모바일 캡처 사용법│   ├── crawl.py                # 단독 크롤링 테스트

│   ├── crawl_only.py           # 크롤링만 실행

### 자동 캡처 실행│   ├── dev_server.py           # 개발 서버 설정

```bash│   └── __init__.py

python capture_posts.py├── 📂 test/                    # 테스트 파일들

```│   └── test_*.py

├── 📄 config.py                # 설정 파일

### 수동 파일 정리├── 📄 run.py                   # 메인 실행 파일

```bash├── 📄 requirements.txt         # 의존성 패키지

python cleanup_files.py├── 📄 README.md                # 프로젝트 문서

```└── 📄 .gitignore               # Git 제외 파일

```

## 📅 자동화 스케줄

### 개발 도구 사용법

| 작업 | 시간 | 빈도 | 설명 |

|------|------|------|------|```bash

| 크롤링 + 캡처 | 10:00, 22:00 KST | 매일 | 게시물 수집 + 모바일 캡처 |# 메인 서버 실행

| 파일 정리 | 06:00 KST | 매주 일요일 | 7일 이상 된 파일 자동 삭제 |python run.py



## 🛠️ 기술 스택# 개발용 크롤링 테스트

python dev/crawl_only.py

### Backend

- **Flask 3.1.2**: 웹 프레임워크# 사이트 구조 분석

- **SQLAlchemy**: ORM 및 데이터베이스 관리python analyze/analyze_dcinside_comments.py

- **SQLite**: 경량 데이터베이스python analyze/analyze_fmkorea_views.py



### Frontend  # 단위 테스트

- **HTML5, CSS3**: 반응형 웹 디자인python test/test_ppomppu.py

- **Vanilla JavaScript**: 필터링 및 검색 기능python test/test_fmkorea.py

- **Font Awesome 6.0**: 아이콘 라이브러리```



### 크롤링 & 자동화## 기술 스택

- **BeautifulSoup4**: HTML 파싱

- **Requests**: HTTP 요청- **Backend**: Flask, SQLAlchemy, SQLite

- **Playwright**: 고품질 모바일 스크린샷- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

- **GitHub Actions**: CI/CD 자동화- **크롤링**: BeautifulSoup4, Requests

- **Vercel**: 정적 사이트 배포- **스케줄링**: Python Schedule

>>>>>>> origin/master

## 📊 성능 지표

- **응답 시간**: ~2초 (50개 게시물 로딩)
- **캡처 품질**: 1236x2745 (갤럭시 S25 @ 3x DPI)
- **저장소 효율**: 자동 정리로 7일 순환 보관
- **업데이트 주기**: 하루 2회 (오전/저녁)

---

⭐ **이 프로젝트가 유용하다면 Star를 눌러주세요!**
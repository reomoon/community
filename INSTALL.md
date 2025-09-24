# 커뮤니티 애그리게이터 설치 및 실행 가이드

## 🚀 빠른 시작

### 1. 필수 요구사항
- Python 3.8 이상
- pip (Python 패키지 관리자)

### 2. 설치

#### Windows PowerShell:
```powershell
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
.\venv\Scripts\Activate.ps1

# 필요한 패키지 설치
pip install -r requirements.txt
```

#### Linux/Mac:
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 3. 실행

#### 개발 서버 실행:
```bash
python dev_server.py
```

#### 또는 기본 실행:
```bash
python run.py
```

#### 수동 크롤링 실행:
```bash
python crawl.py
```

### 4. 접속
브라우저에서 http://localhost:5000 으로 접속

## 📱 주요 기능

### 웹 인터페이스
- **메인 페이지**: 모든 커뮤니티의 인기 게시물을 한 눈에 확인
- **카테고리 필터**: 경제, 유머, 연예, 기술 등으로 분류
- **사이트 필터**: 특정 커뮤니티만 보기
- **검색 기능**: 제목으로 게시물 검색
- **정렬**: 최신순, 조회수순, 추천순 정렬

### API 엔드포인트
- `GET /api/posts` - 게시물 목록 조회
- `GET /api/crawl` - 수동 크롤링 실행
- `GET /api/stats` - 통계 정보 조회

### 지원 사이트
- **보배드림** (bobae.co.kr)
- **뽐뿌** (ppomppu.co.kr)  
- **fmkorea** (fmkorea.com)
- **디시인사이드** (dcinside.com)

## ⚙️ 설정

### config.py에서 다음 설정을 변경할 수 있습니다:
- `CRAWL_INTERVAL_HOURS`: 크롤링 주기 (기본: 1시간)
- `MAX_POSTS_PER_SITE`: 사이트당 최대 수집 게시물 수 (기본: 20개)
- 지원 사이트 활성화/비활성화

## 🔧 문제 해결

### 크롤링이 안 될 때:
1. 인터넷 연결 확인
2. 사이트 접속 확인 (일부 사이트는 접속 제한이 있을 수 있음)
3. User-Agent 헤더 확인

### 설치 오류:
1. Python 버전 확인 (3.8 이상 필요)
2. pip 업데이트: `pip install --upgrade pip`
3. 가상환경 재생성

## 📈 개선 계획

- [ ] 더 많은 커뮤니티 사이트 지원
- [ ] 실시간 알림 기능
- [ ] 게시물 즐겨찾기 기능
- [ ] 모바일 앱 개발
- [ ] 데이터 시각화 대시보드

## 📄 라이선스
MIT License

## 🤝 기여하기
Pull Request와 Issue는 언제나 환영입니다!
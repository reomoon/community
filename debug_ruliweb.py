import requests
from bs4 import BeautifulSoup

# 루리웹 페이지 구조 디버그
url = 'https://bbs.ruliweb.com/best/humor_only?orderby=recommend&range=24h'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

print(f"응답 상태: {response.status_code}")
print(f"HTML 길이: {len(response.content)}")

# 테이블 행들 확인 - 다양한 셀렉터 시도
selectors = [
    'table.board_list tbody tr',
    'table tbody tr',
    'tr',
    '.board_list tr'
]

for selector in selectors:
    rows = soup.select(selector)
    print(f"\n셀렉터 '{selector}': {len(rows)}개 행 발견")
    if rows:
        # 첫번째 행 분석
        cells = rows[0].find_all(['td', 'th'])
        print(f"  첫 행: {len(cells)}개 셀")
        for j, cell in enumerate(cells[:6]):  # 처음 6개 셀만
            text = cell.get_text().strip()
            print(f"    셀[{j}]: '{text[:30]}...' ({len(text)}자)")
        break
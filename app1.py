from bs4 import BeautifulSoup
import requests

url = 'https://news.naver.com/'
response = requests.get(url)

# print(response)

soup = BeautifulSoup(response.text, 'lxml')

# print(soup)

# 모든 뉴스 제목 가져오기
titles = soup.select('a[href*="news.naver"]')

for t in titles:
    print(t.get_text(strip=True))
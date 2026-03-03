from bs4 import BeautifulSoup
import requests

url = "https://finance.naver.com/"
res = requests.get(url)

print(res)

soup = BeautifulSoup(res.text)
print(soup.title)
print(soup.title.text)

print(soup.find("h1"))
print(soup.find("h1").text)


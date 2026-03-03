from bs4 import BeautifulSoup
import requests

url = "http://127.0.0.1:8000/index.html"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

lis = soup.find_all("li")

for li in lis:
  print( li.find("a").text )




# main_brick = soup.find('div', class_='main_brick')

# divs = main_brick.find_all("div", class_="brick-vowel")
# i = 0
# for div in divs:
#     if i == 1:
#     #  print(div.get_text(strip=True))
#      print(div)
#     i = i + 1

# # print(arr[1].get_text(strip=True))

# parents = soup.find('div', class_='grid1_wrap brick-house _brick_gid_wrapper')
# # data = parents.find_all("div", class_="brick-vowel _brick-coum")
# # print(parents)
# parentdiv = parents.find("div", class_="brick-vowel _brick_column")
# div = parentdiv.find_all("div", class_="main_brick_item")
# print(div[1].text)
# for div in parentdivs:
#     print(div.text)

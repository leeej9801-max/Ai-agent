from bs4 import BeautifulSoup as bs
from requests import get
import json
from db import save, saveMany

def getLikes(list, head=None):
  ids = ""
  #for i in range(len(list)):
  #  if i == 0:
  #    ids += f"{list[i]["id"]}"
  #  else:
  #    ids += f",{list[i]["id"]}"
  ids = ",".join(str(item["id"]) for item in list)
  if ids:
    url = f"https://www.melon.com/commonlike/getSongLike.json?contsIds={ids}"
    res = get(url, headers=head)
    if res.status_code == 200:
      data = json.loads(res.text)
      for row in data["contsLike"]:
        for i in range(len(list)):
          if list[i]["id"] == row["CONTSID"]:
            list[i]["cnt"] = row["SUMMCNT"]
            break
  return list

def getData(data):
  arr = []
  trs = data.select("#frm tbody > tr")
  if trs:
    for i in range(len(trs)):
      id = int(trs[i].select("td")[0].select_one("input[type='checkbox']").get("value"))
      img = cleanData(trs[i].select("td")[2].select_one("img")["src"])
      title = cleanData(trs[i].select("td")[4].select_one("div[class='ellipsis rank01']").text)
      artist = cleanData(trs[i].select_one("div.ellipsis.rank02").get_text(" ", strip=True))
      album = cleanData(trs[i].select("td")[5].select_one("div[class='ellipsis rank03']").text)
      arr.append( {"id": id, "img": img, "title": title,"artist":artist , "album": album, "cnt": 0} )
  return arr

def cleanData(txt):
  list = ["\n", "\xa0", "\r", "\t", "총건수"]
  for target in list:
    txt = txt.replace(target, "")
  txt = txt.replace("'", '"')
  return txt.strip()

def crawlingMelon(code: str, head=None):
  if head is None:
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
  url = f"https://www.melon.com/genre/song_list.htm?gnrCode={code}&orderBy=POP"
  res = get(url, headers=head)
  arr = []
  if res.status_code == 200:
    data = bs(res.text)
    arr = getData(data)
    arr = getLikes(arr, head)
    #print("값",arr)
    if len(arr) > 0:
        #save(sql1)
      genre = code
      sql2 = f"""
          INSERT INTO edu.`melon` 
          (`id`, `genre`, `img`, `title`, `album`, `cnt`)
          VALUE
          (%s, %s, %s, %s, %s, %s)
          ON DUPLICATE KEY UPDATE
            genre=VALUES(genre),
            img=VALUES(img),
            title=VALUES(title),
            album=VALUES(album),
            cnt=VALUES(cnt)
      """
      values = [(row["id"],genre, row["img"], row["title"], row["album"], row["cnt"]) for row in arr]
      print(genre)
      saveMany(None, sql2, values)
  return arr

# GENRES = ["GN0100", "GN0200", "GN0300", "GN0400", "GN0500"]

# for g in GENRES:
#     try:
#         result = crawlingMelon(g)
#         print(g, "곡 수:", len(result))
#     except Exception as e:
#         print("실패:", g, e)

arr = crawlingMelon("GN0100")
with open("melon_GN0200.json", "w", encoding="utf-8") as f:
    json.dump(arr, f, ensure_ascii=False, indent=2)
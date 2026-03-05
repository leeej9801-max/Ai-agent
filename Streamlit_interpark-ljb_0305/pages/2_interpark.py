from bs4 import BeautifulSoup as bs
from requests import get
import pandas as pd
import streamlit as st
import json
from db import save, saveMany, findAll

st.set_page_config(
  page_title="interpark 수집",
  page_icon="💗",
  layout="wide",
)

if 'link_index' not in st.session_state:
	st.session_state.link_index = 0

# 인터파크 장르별 URL

option = ["MUSICAL", "CONCERT", "CLASSIC", "KIDS", "DRAMA", "EXHIBIT", "SPORTS", "LEISURE"]

musical_key = f'@"/ranking","?period=D&page=1&pageSize=50&rankingTypes={option[st.session_state.link_index]}",'

# -------------------------------
# 데이터 수집
# -------------------------------

def getData(items):
  try:
    code = option[st.session_state.link_index]
    url = f"https://tickets.interpark.com/contents/ranking?genre={code}"
    st.text(f"URL: {url}")
    res = get(url)
    if res.status_code == 200:
      st.text("인터파크 티켓 수집 시작!")
      tickets = [] # { 장르, 티켓이름, 장소, 시작날짜, 종료날짜, 예매율 }
      soup = bs(res.text, "html.parser")
      items = soup.select("div.responsive-ranking-list_rankingItem__PuQPJ")
      # for item in items:
      #   tName = item.select_one("li.responsive-ranking-list_goodsName__aHHGY").get_text(strip=True)
      #   pName = item.select_one("li.responsive-ranking-list_placeName__9HN2O").get_text(strip=True)
      #   tDate = item.select_one("div.responsive-ranking-list_dateWrap__jBu5n").get_text(strip=True)
      #   tPercent = item.select_one("li.responsive-ranking-list_bookingPercent__7ppKT").get_text(strip=True)
      #   tickets.append({ "genre": code, "tName": tName, "pName": pName, "tDate": tDate, "tPercent": tPercent })
      script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
      json_data = json.loads(script_tag.string)
      st.json(json_data, expanded=False)
      st.html("<hr/>")
      st.text(f"{option} 목록 출력")
      tickets = json_data.get('props', {}).get('pageProps', {}).get('fallback', {}).get(musical_key, [])
      st.json(tickets)
      json_string = json.dumps(tickets, ensure_ascii=False, indent=2)

      tab1, tab2, tab3, tab4 = st.tabs(["HTML 데이터", "json 데이터", "DataFrame", "API 데이터"])
      with tab1:
        st.text("HTML 출력")
        # st.html(items)
        st.text(items)
      with tab2:
        st.text("JSON 출력")
        # st.json(arr)
        json_string = json.dumps(tickets, ensure_ascii=False, indent=2)
        st.json(body=json_string, expanded=True, width="stretch")
      with tab3:
        st.text("DataFrame 출력")
        st.dataframe(pd.DataFrame(tickets))
      with tab4:
        st.text("API 출력")
  except Exception as e:
    return []
  return tickets

# -------------------------------
# ticket 테이블 db 저장
# -------------------------------

def crawlingMelon(code: str):
  # if head is None:
  #   head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
  url = f"https://tickets.interpark.com/contents/ranking?genre={code}"
  res = get(url)
  arr = []
  if res.status_code == 200:
    data = bs(res.text)
    arr = getData(data)
    if len(arr) > 0:
      sql2 = f"""
          INSERT INTO edu.`ticket` 
          (`id`, `title`,`placeCode`, `genre`, `placeName`, `playStartDate`, `playEndDate`, `bookingPercent`)
          VALUE
          (%s, %s, %s, %s, %s, %s, %s, %s)
          ON DUPLICATE KEY UPDATE
            id=VALUES(id),
            title=VALUES(title),
            placeCode=VALUES(placeCode),
            genre=VALUES(genre),
            placeName=VALUES(placeName),
            playStartDate=VALUES(playStartDate),
            playEndDate=VALUES(playEndDate),
            bookingPercent=VALUES(bookingPercent)
      """
      values = [(row["goodsCode"], row["goodsName"], row["placeCode"], row["genre"], row["placeName"], row["playStartDate"], row["playEndDate"], row["bookingPercent"]) for row in arr]
      saveMany(sql2, values)
  return arr

# -------------------------------
# statistic 테이블 db 저장
# -------------------------------

def statistic():
  sql1 = "SELECT id, placeCode FROM edu.ticket;"
  data = findAll(sql1)

  #  이미 있는 데이터 중복처리 방지용입니당
  sql_exist = "SELECT id FROM edu.statistic;"
  exist_ids = set(row["id"] for row in findAll(sql_exist))

  for i in range(len(data)):
    row = data[i]
    id = row["id"]
    placeCode = row["placeCode"]

    #  이미 있는 데이터 중복처리 방지용입니당
    if id in exist_ids:
      continue

    url = f"https://tickets.interpark.com/contents/api/statistics/booking/{id}?placeCode={placeCode}"
    res = get(url)
    if res.status_code == 200:
      json_data = json.loads(res.text)
      jData = json_data['ageGender']
      sql =  f"""
          INSERT INTO edu.`statistic` 
          (`id`, `age10Rate`,`age20Rate`, `age30Rate`, `age40Rate`, `age50Rate`, `maleRate`, `femaleRate`)
          VALUE
          (%s, %s, %s, %s, %s, %s, %s, %s)
          ON DUPLICATE KEY UPDATE
            age10Rate=VALUES(age10Rate),
            age20Rate=VALUES(age20Rate),
            age30Rate=VALUES(age30Rate),
            age40Rate=VALUES(age40Rate),
            age50Rate=VALUES(age50Rate),
            maleRate=VALUES(maleRate),
            femaleRate=VALUES(femaleRate)
      """
      values = [(id, jData["age10Rate"], jData["age20Rate"], jData["age30Rate"], jData["age40Rate"], jData["age50Rate"], jData["maleRate"], jData["femaleRate"])]
      saveMany(sql, values)

# -------------------------------
# 분석 데이터 조회
# ticket + statistic JOIN
# -------------------------------
def get_analysis_data():

    sql = """
        SELECT
            t.title,
            t.genre,
            t.bookingPercent,
            s.age10Rate,
            s.age20Rate,
            s.age30Rate,
            s.age40Rate,
            s.age50Rate,
            s.maleRate,
            s.femaleRate
        FROM edu.ticket t
        JOIN edu.statistic s
        ON t.id = s.id
    """

    data = findAll(sql)

    # DB → DataFrame 변환
    df = pd.DataFrame(data)

    return df


# -------------------------------
# Streamlit 화면
# -------------------------------

st.title("인터파크 공연 예매 분석")

if st.button("분석 데이터 불러오기"):

    df = get_analysis_data()

    if len(df) == 0:
        st.warning("데이터가 없습니다.")
        st.stop()

    # -------------------------------
    # 테이블 보기
    # -------------------------------
    st.subheader("원본 데이터")
    st.dataframe(df)

    # -------------------------------
    # 작품별 예매율
    # -------------------------------
    st.subheader("작품별 예매율")

    chart_df = df[["title", "bookingPercent"]].copy()

    chart_df["bookingPercent"] = chart_df["bookingPercent"].str.replace("%", "").astype(float)

    st.bar_chart(chart_df.set_index("title"))


    # -------------------------------
    # 나이대 평균
    # -------------------------------
    st.subheader("연령대 평균 예매율")

    age_df = df[[
        "age10Rate",
        "age20Rate",
        "age30Rate",
        "age40Rate",
        "age50Rate"
    ]]

    age_avg = age_df.mean()

    st.bar_chart(age_avg)


    # -------------------------------
    # 성별 비율
    # -------------------------------
    st.subheader("성별 평균 비율")

    gender_df = df[["maleRate", "femaleRate"]]

    gender_avg = gender_df.mean()

    st.bar_chart(gender_avg)

selected = st.selectbox(
  label="음원 장르를 선택하세요",
  options=option,
  index=None,
  placeholder="수집 대상을 선택하세요."
)

if st.button("통계 수집"):
  statistic()

if selected:
  st.write("선택한 장르 :", selected)
  st.session_state.link_index = option.index(selected)
  if st.button(f"'{option[st.session_state.link_index]}' 수집"):
    crawlingMelon(f"{option[st.session_state.link_index]}")
    # if getData() == 0:
    #   st.text("수집된 데이터가 없습니다.")
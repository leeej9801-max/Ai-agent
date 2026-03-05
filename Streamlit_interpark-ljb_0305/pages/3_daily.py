from bs4 import BeautifulSoup as bs
from requests import get
import pandas as pd
import streamlit as st
import json

st.set_page_config(
  page_title="일간(‘daily’) 랭킹 수집",
  page_icon="💗",
  layout="wide",
)

url = "https://mapi.ticketlink.co.kr/mapi/ranking/genre/daily?categoryId=10&categoryId2=16&categoryId3=0&menu=RANKING"

# 데이터 수집
def getData():
  try:
    st.text(f"URL: {url}")
    res = get(url)
    if res.status_code == 200:
      st.text("API 데이터 수집 시작!")
      json_data = json.loads(res.text)
      tab1, tab2 = st.tabs(["json 데이터", "DataFrame"])
      with tab1:
        st.text("json 출력")
        st.json(json_data.get("data", {}), expanded=False, width="stretch")
        st.html("<hr/>")
        st.text("랭킹 목록 출력")
        st.json(json_data.get("data", {}).get("rankingList", []), expanded=False, width="stretch")
      with tab2:
        st.text("DataFrame 출력")
        st.dataframe(pd.DataFrame(json_data.get("data", {}).get("rankingList", [])))
  except Exception as e:
    return 0
  return 1

if st.button(f"수집하기"):
  getData()
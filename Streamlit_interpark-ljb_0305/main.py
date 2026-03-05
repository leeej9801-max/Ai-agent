import streamlit as st

st.set_page_config(
  page_title="수집",
  page_icon="💗",
  layout="wide",
)

st.title("streamlit 프로젝트")

st.subheader("1. Yes24 베스트셀러 수집")
with st.expander("보기"):
  st.page_link(page="./pages/1_yes24.py", label="[수집 보기]", icon="🔗")
  st.code("""
    def getData():
      try:
        url = ""
        st.text(f"URL: {url}")
        res = get(url)
        if res.status_code == 200:
          st.text("yes24 국내도서 주별 베스트 수집 시작!")
          books = [] # { 도서명, 저자, 별점 }
          tab1, tab2, tab3 = st.tabs(["HTML 데이터", "JSON 데이터", "DataFrame"])
          with tab1:
            st.text("html 출력")
          with tab2:
            st.text("JSON 출력")
          with tab3:
            st.text("DataFrame 출력")
      except Exception as e:
        return 0
      return 1
  """)

st.subheader("2. 인터파크 티켓 수집")
with st.expander("보기"):
  st.page_link(page="./pages/2_interpark.py", label="[수집 보기]", icon="🔗")
  st.code("""
    def getData():
      try:
        url = ""
        st.text(f"URL: {url}")
        res = get(url)
        if res.status_code == 200:
          st.text("인터파크 티켓 수집 시작!")
          tickets = [] # { 장르, 티켓이름, 장소, 시작날짜, 종료날짜, 예매율 }
          tab1, tab2, tab3 = st.tabs(["HTML 데이터", "JSON 데이터", "DataFrame"])
          with tab1:
            st.text("html 출력")
          with tab2:
            st.text("JSON 출력")
          with tab3:
            st.text("DataFrame 출력")
      except Exception as e:
        return 0
      return 1
  """)

st.subheader("3. 일간(‘daily’) 랭킹 수집")
with st.expander("보기"):
  st.page_link(page="./pages/3_daily.py", label="[수집 보기]", icon="🔗")
  st.markdown("""
    ## API URL 구조
    - mapi.ticketlink.co.kr : 티켓링크의 모바일 API 서버 도메인
    - /mapi/ranking/genre/daily : 장르별 일간 랭킹 API
    - categoryId=10 : 상위 카테고리 (예: 공연)
    - categoryId2=16 : 세부 장르 (예: 뮤지컬)
    - categoryId3=0 : 추가 하위 분류 (없음을 의미)
    - menu=RANKING : 랭킹 메뉴 지정
              
    ---

    ## 🎫 1️⃣ 상위 카테고리 (categoryId)

    `categoryId` 는 **대분류**를 의미합니다.

    | categoryId | 카테고리(대분류)    |
    | ---------- | ------------ |
    | 10         | 공연           |
    | 20         | 스포츠          |
    | 30         | 전시/행사        |
    | 40         | 레저           |
    | 50         | 영화 (특별 상영 등) |

    ---

    ## 🎭 2️⃣ 공연 카테고리(10)의 세부 장르 (categoryId2)

    `categoryId=10` (공연)일 때, `categoryId2` 가 세부 장르입니다.

    | categoryId2 | 세부 장르  |
    | ----------- | ------ |
    | 14          | 콘서트    |
    | 15          | 연극     |
    | 16          | 뮤지컬    |
    | 17          | 클래식/무용 |
    | 18          | 아동/가족  |
    | 19          | 복합장르   |
    | 20          | 국악     |
    | 21          | 오페라    |

    ---

    ## 🏟 3️⃣ 스포츠 카테고리(20) 세부 장르 예시

    | categoryId2 | 세부 장르 |
    | ----------- | ----- |
    | 21          | 축구    |
    | 22          | 야구    |
    | 23          | 농구    |
    | 24          | 배구    |
    | 25          | e스포츠  |
  """)

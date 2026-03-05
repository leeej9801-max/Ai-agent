import streamlit as st
import pandas as pd
import plotly.express as px

# DB 연결 함수
try:
    from db import findAll
    DB_AVAILABLE = True
except:
    DB_AVAILABLE = False


st.set_page_config(
    page_title="인터파크 공연 분석",
    page_icon="🎭",
    layout="wide"
)

st.title("인터파크 공연 관객 분석 대시보드")

# ---------------------------
# 더미 데이터 (DB 없을 때)
# ---------------------------

def get_dummy_data():

    data = [
        {
            "title":"뮤지컬 레미제라블",
            "genre":"MUSICAL",
            "bookingPercent":92,
            "age10Rate":5,
            "age20Rate":35,
            "age30Rate":30,
            "age40Rate":20,
            "age50Rate":10,
            "maleRate":40,
            "femaleRate":60
        },
        {
            "title":"아이유 콘서트",
            "genre":"CONCERT",
            "bookingPercent":98,
            "age10Rate":20,
            "age20Rate":50,
            "age30Rate":15,
            "age40Rate":10,
            "age50Rate":5,
            "maleRate":45,
            "femaleRate":55
        },
        {
            "title":"베토벤 교향곡",
            "genre":"CLASSIC",
            "bookingPercent":60,
            "age10Rate":3,
            "age20Rate":12,
            "age30Rate":25,
            "age40Rate":35,
            "age50Rate":25,
            "maleRate":55,
            "femaleRate":45
        },
        {
            "title":"연극 햄릿",
            "genre":"DRAMA",
            "bookingPercent":75,
            "age10Rate":5,
            "age20Rate":30,
            "age30Rate":35,
            "age40Rate":20,
            "age50Rate":10,
            "maleRate":48,
            "femaleRate":52
        }
    ]

    return pd.DataFrame(data)


# ---------------------------
# DB 데이터 가져오기
# ---------------------------

def get_db_data():

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
        FROM ticket t
        JOIN statistic s
        ON t.id = s.id
    """

    data = findAll(sql)

    df = pd.DataFrame(data)

    return df


# ---------------------------
# 데이터 로딩
# ---------------------------

try:

    if DB_AVAILABLE:
        df = get_db_data()

        if len(df) == 0:
            raise Exception("데이터 없음")

    else:
        raise Exception("DB 없음")

except:

    st.warning("DB 연결 실패 → 더미 데이터 사용")

    df = get_dummy_data()


# ---------------------------
# 장르 선택
# ---------------------------

genre_list = ["전체"] + list(df["genre"].unique())

selected_genre = st.selectbox(
    "장르 선택",
    genre_list
)

if selected_genre != "전체":
    df = df[df["genre"] == selected_genre]


# ---------------------------
# KPI
# ---------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "공연 수",
    len(df)
)

col2.metric(
    "평균 예매율",
    f"{df['bookingPercent'].mean():.1f}%"
)

col3.metric(
    "여성 관객 평균",
    f"{df['femaleRate'].mean():.1f}%"
)


# ---------------------------
# 작품별 예매율
# ---------------------------

st.subheader("작품별 예매율")

fig = px.bar(
    df,
    x="title",
    y="bookingPercent",
    color="genre",
    text="bookingPercent"
)

fig.update_layout(
    xaxis_title="공연",
    yaxis_title="예매율 (%)"
)

st.plotly_chart(fig, use_container_width=True)


# ---------------------------
# 연령대 관객 비율
# ---------------------------

st.subheader("관객 연령대 평균")

age_df = df[[
    "age10Rate",
    "age20Rate",
    "age30Rate",
    "age40Rate",
    "age50Rate"
]].mean().reset_index()

age_df.columns = ["age", "rate"]

fig2 = px.bar(
    age_df,
    x="age",
    y="rate",
    color="age",
    text="rate"
)

fig2.update_layout(
    xaxis_title="연령대",
    yaxis_title="관객 비율 (%)"
)

st.plotly_chart(fig2, use_container_width=True)


# ---------------------------
# 성별 비율
# ---------------------------

st.subheader("관객 성별 비율")

gender_df = df[["maleRate","femaleRate"]].mean().reset_index()

gender_df.columns = ["gender","rate"]

fig3 = px.pie(
    gender_df,
    names="gender",
    values="rate",
    hole=0.4
)

st.plotly_chart(fig3, use_container_width=True)


# ---------------------------
# 장르 vs 연령 히트맵
# ---------------------------

st.subheader("장르별 관객 연령 히트맵")

heatmap_df = df.groupby("genre")[[
    "age10Rate",
    "age20Rate",
    "age30Rate",
    "age40Rate",
    "age50Rate"
]].mean()

fig4 = px.imshow(
    heatmap_df,
    text_auto=True,
    aspect="auto"
)

st.plotly_chart(fig4, use_container_width=True)


# ---------------------------
# 데이터 테이블
# ---------------------------

st.subheader("데이터")

st.dataframe(df)
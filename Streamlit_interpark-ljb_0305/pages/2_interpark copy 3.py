import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="공연 분석", page_icon="🎭", layout="wide")
st.title("🎭 인터파크 공연 분석 (DB 없이 더미 데이터 버전)")

# -----------------------------
# 0) 더미 데이터 생성
# -----------------------------
random.seed(42)

GENRES = ["MUSICAL", "CONCERT", "CLASSIC", "KIDS", "DRAMA", "EXHIBIT"]
PLACES = ["블루스퀘어", "샤롯데씨어터", "예술의전당", "세종문화회관", "대학로극장", "KSPO돔", "고척돔", "코엑스"]

def make_dummy_df(n=60):
    today = pd.Timestamp(datetime.today().date())

    rows = []
    for i in range(n):
        genre = random.choice(GENRES)
        title = f"{genre}_작품_{i+1:02d}"
        place = random.choice(PLACES)

        # 종료일: -10일 ~ +60일 (지난 공연도 일부 섞어둠)
        end_date = today + pd.Timedelta(days=random.randint(-10, 60))

        # 시작일: 종료일보다 1~120일 전
        start_date = end_date - pd.Timedelta(days=random.randint(1, 120))

        booking = round(random.uniform(30, 99), 1)

        # 연령/성별 비율(대충 그럴듯하게, 합 100 근사)
        a10 = random.randint(1, 20)
        a20 = random.randint(5, 45)
        a30 = random.randint(5, 45)
        a40 = random.randint(1, 35)
        a50 = max(1, 100 - (a10 + a20 + a30 + a40))
        # 혹시 100 초과면 조정
        if a50 < 1:
            a50 = 1
            a40 = max(1, 100 - (a10 + a20 + a30 + a50))

        male = random.randint(30, 70)
        female = 100 - male

        rows.append({
            "id": 100000 + i,
            "title": title,
            "genre": genre,
            "placeName": place,
            "playStartDate": start_date,
            "playEndDate": end_date,
            "bookingPercent": booking,
            "age10Rate": a10,
            "age20Rate": a20,
            "age30Rate": a30,
            "age40Rate": a40,
            "age50Rate": a50,
            "maleRate": male,
            "femaleRate": female
        })

    df = pd.DataFrame(rows)
    df["playStartDate"] = pd.to_datetime(df["playStartDate"])
    df["playEndDate"] = pd.to_datetime(df["playEndDate"])
    return df

df_all = make_dummy_df(80)

# -----------------------------
# 1) 장르 선택
# -----------------------------
genre_list = ["전체"] + sorted(df_all["genre"].unique().tolist())
genre_select = st.selectbox("장르 선택", genre_list)

# 화면에 보여줄 df (장르 선택 반영)
df = df_all.copy()
if genre_select != "전체":
    df = df[df["genre"] == genre_select].copy()

today = pd.Timestamp(datetime.today())
df_all["remainDays"] = (df_all["playEndDate"] - today).dt.days
df["remainDays"] = (df["playEndDate"] - today).dt.days

# -----------------------------
# 2) KPI
# -----------------------------
# 7일 이내(종료 안 된 공연만) 마감 공연 수
deadline_7_all = df_all[
    (df_all["playEndDate"] >= today) &
    (df_all["playEndDate"] <= today + pd.Timedelta(days=7))
]
deadline_7 = df[
    (df["playEndDate"] >= today) &
    (df["playEndDate"] <= today + pd.Timedelta(days=7))
]

col1, col2, col3 = st.columns(3)
col1.metric("공연 수", len(df))
col2.metric("평균 예매율", f"{df['bookingPercent'].mean():.1f}%")
col3.metric("7일 이내 마감 공연 수", len(deadline_7))

st.divider()

# -----------------------------
# 3) 전체 선택 시: 장르별 공연 수 + 장르별 평균 예매율(텍스트 + 비교 차트)
# -----------------------------
if genre_select == "전체":
    st.subheader("장르별 공연 수")
    genre_count = df_all.groupby("genre")["id"].count().reset_index()
    genre_count.columns = ["genre", "count"]

    chart_count = alt.Chart(genre_count).mark_bar().encode(
        x=alt.X("genre:N", sort="-y", title="장르"),
        y=alt.Y("count:Q", title="공연 수"),
        tooltip=["genre", "count"]
    ).properties(height=260)

    st.altair_chart(chart_count, use_container_width=True)

    st.subheader("장르별 평균 예매율 (가독성: 텍스트 + 차트)")
    avg_booking = df_all.groupby("genre")["bookingPercent"].mean().sort_values(ascending=False)

    # 텍스트(가시성 좋게)
    for g, v in avg_booking.items():
        st.write(f"- **{g}** : {v:.1f}%")

    avg_df = avg_booking.reset_index()
    avg_df.columns = ["genre", "bookingPercent"]

    chart_avg = alt.Chart(avg_df).mark_bar().encode(
        x=alt.X("genre:N", sort="-y", title="장르"),
        y=alt.Y("bookingPercent:Q", title="평균 예매율(%)"),
        tooltip=["genre", alt.Tooltip("bookingPercent:Q", format=".1f")]
    ).properties(height=260)

    st.altair_chart(chart_avg, use_container_width=True)

else:
    # -----------------------------
    # 4) 장르 선택 시: 해당 장르 TOP10 작품 예매율
    # -----------------------------
    st.subheader(f"{genre_select} 예매율 TOP10 작품")

    top10 = df.sort_values("bookingPercent", ascending=False).head(10)

    chart_top10 = alt.Chart(top10).mark_bar().encode(
        y=alt.Y("title:N", sort="-x", title="작품"),
        x=alt.X("bookingPercent:Q", title="예매율(%)"),
        tooltip=["title", "genre", alt.Tooltip("bookingPercent:Q", format=".1f")]
    ).properties(height=320)

    st.altair_chart(chart_top10, use_container_width=True)

st.divider()

# -----------------------------
# 5) 히트맵: 장르×연령 (항상 전체 기준)
# -----------------------------
st.subheader("장르별 관객 연령 히트맵 (전체 기준)")

age_cols = ["age10Rate", "age20Rate", "age30Rate", "age40Rate", "age50Rate"]

heat_df = df_all.groupby("genre")[age_cols].mean().reset_index()
heat_df = heat_df.melt(id_vars="genre", var_name="age", value_name="rate")

heat_chart = alt.Chart(heat_df).mark_rect().encode(
    x=alt.X("age:N", title="연령대"),
    y=alt.Y("genre:N", title="장르"),
    color=alt.Color("rate:Q", title="비율", scale=alt.Scale(scheme="blues")),
    tooltip=["genre", "age", alt.Tooltip("rate:Q", format=".1f")]
).properties(height=260)

st.altair_chart(heat_chart, use_container_width=True)

st.divider()

# -----------------------------
# 6) 성별 선호 작품: 장르 선택 시에만
#    기준 비율은 슬라이더로 조절 가능
# -----------------------------
if genre_select != "전체":
    st.subheader("성별 선호 작품 (장르 내)")
    threshold = st.slider("선호 기준(%)", min_value=50, max_value=80, value=60, step=5)

    colA, colB = st.columns(2)

    with colA:
        st.markdown(f"### 여성 선호 TOP (femaleRate ≥ {threshold}%)")
        female_candidates = df[df["femaleRate"] >= threshold].copy()
        if len(female_candidates) == 0:
            st.info("조건을 만족하는 작품이 없습니다.")
        else:
            # 조건 만족 중 예매율 높은 작품 1개
            top_female = female_candidates.sort_values("bookingPercent", ascending=False).head(1)
            st.dataframe(top_female[["title", "bookingPercent", "femaleRate", "maleRate", "playEndDate"]])

    with colB:
        st.markdown(f"### 남성 선호 TOP (maleRate ≥ {threshold}%)")
        male_candidates = df[df["maleRate"] >= threshold].copy()
        if len(male_candidates) == 0:
            st.info("조건을 만족하는 작품이 없습니다.")
        else:
            top_male = male_candidates.sort_values("bookingPercent", ascending=False).head(1)
            st.dataframe(top_male[["title", "bookingPercent", "maleRate", "femaleRate", "playEndDate"]])

st.divider()

# -----------------------------
# 7) 마감 임박 공연 TOP5 (7일 이내 / 예매율 높은 순)
#    - KPI는 개수만
#    - TOP5는 "그 중 예매율 높은 순"
# -----------------------------
st.subheader("7일 이내 마감 공연 TOP5 (예매율 높은 순)")

if len(deadline_7) == 0:
    st.info("7일 이내 마감 공연이 없습니다.")
else:
    deadline_top5 = deadline_7.sort_values("bookingPercent", ascending=False).head(5)

    chart_deadline = alt.Chart(deadline_top5).mark_bar().encode(
        y=alt.Y("title:N", sort="-x", title="작품"),
        x=alt.X("bookingPercent:Q", title="예매율(%)"),
        tooltip=["title", "genre", "playEndDate", "remainDays", alt.Tooltip("bookingPercent:Q", format=".1f")]
    ).properties(height=220)

    st.altair_chart(chart_deadline, use_container_width=True)

    st.dataframe(deadline_top5[["title", "genre", "placeName", "playEndDate", "remainDays", "bookingPercent"]])

# -----------------------------
# 8) 원본 데이터 (옵션)
# -----------------------------
with st.expander("원본 데이터 보기"):
    st.dataframe(df_all)
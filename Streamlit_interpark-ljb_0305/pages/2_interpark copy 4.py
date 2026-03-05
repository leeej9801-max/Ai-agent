import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from db import findAll

st.set_page_config(page_title="공연 분석", page_icon="🎭", layout="wide")
st.title("🎭 인터파크 공연 분석 대시보드")

# -----------------------------
# 1) DB에서 JOIN 데이터 로드
# -----------------------------
sql = """
    SELECT
        t.id,
        t.title,
        t.genre,
        t.placeName,
        t.playStartDate,
        t.playEndDate,
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
rows = findAll(sql)
df_all = pd.DataFrame(rows)

if len(df_all) == 0:
    st.error("DB에서 조회된 데이터가 없습니다. (ticket/statistic JOIN 결과가 비어있음)")
    st.stop()

# -----------------------------
# 2) 타입 정리 (DB가 VARCHAR여도 안전하게)
# -----------------------------
df_all["playStartDate"] = pd.to_datetime(df_all["playStartDate"], errors="coerce")
df_all["playEndDate"] = pd.to_datetime(df_all["playEndDate"], errors="coerce")

# bookingPercent가 "72%" 형태면 숫자로
df_all["bookingPercent"] = (
    df_all["bookingPercent"]
    .astype(str)
    .str.replace("%", "", regex=False)
)
df_all["bookingPercent"] = pd.to_numeric(df_all["bookingPercent"], errors="coerce")

rate_cols = ["age10Rate","age20Rate","age30Rate","age40Rate","age50Rate","maleRate","femaleRate"]
for c in rate_cols:
    df_all[c] = pd.to_numeric(df_all[c], errors="coerce")

# 날짜/숫자 핵심 컬럼 결측치 제거(차트 안정성)
df_all = df_all.dropna(subset=["genre", "title", "playEndDate", "bookingPercent"])

today = pd.Timestamp(datetime.today())
df_all["remainDays"] = (df_all["playEndDate"] - today).dt.days

# -----------------------------
# 3) 장르 선택
# -----------------------------
genre_list = ["전체"] + sorted(df_all["genre"].unique().tolist())
genre_select = st.selectbox("장르 선택", genre_list)

df = df_all.copy()
if genre_select != "전체":
    df = df[df["genre"] == genre_select].copy()

df["remainDays"] = (df["playEndDate"] - today).dt.days

deadline_7 = df[
    (df["playEndDate"] >= today) &
    (df["playEndDate"] <= today + pd.Timedelta(days=7))
].copy()

# -----------------------------
# 4) KPI
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("공연 수", int(len(df)))
col2.metric("평균 예매율", f"{df['bookingPercent'].mean():.1f}%")
col3.metric("7일 이내 마감 공연 수", int(len(deadline_7)))

st.divider()

# -----------------------------
# 5) 전체 vs 장르 선택에 따른 메인 차트
# -----------------------------
if genre_select == "전체":
    st.subheader("장르별 평균 예매율 (텍스트 + 비교)")

    avg_booking = df_all.groupby("genre")["bookingPercent"].mean().sort_values(ascending=False)
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
    st.subheader(f"{genre_select} 예매율 TOP10 작품")

    top10 = df.sort_values("bookingPercent", ascending=False).head(10)

    chart_top10 = alt.Chart(top10).mark_bar().encode(
        y=alt.Y("title:N", sort="-x", title="작품"),
        x=alt.X("bookingPercent:Q", title="예매율(%)"),
        tooltip=["title", alt.Tooltip("bookingPercent:Q", format=".1f"), "playEndDate"]
    ).properties(height=320)

    st.altair_chart(chart_top10, use_container_width=True)

st.divider()

# -----------------------------
# 6) 히트맵: 장르 × 연령 (항상 전체 기준)
# -----------------------------
st.subheader("장르별 관객 연령 히트맵 (전체 기준)")

age_cols = ["age10Rate","age20Rate","age30Rate","age40Rate","age50Rate"]
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
# 7) 성별 선호 작품 (장르 선택 시에만)
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
            top_female = female_candidates.sort_values("bookingPercent", ascending=False).head(1)
            st.dataframe(top_female[["title","bookingPercent","femaleRate","maleRate","playEndDate"]])

    with colB:
        st.markdown(f"### 남성 선호 TOP (maleRate ≥ {threshold}%)")
        male_candidates = df[df["maleRate"] >= threshold].copy()
        if len(male_candidates) == 0:
            st.info("조건을 만족하는 작품이 없습니다.")
        else:
            top_male = male_candidates.sort_values("bookingPercent", ascending=False).head(1)
            st.dataframe(top_male[["title","bookingPercent","maleRate","femaleRate","playEndDate"]])

st.divider()

# -----------------------------
# 8) 7일 이내 마감 TOP5 (예매율 높은 순)
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
    st.dataframe(deadline_top5[["title","genre","placeName","playEndDate","remainDays","bookingPercent"]])

with st.expander("원본 데이터 보기"):
    st.dataframe(df_all)
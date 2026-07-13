import streamlit as st
import pandas as pd

st.title("도시 열섬 현상 분석 (서울 vs 양평)")

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")

    # 날짜 처리
    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])

    # 열 이름 통일
    seoul = seoul.rename(columns={"기온(°C)": "서울"})
    yangpyeong = yangpyeong.rename(columns={"기온(°C)": "양평"})

    # 병합
    df = pd.merge(seoul[["일시", "서울"]],
                  yangpyeong[["일시", "양평"]],
                  on="일시")

    return df

df = load_data()

# -----------------------------
# 1년간 기온 변화
# -----------------------------
st.subheader("1년간 기온 변화")

st.line_chart(df.set_index("일시"))

# -----------------------------
# 시각별 평균 기온차
# -----------------------------
st.subheader("시각별 평균 기온차 (서울 - 양평)")

df["시"] = df["일시"].dt.hour
df["기온차"] = df["서울"] - df["양평"]

hourly_diff = df.groupby("시")["기온차"].mean()

st.bar_chart(hourly_diff)

# -----------------------------
# 월별 평균 기온차
# -----------------------------
st.subheader("월별 평균 기온차 (서울 - 양평)")

df["월"] = df["일시"].dt.month

monthly_diff = df.groupby("월")["기온차"].mean()

st.bar_chart(monthly_diff)

# -----------------------------
# 추가 설명
# -----------------------------
st.markdown("""
### 해석 팁
- **기온차(서울 - 양평)가 양수** → 서울이 더 따뜻 → 열섬 효과
- 보통 **밤(특히 18~06시)**에 차이가 커지면 열섬현상이 강한 것
- 겨울철에 더 크게 나타나는 경향 있음
""")

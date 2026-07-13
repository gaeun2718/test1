import streamlit as st
import pandas as pd

st.title("서울·양평 기온과 전력수요 분석")

# -----------------------------

# 데이터 불러오기

# -----------------------------

@st.cache_data
def load_data():
seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
power = pd.read_csv("전력수요.csv", encoding="cp949")

```
# 날짜 변환
seoul["일시"] = pd.to_datetime(seoul["일시"])
yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])
power["일시"] = pd.to_datetime(power["일시"])

# 열 이름 정리
seoul = seoul.rename(columns={"기온(°C)": "서울"})
yangpyeong = yangpyeong.rename(columns={"기온(°C)": "양평"})
power = power.rename(columns={"전력수요(MWh)": "전력수요"})

# 병합
temp_df = pd.merge(
    seoul[["일시", "서울"]],
    yangpyeong[["일시", "양평"]],
    on="일시"
)

power_df = pd.merge(
    seoul[["일시", "서울"]],
    power[["일시", "전력수요"]],
    on="일시"
)

return temp_df, power_df
```

temp_df, power_df = load_data()

# 탭 생성

tab1, tab2 = st.tabs(["열섬 분석", "전력 연결"])

# =============================

# 탭1: 열섬 분석

# =============================

with tab1:
st.subheader("1년간 기온 변화")
st.line_chart(temp_df.set_index("일시"))

```
st.subheader("시각별 평균 기온차 (서울 - 양평)")
temp_df["시"] = temp_df["일시"].dt.hour
temp_df["기온차"] = temp_df["서울"] - temp_df["양평"]
hourly_diff = temp_df.groupby("시")["기온차"].mean()
st.bar_chart(hourly_diff)

st.subheader("월별 평균 기온차 (서울 - 양평)")
temp_df["월"] = temp_df["일시"].dt.month
monthly_diff = temp_df.groupby("월")["기온차"].mean()
st.bar_chart(monthly_diff)
```

# =============================

# 탭2: 전력 연결

# =============================

with tab2:
st.subheader("기온과 전력수요 관계 (산점도)")
st.scatter_chart(
power_df.rename(columns={"서울": "x", "전력수요": "y"})[["x", "y"]]
)

```
st.subheader("기온 구간별 평균 전력수요")

# 기온 구간 나누기 (5도 단위)
bins = range(-20, 45, 5)
power_df["기온구간"] = pd.cut(power_df["서울"], bins=bins)

temp_power = power_df.groupby("기온구간")["전력수요"].mean()
st.bar_chart(temp_power)

st.subheader("월별 평균 전력수요")
power_df["월"] = power_df["일시"].dt.month
monthly_power = power_df.groupby("월")["전력수요"].mean()
st.bar_chart(monthly_power)
```

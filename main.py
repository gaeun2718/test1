import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="도시 열섬현상 및 전력수요 분석", layout="wide")
st.title("🏙️ 서울-양평 열섬현상 및 기온별 전력수요 분석 대시보드")
st.markdown("본 웹앱은 2025년 시간별 데이터를 바탕으로 서울과 양평의 기온을 비교하여 도시 열섬현상을 분석하고, 서울 기온과 전력수요의 상관관계를 살펴봅니다.")

# 2. 데이터 로드 및 전처리 함수
@st.cache_data
def load_all_data():
    # [공통] 한글 파일 처리를 위해 encoding="cp949" 적용
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형태로 변환
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
    power['일시'] = pd.to_datetime(power['일시'])
    
    # 필요한 컬럼 추출 및 이름 구체화
    seoul = seoul[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울기온'})
    yangpyeong = yangpyeong[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평기온'})
    power = power[['일시', '전력수요(MWh)']]
    
    # 동일 일시 기준으로 세 파일 모두 결합
    merged = pd.merge(seoul, yangpyeong, on='일시', how='inner')
    merged = pd.merge(merged, power, on='일시', how='inner')
    
    # 파생 변수(기온차, 월, 시각, 기온구간) 생성
    merged['기온차(서울-양평)'] = merged['서울기온'] - merged['양평기온']
    merged['월'] = merged['일시'].dt.month
    merged['시각'] = merged['일시'].dt.hour
    
    # ②번 문항을 위한 5도 단위 기온 구간 계산 (예: 23.5도 -> 20도 구간)
    merged['기온구간'] = (merged['서울기온'] // 5) * 5
    
    return merged

try:
    df = load_all_data()
    
    # 탭 구성 (st.tabs)
    tab1, tab2 = st.tabs(["🌡️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])
    
    # --- [탭1: 열섬 분석] ---
    with tab1:
        st.header("도시 열섬현상(Urban Heat Island) 분석")
        st.markdown("서울(대도시)과 양평(근교 농촌)의 기온 차이를 다각도로 분석합니다.")
        
        # ① 1년간 두 지역 기온 변화 (선그래프)
        st.subheader("① 1년간 두 지역 기온 변화")
        chart_data1 = df.set_index('일시')[['서울기온', '양평기온']]
        st.line_chart(chart_data1)
        
        col1_1, col1_2 = st.columns(2)
        
        with col1_1:
            # ② 시각(0~23시)별 평균 기온차, 서울-양평 (막대그래프)
            st.subheader("② 시각별 평균 기온차 (서울-양평)")
            chart_data2 = df.groupby('시각')['기온차(서울-양평)'].mean()
            st.bar_chart(chart_data2)
            st.caption("💡 도심 콘크리트의 방열 현상 등으로 인해 대개 밤~새벽 시간대에 두 지역의 기온차가 두드러집니다.")
            
        with col1_2:
            # ③ 월(1~12월)별 평균 기온차, 서울-양평 (막대그래프)
            st.subheader("③ 월별 평균 기온차 (서울-양평)")
            chart_data3 = df.groupby('월')['기온차(서울-양평)'].mean()
            st.bar_chart(chart_data3)
            st.caption("💡 일사량 변화 및 대기 순환 특성에 따른 월별 열섬 강도의 변동입니다.")

    # --- [탭2: 전력 연결] ---
    with tab2:
        st.header("서울 기온과 전력수요의 관계 분석")
        st.markdown("외기 온도 변화가 서울의 전기 소비(냉·난방)에 미치는 요인을 살펴봅니다.")
        
        # ① 기온(가로)과 전력수요(세로)의 산점도
        st.subheader("① 기온과 전력수요의 상관관계 (산점도)")
        scatter_data = df[['서울기온', '전력수요(MWh)']]
        # 외부 시각화 툴 없이 streamlit 고유 기능인 scatter_chart 활용
        st.scatter_chart(scatter_data, x='서울기온', y='전력수요(MWh)')
        st.caption("💡 추운 겨울(난방)과 더운 여름(냉방) 양쪽 끝단에서 전력수요가 올라가는 형태를 관찰할 수 있습니다.")
        
        col2_1, col2_2 = st.columns(2)
        
        with col2_1:
            # ② 기온 구간별 평균 전력수요 (막대그래프)
            st.subheader("② 기온 구간별 평균 전력수요")
            df_grouped_temp = df.groupby('기온구간')['전력수요(MWh)'].mean().reset_index()
            # 그래프 가독성을 위해 구간 범위를 텍스트로 라벨링 ('15~20°C' 등)
            df_grouped_temp['기온구간명'] = df_grouped_temp['기온구간'].apply(lambda x: f"{int(x)}~{int(x+5)}°C")
            df_grouped_temp = df_grouped_temp.set_index('기온구간명')['전력수요(MWh)']
            st.bar_chart(df_grouped_temp)
            st.caption("💡 기온 구간 변화에 따라 냉난방 전력수요가 증가하기 시작하는 지점을 파악할 수 있습니다.")
            
        with col2_2:
            # ③ 월(1~12월)별 평균 전력수요 (막대그래프)
            st.subheader("③ 월별 평균 전력수요")
            chart_data_month_power = df.groupby('월')['전력수요(MWh)'].mean()
            st.bar_chart(chart_data_month_power)
            st.caption("💡 냉방 중심의 하절기(7~8월)와 난방 중심의 동절기(12~1월)에 평균 소비량이 크게 기록됩니다.")

except Exception as e:
    st.error(f"⚠️ 데이터를 정상적으로 읽어오지 못했습니다. '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 세 파일이 한 폴더에 있는지 확인해 주세요. (에러 로그: {e})")

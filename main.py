import streamlit as st
 
st.title("김희연 바보")
st.write("노직도 바보임")

지역 = st.selectbox("지역을 골라 보세요", ["서울", "양평", "부산"])
st.write("당신이 고른 지역:", 지역)


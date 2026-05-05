import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime

# 오늘 날짜 자동 가져오기
today_date = datetime.now().strftime('%Y-%m-%d')

# 수정된 부분: 직접 키를 적지 않고 Streamlit 설정값에서 가져옵니다.
# 'GOOGLE_API_KEY'라는 이름의 비밀 열쇠를 사용합니다.
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("API 키 설정이 필요합니다. Streamlit Cloud 설정에서 Secrets를 추가해주세요.")
    st.stop()

model = genai.GenerativeModel('gemini-2.5-flash')

# 3. 지시문에 오늘 날짜 주입하기
# f""" 를 사용하면 {today_date} 자리에 실제 오늘 날짜가 쏙 들어갑니다.
prompt_text = f"""
[역할]
너는 제주도 렌트카 업체의 외국인 및 주한미군 서류 검수 전문가야. 고객이 제출한 서류를 분석하여 대한민국 법규 및 업체 규정에 따른 대여 가능 여부를 엄격하게 판독해.

[분석 기준 날짜]
- **현재 날짜: {today_date}** (모든 유효기간 및 날짜 계산의 절대적 기준)

[전사 공통 필수 대여 조건]
- 만 나이: 대여일({today_date}) 기준 만 26세 이상 필수.
- 운전 경력: {today_date} 기준 본국 또는 USFK 면허 취득 후 1년 경과 필수.

[검수 세부 기준]
- 성함 일치: 여권과 모든 제출 서류의 영문 스펠링 일치 확인.
- 일반 외국인: 국제면허증(IDP) 유효기간 및 입국일 1년 미만 확인 (입국일이 {today_date} 기준 1년 이내인지).
- 주한미군: USFK 면허증(130EK) + 본국 면허증 + 여권 대조.

[응답 형식]
결과를 다음 구조로 출력해줘:
최종 판정: [대여 가능 / 대여 불가]
대상 구분: [일반 외국인 / 주한미군]
불가 사유: (기준 미달 시 상세 기재)
상세 대조표 (항목|검수 내용|판정)
"""

# 4. 앱 화면 구성 및 실행 로직 (기존과 동일)
st.set_page_config(page_title="해피 외국인 서류검수", layout="centered")
st.title("🔍외국인 서류 검수 시스템")
st.write(f"📅 오늘 날짜 {today_date}") # 화면에도 오늘 날짜를 표시해줍니다.

uploaded_files = st.file_uploader("사진을 선택하세요", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if st.button("검수 시작"):
    if uploaded_files:
        with st.spinner('AI가 오늘 날짜 기준으로 분석 중입니다...'):
            try:
                images = [Image.open(f) for f in uploaded_files]
                response = model.generate_content([prompt_text] + images)
                st.success("분석 완료!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"오류: {e}")

# 앱 맨 아래쪽에 서명 추가하기
st.markdown("---") # 얇은 가로줄을 하나 그어줍니다.
st.markdown(
    "<div style='text-align: center; color: #b0b0b0; font-size: 13px;'>"
    "<b>Created by 김성결</b>♡ "
    "</div>", 
    unsafe_allow_html=True
)

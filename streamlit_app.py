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

[운영 원칙: 데이터 격리 및 보안]
1인 1대화 원칙: 각 대화 세션은 오직 한 명의 고객 데이터만 처리한다.
혼동 금지: 이전 대화나 다른 세션의 정보를 현재 검수에 절대 인용하지 않는다.

[전사 공통 필수 대여 조건 (Critical)]
만 나이: 대여일({today_date}) 기준 만 26세 이상 필수. (여권상 생년월일로 계산)
운전 경력: 아래 기준 중 하나를 충족하여 경력 1년 이상 필수.
일반 외국인: 본국(로컬) 면허 취득일로부터 {today_date} 기준 1년 경과.
주한미군:
(1순위) USFK 면허증상 발급일로부터 {today_date} 기준 1년 경과 시 즉시 승인.
(2순위) USFK 경력이 1년 미만일 경우, 본국(로컬) 면허증의 경력을 확인하여 합산 1년 이상이면 승인.

[검수 세부 기준]
성함 일치 여부: 모든 서류(IDP, 로컬 면허증, 여권, USFK 면허증 등)의 영문 스펠링이 여권과 완벽히 일치해야 함.
일반 외국인 (IDP 소지자):
여권/입국일: 대한민국 입국일로부터 1년이 지나지 않았어야 함.
협약국 유효기간: 제네바 협약(발급일로부터 1년), 비엔나 협약(발급일로부터 3년). {today_date} 기준으로 유효기간이 남아있는지 확인. 비공식 기관 발행본은 대여 불가.
주한미군 (USFK 소지자):
필수 서류: 주황색 주한미군 면허증(USFK Form 130EK) + 본국(로컬) 면허증 + 여권.
차종(인승) 검증:
Class 1 (Private): 9인승 이하 승용차만 가능.
Class 2 (Commercial): 11~15인승 승합차 가능.

[응답 형식]
결과를 다음 구조로 출력해줘:
최종 판정: [대여 가능 / 대여 불가]
대상 구분: [일반 외국인 / 주한미군]
불가 사유: (기준 미달 시 해당 항목을 구체적으로 나열)

상세 대조표:
| 항목 | 검수 내용 | 판정 | 이유 |
| :--- | :--- | :--- | :--- |
| 여권 확인 | 첨부 사진이 실제 여권이 맞는지 확인 | [확인완료 / 불가] | (국적 정보 기재) |
| 로컬면허 확인 | 신분증 등이 아닌 실제 운전면허증이 맞는지 확인 | [확인완료 / 불가] | **(서류에 적힌 실제 발급일(ISSUE)을 YYYY-MM-DD 형식으로 반드시 포함하여 기재, 미제출이나 식별 불가 시 사유 기재)** |
| IDP 정식발급 여부 | 사설 기관 발급 여부 확인 (IAA 등 불가) | [확인완료 / 불가] | (발급 기관 정보 기재) |
| 성함 일치 여부 | 모든 서류 스펠링 대조 | [확인완료 / 불일치] | (일치 여부 및 영문 성함 기재) |
| 만 나이 | {today_date} 기준 만 26세 이상 | [확인완료 / 미달] | (생년월일 및 만 나이 기재) |
| 운전 경력 | 로컬/USFK 면허 취득 후 1년 경과 | [확인완료 / 불가] | **(로컬/USFK 면허의 실제 발급일을 바탕으로 경력 계산 근거 기재)** |
| 협약국 여부 | 제네바 또는 비엔나 협약국 리스트 포함 여부 | [확인완료 / 불가] | (해당 국가 기재) |
| IDP 유효기간 | 국제면허증 유효기간 만료 여부 | [확인완료 / 불가] | **(서류에 적힌 실제 발급일(ISSUE)과 만료일(EXPIRY)을 YYYY-MM-DD 형식으로 모두 반드시 포함하여 기재)** |

[현장 확인 안내] ※ 최근 한국 입국 시 입국 도장이나 스티커를 날인하지 않는 경우가 많으므로, 고객의 실제 입국일이 1년 미만인지 여부는 직원이 현장에서 직접 확인해 주세요.
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

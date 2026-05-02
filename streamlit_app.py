import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. API 키 설정 (주인님의 실제 키를 아래 따옴표 안에 넣어주세요)
# 주의: AI Studio에서 '새 프로젝트'로 키를 다시 발급받는 것을 추천합니다.
API_KEY = "주인님의_실제_API_키_입력"
genai.configure(api_key=API_KEY)

# 2. 모델 설정 (404 오류 방지를 위해 가장 안정적인 이름 사용)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. 검수 지시문 (프롬프트)
prompt_text = """
[역할]
너는 제주도 렌트카 업체의 외국인 및 주한미군 서류 검수 전문가야. 고객이 제출한 서류를 분석하여 대한민국 법규 및 업체 규정에 따른 대여 가능 여부를 엄격하게 판독해.

[운영 원칙]
1인 1대화 원칙: 각 대화 세션은 오직 한 명의 고객 데이터만 처리한다.

[전사 공통 필수 대여 조건]
- 만 나이: 대여일 기준 만 26세 이상 필수. (여권상 생년월일로 계산)
- 운전 경력: 본국 면허 또는 USFK 면허 취득 후 1년 이상 경과 필수.

[검수 세부 기준]
- 성함 일치: 여권과 모든 제출 서류의 영문 스펠링 일치 확인.
- 일반 외국인: 국제면허증(IDP) 유효기간 및 입국일 1년 미만 확인.
- 주한미군: USFK 면허증(130EK) + 본국 면허증 + 여권 대조.

[응답 형식]
결과를 다음 구조로 출력해줘:
최종 판정: [대여 가능 / 대여 불가]
대상 구분: [일반 외국인 / 주한미군]
불가 사유: (기준 미달 시 상세 기재)
상세 대조표 (항목|검수 내용|판정)
"""

# 4. 앱 화면 구성
st.set_page_config(page_title="제주 해피렌트카 서류 검수기", layout="centered")
st.title("🚗 외국인 서류 검수 시스템")
st.info("여권, 국제면허증, 로컬면허증 사진을 업로드해주세요.")

# 5. 실행 로직
uploaded_files = st.file_uploader("사진을 선택하세요 (여러 장 가능)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if st.button("검수 시작"):
    if uploaded_files:
        if API_KEY == "주인님의_실제_API_키_입력":
            st.error("잠깐! 코드 8번째 줄에 주인님의 실제 API 키를 넣으셔야 합니다.")
        else:
            with st.spinner('AI가 서류를 분석 중입니다...'):
                try:
                    images = [Image.open(f) for f in uploaded_files]
                    # 지시문과 사진을 하나의 리스트로 구성
                    request_parts = [prompt_text] + images
                    response = model.generate_content(request_parts)
                    st.success("분석이 완료되었습니다!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
                    st.info("팁: API 키가 방금 발급되었다면 활성화까지 1~2분이 걸릴 수 있습니다.")
    else:
        st.warning("분석할 사진을 먼저 올려주세요.")

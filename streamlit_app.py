import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. API 키 설정 (선택하신 키 그대로 적용)
genai.configure(api_key="AIzaSyDoTAUwFFLp9HF_TQNr0GNS5XdlH0fUKqI")

# 2. 가장 안정적인 모델 선택 (지시문 충돌 방지)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. 프롬프트(지시문) 통합
prompt_text = """
[역할]
너는 제주도 렌트카 업체의 외국인 및 주한미군 서류 검수 전문가야. 고객이 제출한 서류를 분석하여 대한민국 법규 및 업체 규정에 따른 대여 가능 여부를 엄격하게 판독해.

[운영 원칙: 데이터 격리 및 보안]
1인 1대화 원칙: 각 대화 세션은 오직 한 명의 고객 데이터만 처리한다.
혼동 금지: 이전 대화나 다른 세션의 정보를 현재 검수에 절대 인용하지 않는다.

[전사 공통 필수 대여 조건 (Critical)]
만 나이: 대여일 기준 만 26세 이상 필수. (여권상 생년월일로 계산)
운전 경력: 아래 기준 중 하나를 충족하여 경력 1년 이상 필수.
일반 외국인: 본국(로컬) 면허 취득일로부터 1년 경과.
주한미군:
(1순위) USFK 면허증상 발급일로부터 1년 경과 시 즉시 승인.
(2순위) USFK 경력이 1년 미만일 경우, 본국(로컬) 면허증의 경력을 확인하여 합산 1년 이상이면 승인.

[검수 세부 기준]
성함 일치 여부: 모든 서류(IDP, 로컬 면허증, 여권, USFK 면허증 등)의 영문 스펠링이 여권과 완벽히 일치해야 함.
일반 외국인 (IDP 소지자):
여권/입국일: 입국일로부터 1년 미만이어야 함.
협약국 유효기간: 제네바(1년), 비엔나(3년). 비공식 기관 발행본은 대여 불가.
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
항목|검수 내용|판정
성함 일치|여권 vs 제출 서류 일치 여부|[일치 / 불일치]
연령 확인|만 나이 계산 (현재 2026년 기준)|[만 00세 / 적합 또는 미달]
운전 경력|USFK(우선) 또는 로컬 면허 경력 1년 확인|[0년 0개월 / 적합 또는 미달]
입국/신분|입국일 1년 미만 또는 USFK 신분 확인|[확인 완료 / 미달]
면허 유효성|IDP 유형 및 유효기간 / USFK 면허 상태|[정상 / 불량]
운행 가능 인승|요청 차량 대비 면허 등급(Class) 확인|[9인승 이하 / 15인승까지]

[분석 요청]
위 기준에 따라, 내가 지금 첨부한 서류 사진들을 정밀 분석해서 최종 판정표를 작성해줘.
"""

# 4. 앱 화면 구성
st.set_page_config(page_title="서류 검수 매니저", layout="centered")
st.title("🚗 외국인 서류 검수 시스템")
st.info("여권, 국제면허증, 로컬면허증 사진을 모두 업로드해주세요.")

# 5. 서류 검수 실행 로직
uploaded_files = st.file_uploader("사진을 선택하세요 (여러 장 가능)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if st.button("검수 시작"):
    if uploaded_files:
        with st.spinner('AI가 서류를 정밀 분석 중입니다...'):
            try:
                # 사진들을 열고 지시문과 하나로 합치기
                images = [Image.open(f) for f in uploaded_files]
                request_contents = [prompt_text] + images
                
                # 분석 요청
                response = model.generate_content(request_contents)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
    else:
        st.warning("분석할 사진을 먼저 올려주세요.")

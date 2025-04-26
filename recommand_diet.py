import streamlit as st
import openai
from serpapi import Client
import requests

class Recommand_Diet():
    def __init__(self):
        self.api_key = None
        self.google_api_key = None
        self.setup_page()

    def setup_page(self):
        st.set_page_config(page_title="Plan M", page_icon="🥗")
        st.title("🥗 :red[Plan] M")

        user_input = st.text_input("원하시는 조건을 입력해주세요! (일자, 예산, 목적 등)")
        meal_button = st.button("식단만들기")

        with st.sidebar:
            self.api_key = st.text_input("OpenAI API Key를 입력하세요", key="openai_api_key", type="password")
            self.google_api_key = st.text_input("구글 API Key를 입력하세요", key="google_api_key", type="password")
            process = st.button("실행")
        if process:
            if not self.api_key:
                st.warning("❌ OpenAI API Key를 입력하세요!!")
                st.stop()

        if meal_button:
            if not self.api_key:
                st.warning("❗OpenAI API Key를 먼저 입력하세요!!")
                st.stop()

            openai.api_key = self.api_key
            if user_input:
                with st.spinner("🤖 검색중..."):
                    plan = self.generate_meal_plan(user_input)
                    st.text_area("🍽️ 생성된 식단", plan, height=500)
                    st.subheader("🍴 식단 미리보기")
                    self.display_meal_images(plan)

    def generate_meal_plan(self, user_input):
        prompt = f"""
        기본적으로 {user_input}의 조건으로 식단을 만들고,
        1. 각 끼니를 아침/점심/저녁으로 구분하기
        2. 메뉴명은 한단어로 표시
        2. 식단별로 재료 및 칼로리 표시
        3. 예산이 있다면 예산에 맞춰 식단 만들기
        4. 목적에 맞는 식단짜기 (예시 : 다이어트 목적, 간단한 식단, 벌크업 등)
        5. 마지막에 필요한 재료 리스트를 정리해줘        
        """
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def search_image_url(self, menu, api_key):
        client = Client(api_key=api_key)  # Client로 바꿈
        params = {
            "engine": "google",
            "q": menu + " food",
            "tbm": "isch",  # 이미지 검색 모드
        }
        results = client.search(params)
        if "images_results" in results:
            return results["images_results"][0]["thumbnail"]
        else:
            return None

    def display_meal_images(self, plan_text):
        lines = plan_text.splitlines()
        for line in lines:
            if any(meal in line for meal in ["아침", "점심", "저녁"]):
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        menu = parts[1].strip().split()[0]
                        if menu:
                            st.markdown(f"### 🍽️ {menu}")
                            menu_eng = self.auto_translate_text(menu)
                            image_url = self.search_image_url(menu_eng, self.google_api_key)
                            if image_url:
                                st.image(image_url, caption=menu)
                            else:
                                st.warning(f"❗ {menu} 이미지 검색 실패")

                            coupang_link = self.search_coupang_product(menu)
                            st.markdown(f"[🛒 {menu} 구매하러 가기]({coupang_link})")

    def auto_translate_text(self, text):
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "ko",
            "tl": "en",
            "dt": "t",
            "q": text
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json()
            translated_text = result[0][0][0]
            return translated_text
        else:
            return text

    def search_coupang_product(self, query):
        return f"https://www.coupang.com/np/search?component=&q={query.replace(' ', '')}"

    def extract_meal_name(self, plan_text):
        meal_names = []
        for line in plan_text.splitlines():
            if any(meal in line for meal in ["아침", "점심", "저녁"]):
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        menu = parts[1].strip()
                        words = menu.split()
                        if len(words) >= 2:
                            menu = " ".join(words[:-1])
                            calorie = words[-1]
                            meal_name = f"{menu}({calorie})"
                        else:
                            meal_name = f"{menu}"
                        meal_names.append(meal_name)
        return "\n".join(meal_names)

if __name__ == '__main__':
    app = Recommand_Diet()

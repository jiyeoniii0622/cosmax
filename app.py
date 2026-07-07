import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="What's in my kitchen?",
    page_icon="🍳",
    layout="wide",
)

BASE_DIR = Path(__file__).parent


def load_app_html() -> str:
    """index.html을 읽어와서 recipes.js 내용을 인라인으로 삽입한다.

    Streamlit의 components.html은 페이지를 샌드박스 iframe(HTML 문자열)으로
    렌더링하기 때문에 <script src="recipes.js">처럼 같은 폴더의 상대경로
    파일을 불러올 수 없다. 그래서 배포 시에는 recipes.js 내용을 통째로
    <script> 태그 안에 넣어 함께 전달한다.
    """
    html = (BASE_DIR / "index.html").read_text(encoding="utf-8")
    recipes_js = (BASE_DIR / "recipes.js").read_text(encoding="utf-8")

    html = html.replace(
        '<script src="recipes.js"></script>',
        f"<script>\n{recipes_js}\n</script>",
    )
    return html


html_content = load_app_html()

# height는 필요에 맞게 조절 가능. scrolling=True로 iframe 내부 스크롤 허용.
components.html(html_content, height=1600, scrolling=True)

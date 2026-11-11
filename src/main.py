import streamlit as st
import streamlit.components.v1 as components
from fa_diacritizer.model import diacritize

# ---------- page setting ----------
st.set_page_config(
    page_title="farsi diacritizer",
    page_icon="📝",
    layout="centered",
)

# ---------- RTL style and beautification ----------
st.markdown(
    """
    <style>
        .stApp { direction: rtl; }
        textarea, input { direction: rtl; text-align: right; }
        .stTextArea label, .stTextInput label { direction: rtl; text-align: right; }
        h1, h2, h3, p, span, div { direction: rtl; text-align: right; }
        .copy-btn {
            padding: 0.5rem 1.2rem;
            background: #16a34a;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-family: inherit;
            font-size: 15px;
            margin-top: 4px;
        }
        .copy-btn:hover { background: #15803d; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Header ----------
st.title("📝farsi diacritizer ")
st.caption("input your text. give output as txt file or copy it")

# ---------- input ----------
input_text = st.text_area(
    "input text",
    height=200,
    placeholder="input your text",
    key="input_text",
)

col1, col2 = st.columns([1, 1])
with col1:
    process_btn = st.button("🚀 Processing", type="primary", use_container_width=True)
with col2:
    clear_btn = st.button("🗑️ delete", use_container_width=True)

if clear_btn:
    st.session_state.pop("output_text", None)
    st.rerun()

# ---------- Processing ----------
if process_btn:
    if input_text.strip():
        st.session_state["output_text"] = diacritize(input_text)
    else:
        st.warning("please first input your text")

# ---------- output ----------
if "output_text" in st.session_state:
    output = st.session_state["output_text"]
    st.subheader("📤 output")
    st.code(output, language=None)
    

    # txt download button
    st.download_button(
        label="📥 Doemload as TXT",
        data=output.encode("utf-8"),
        file_name="output.txt",
        mime="text/plain; charset=utf-8",
        use_container_width=True,
    )
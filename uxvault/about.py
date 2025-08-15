# Solutions
# Finding insights in one place has never been easier with UX Vault. Designed for UX professionals to efficiently conduct card sorting studies, generating real-time results such as dendrograms and similarity matrices, as well as exporting data for further analysis. Learn more about our project on our GitHub , and stay tuned for future tools to boost your UX research.

# ← Go Back


import streamlit as st


text_to_justify = "Solutions"
content = r"""Finding insights in one place has never been easier with UX Vault. 
Designed for UX professionals to efficiently conduct card sorting studies, 
generating real-time results such as dendrograms and similarity matrices, 
as well as exporting data for further analysis. 
Learn more about our project on our"""
text_link = "GitHub"
hyperlink = "https://github.com/cronozul/p_cards"

ending = """and stay tuned for future tools to boost your UX research."""


with st.container(horizontal=False, gap="medium", horizontal_alignment="center"):
    st.markdown(f"<h1 style='text-align: center;'>{text_to_justify}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{content} <a href='{hyperlink}'>{text_link}</a> {ending}</p>", unsafe_allow_html=True)
    with st.container(horizontal=True, gap="medium", horizontal_alignment="right"):
        if st.button("Go Back",type='primary'):
            st.switch_page("intro.py")
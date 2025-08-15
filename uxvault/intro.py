# The free UX research platform: simple and accessible
# A free, open-source tool designed to simplify the UX Research process.
# Create a card sorting
# Learn more
import streamlit as st

text_to_justify = "The free UX research platform: simple and accessible"
subtitle = "A free, open-source tool designed to simplify the UX Research process."

with st.container(horizontal=False, gap="medium", horizontal_alignment="center"):
    st.markdown(f"<h1 style='text-align: center;'>{text_to_justify}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align: center;'>{subtitle}</h2>", unsafe_allow_html=True)
    with st.container(horizontal=True, gap="medium", horizontal_alignment="center"):
        if st.button("Create a card sorting",type="primary"):
            st.switch_page("create_card_sorting.py")
        
        if st.button("Learn more"):
            st.switch_page("about.py") 
        # st.page_link(label="Create a card sorting", page="create_card_sorting.py", icon=":material/create:")
        # st.page_link(label="Learn more", page="about.py")

import streamlit as st
import os

# Change working directory to script directory
# os.chdir(os.path.dirname(os.path.abspath(__file__)))

BIG_LOGO = 'uxvault/assets/ux-vault-logo-white.svg'
SMALL_LOGO = 'uxvault/assets/ux-vault-logo-mini.svg'
st.set_page_config(
    page_title="UX Vault",
    page_icon=SMALL_LOGO,
    layout="centered",
    initial_sidebar_state="expanded",)

# detect 
st.logo(image = BIG_LOGO,size="large")


pg = st.navigation({
    "Who we are": [st.Page("uxvault/intro.py",icon=':material/home:' ,title="Home") , st.Page("uxvault/about.py",icon=':material/info:' ,title="About Us")],
    "Tools": [st.Page("uxvault/create_card_sorting.py",icon=':material/create:' ,title="Create Card Sorting"),
              st.Page("uxvault/solve_card_sorting.py",icon=':material/checklist_rtl:' ,title="Solve Card Sorting"),
              st.Page("uxvault/dashboard.py",icon=':material/dashboard:' ,title="Dashboard")]
},
position='top')

pg.run()

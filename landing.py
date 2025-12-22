import importlib
import streamlit as st
import os


# Change working directory to script directory
# os.chdir(os.path.dirname(os.path.abspath(__file__)))

BIG_LOGO = 'uxvault/assets/ux-vault-logo-white.svg'
SMALL_LOGO = 'uxvault/assets/ux-vault-logo-mini.svg'
st.set_page_config(
    page_title="UX Vault",
    page_icon=SMALL_LOGO,
    # layout="centered",
    initial_sidebar_state="expanded",)

# detect 
st.logo(image = BIG_LOGO,size="large") #,link="https://github.com/gquinche/uxvault")



basic_page_setup = {
    
    "Tools": [st.Page("uxvault/create_card_sorting.py",icon=':material/create:' ,title="Create Card Sorting"),
              st.Page("uxvault/solve_card_sorting.py",icon=':material/checklist_rtl:' ,title="Solve Card Sorting")],
    "Who we are": [st.Page("uxvault/intro.py",icon=':material/home:' ,title="Home") , st.Page("uxvault/about.py",icon=':material/info:' ,title="About Us")],

}

extra_dict = {"User" : [st.Page("uxvault/log_in.py",icon=':material/login:' ,title="Log In/Sign Up"),],}
if True or st.user.is_logged_in:
    extra_dict.update(basic_page_setup)
    basic_page_setup = extra_dict
    logged_in_tools = [st.Page("uxvault/create_card_sorting.py",icon=':material/create:' ,title="Create Card Sorting"),
                       st.Page("uxvault/solve_card_sorting.py",icon=':material/checklist_rtl:' ,title="Solve Card Sorting"),
                       st.Page("uxvault/dashboard.py",icon=':material/dashboard:' ,title="Dashboard")]
    basic_page_setup["Tools"] = logged_in_tools
    
else:
    basic_page_setup.update(extra_dict)

    
pg = st.navigation(basic_page_setup,
                    position='top')

pg.run()
# Add a button for the GitHub repository in the bottom right corner
st.markdown(
"""
<style>
.github-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000; /* Ensure it's above other content */
}
</style>
<div class="github-button">
    <a href="https://github.com/gquinche/uxvault" target="_blank"> Our Github
    </a>
</div>
""",
unsafe_allow_html=True
)

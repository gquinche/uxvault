import streamlit as st
import os

# Change working directory to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

BIG_LOGO = './assets/ux-vault-logo-white.svg'
SMALL_LOGO = './assets/ux-vault-logo-mini.svg'
st.set_page_config(
    page_title="UX Vault",
    page_icon=SMALL_LOGO,
    layout="centered",
    initial_sidebar_state="expanded",)
st.logo(image = BIG_LOGO,icon_image=SMALL_LOGO,size="large")

    # >>> import streamlit as st
    # >>>
    # >>> pages = {
    # ...     "Your account": [
    # ...         st.Page("create_account.py", title="Create your account"),
    # ...         st.Page("manage_account.py", title="Manage your account"),
    # ...     ],
    # ...     "Resources": [
    # ...         st.Page("learn.py", title="Learn about us"),
    # ...         st.Page("trial.py", title="Try it out"),
    # ...     ],
    # ... }
    # >>>
    # >>> pg = st.navigation(pages)
    # >>> pg.run()

# uxvault/about.py uxvault/create_card_sorting.py uxvault/dashboard.py uxvault/home.py uxvault/landing page.py uxvault/solve_card_sorting.py
pg = st.navigation({
    "Home": [st.Page("./intro.py",icon=':material/home:' ,title="Home")],
    "About": [st.Page("./about.py",icon=':material/info:' ,title="About Us")],
    "Tools": [st.Page("./create_card_sorting.py",icon=':material/create:' ,title="Create Card Sorting"),
              st.Page("./solve_card_sorting.py",icon=':material/checklist_rtl:' ,title="Solve Card Sorting"),
              st.Page("./dashboard.py",icon=':material/dashboard:' ,title="Dashboard")]
})

pg.run()

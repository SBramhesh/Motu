import streamlit as st
st.set_page_config(
    page_title="5G Nokia Scripting",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",

)
import streamlit_authenticator as stauth
import aloha_dict
import nrcell_replace
import vswrapp
import attLogs
import streamapp



# nokia.py
# import fireStoreapp
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """

st.markdown(hide_st_style, unsafe_allow_html=True)
names = ['Nokia User', 'Integer User']
usernames = ['Nokia', 'Integer']
passwords = ['Nokia123', 'Nokia456']
hashed_passwords = stauth.hasher(passwords).generate()

authenticator = stauth.authenticate(names, usernames, hashed_passwords,
                                    'nokia_integer', 'wnqwedhbepwopmmbvbxv', cookie_expiry_days=30)
name, authentication_status = authenticator.login('Nokia Login', 'main')

if authentication_status:
    st.sidebar.write('Logged in as *%s*' % (name))
    PAGES_ADMIN = {
        "Upload  New File (RTWP + VSWR)": streamapp,
        # "Files Processed (Raw Data + Summary)": fireStoreapp,
        "Process AT&T Log Files (RSSI)": attLogs,
        "5G Nokia Scripting": nrcell_replace,
        "Admin Module": aloha_dict,
    }
    PAGES = {
        "Upload  New File (RTWP + VSWR)": streamapp,
        # "Files Processed (Raw Data + Summary)": fireStoreapp,
        "Process AT&T Log Files (RSSI)": attLogs,
        "5G Nokia Scripting": nrcell_replace,
    }
    st.sidebar.title('Nokia Main Menu')
    if name == 'Integer User':
        PAGES = PAGES_ADMIN
    selection = st.sidebar.radio(
        f"Navigate to:", list(PAGES.keys()))
    page = PAGES[selection]
    page.app()
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

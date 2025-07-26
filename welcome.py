import streamlit as st
from streamlit_lottie import st_lottie
from utils.lottie_helper import load_lottie_url
import time

def show_lottie_welcome():
    if 'welcome_shown' not in st.session_state:
        st.session_state.welcome_shown = True  # ensure it runs only once

        lottie_url = "https://assets1.lottiefiles.com/packages/lf20_1pxqjqps.json"
        lottie_json = load_lottie_url(lottie_url)

        placeholder = st.empty()  # create a placeholder container

        with placeholder.container():
            st.markdown("## 👋 Welcome to the KPI & Chart Generator!")
            st.markdown("Upload your CSV, generate KPIs, and visualize charts easily.")
            if lottie_json:
                st_lottie(lottie_json, height=300, key="welcome_lottie")

        time.sleep(10)  # wait 3 seconds
        placeholder.empty()  # auto-dismiss the welcome section

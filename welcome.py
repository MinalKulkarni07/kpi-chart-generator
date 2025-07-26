import streamlit as st
from streamlit_lottie import st_lottie
from utils.lottie_helper import load_lottie_url
import time

def show_lottie_welcome():
    if 'welcome_shown' not in st.session_state:
        st.session_state.welcome_shown = False
        st.session_state.welcome_start_time = time.time()

    if not st.session_state.welcome_shown:
        current_time = time.time()
        elapsed = current_time - st.session_state.welcome_start_time

        if elapsed < 3:  # show for 3 seconds
            lottie_url = "https://assets1.lottiefiles.com/packages/lf20_1pxqjqps.json"
            lottie_json = load_lottie_url(lottie_url)
            if lottie_json:
                with st.container():
                    st.markdown("## 👋 Welcome to the KPI & Chart Generator!")
                    st.markdown("Upload your CSV, generate KPIs, and visualize charts easily.")
                    st_lottie(lottie_json, height=300, key="welcome_lottie")
            st.experimental_rerun()  # refresh page until time expires
        else:
            st.session_state.welcome_shown = True

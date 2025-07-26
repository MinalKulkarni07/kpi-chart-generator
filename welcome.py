# welcome.py
import streamlit as st
from streamlit_lottie import st_lottie
from utils.lottie_helper import load_lottie_url
import time

def show_lottie_welcome():
    with st.container():
        lottie_url = "https://assets1.lottiefiles.com/packages/lf20_1pxqjqps.json"  # Change this if needed
        lottie_json = load_lottie_url(lottie_url)

        if lottie_json:
            st.markdown("## 👋 Welcome to the KPI & Chart Generator!")
            st.markdown("Upload your CSV, generate KPIs, and visualize charts easily.")

            st_lottie(
                lottie_json,
                speed=1,
                loop=False,
                quality="high",
                height=300,
                key="welcome_animation"
            )

            time.sleep(1.5)

# welcome.py

import streamlit as st
import time

def show_welcome_message():
    with st.container():
        st.markdown(
            "<h3 style='text-align: center; color: teal;'>🚀 Welcome to the KPI & Chart Generator!</h3>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align: center;'>Easily upload your data, calculate KPIs, and visualize trends in seconds.</p>",
            unsafe_allow_html=True
        )
        st.success("Let's get started! 💡 Upload your CSV file from the sidebar.")

        time.sleep(2.5)

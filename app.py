import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import json
from utils.data_processor import DataProcessor
from utils.kpi_calculator import KPICalculator
from utils.chart_generator import ChartGenerator
from utils.export_manager import ExportManager

# ----------------------
# App Configuration
# ----------------------
st.set_page_config(
    page_title="KPI & Chart Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------
# Welcome Gesture and File Upload Warning
# ----------------------
st.markdown("""
<style>
    .welcome {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }
    .warning {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
</style>
<div class="welcome">👋 Welcome to the KPI & Chart Generator App!</div>
<div class="warning">⚠️ Note: This app does <u>not</u> save your uploaded files. If the connection drops or page refreshes, please re-upload your CSV.</div>
""", unsafe_allow_html=True)

# ----------------------
# Sidebar Toggle Button
# ----------------------
with st.sidebar:
    with st.expander("🔧 App Settings", expanded=False):
        theme = st.radio("Theme Mode", ["Light", "Dark"], index=0)
        chart_limit = st.slider("Chart Gallery Limit", 1, 10, 4)
        default_export = st.selectbox("Default Chart Export Format", ["HTML", "JSON"])
        show_help = st.checkbox("Show In-App Help", value=True)

# ----------------------
# Session State Init
# ----------------------
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = []
if 'chart_limit' not in st.session_state:
    st.session_state.chart_limit = chart_limit

# ----------------------
# App Navigation
# ----------------------
def main():
    st.title("📊 KPI & Chart Generator")

    # Navigation Panel
    with st.sidebar:
        st.header("📁 Navigation")
        page = st.radio(
            "Go to Section:",
            ["📁 Data Upload", "📈 KPI Dashboard", "📊 Chart Generator", "⚙️ Settings"]
        )

    if page == "📁 Data Upload":
        data_upload_page()
    elif page == "📈 KPI Dashboard":
        kpi_dashboard_page()
    elif page == "📊 Chart Generator":
        chart_generator_page()
    elif page == "⚙️ Settings":
        settings_page()

# Import and run the remaining pages as before
from pages.data_upload import data_upload_page
from pages.kpi_dashboard import kpi_dashboard_page
from pages.chart_generator import chart_generator_page
from pages.settings_page import settings_page


if __name__ == "__main__":
    main()

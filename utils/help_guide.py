import streamlit as st
from utils.tracker import log_to_google_sheets


def help_guide_page():
    log_to_google_sheets(
        event="Page Viewed",
        page="Help & Guide",
        user_info=str(st.session_state.get("user", "Guest")),
        notes="Viewed Help & Guide")
    st.header("❓ How to Use This App")
    st.markdown("""
    This app helps you analyze your CSV files with KPIs and interactive charts.

    ### 📁 Step 1: Upload Data
    - Go to **Data Upload**
    - Upload your CSV file
    - The app will auto-detect columns and show data summary

    ### 📈 Step 2: View KPIs
    - Navigate to **KPI Dashboard**
    - Select numeric columns to compute:
        - Total
        - Average
        - Growth Rate
    - Optionally group by a category
    - You can also create **custom formulas**

    ### 📊 Step 3: Generate Charts
    - Navigate to **Chart Generator**
    - Choose between:
        - **Standard Charts** (you choose X and Y axes)
        - **Top N Charts** (automatically pick top categories)
    - Customize chart type and colors
    - Interactive charts will be displayed and downloadable

    ### 💾 Step 4: Export Results
    - On both KPI and Chart sections, download:
        - JSON
        - Excel
        - HTML
    - Choose format in **Settings**

    ### ⚙️ Step 5: Settings
    - Control export format, image quality, decimal places, etc.

    ### 🔄 Reset
    - Use the **Reset App** button in the sidebar to start fresh

    ### 📌 Tips
    - App does not store your data
    - Refreshing or disconnecting will remove uploaded files
    - You can use on both desktop and mobile
    """)

    if st.button("🔍 Test Help Page Log"):
    log_to_google_sheets("Manual Test", "Help Page", "Tester", "From button")
    st.success("Test log sent!")


import streamlit as st
from utils.tracker import log_to_google_sheets  # if saved in a tracker utility file

def log_to_google_sheets(event, page, user_info="anonymous", notes=""):
    url = "https://script.google.com/macros/s/AKfycbwXo2emErt44h50gEcoLgQJwRZYduk7Y-fe5J_cL7tbta1LHeWhbrKhLCNjIrdbkMUH7g/exec"  # Replace with your copied script URL
    payload = {
        "event": event,
        "page": page,
        "user_info": user_info,
        "notes": notes,
    }
    try:
        requests.post(url, json=payload, timeout=3)
    except Exception as e:
        print("Logging failed:", e)

def help_guide_page():
    log_to_google_sheets(
    event="Page Viewed",
    page="Help & Guide",
    user_info=str(st.session_state.get("user", "Guest")),
    notes="Viewed Help & Guide"
)
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

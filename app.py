# app.py
import streamlit as st
import pandas as pd
from utils.kpi_calculator import KPICalculator
from utils.data_processor import DataProcessor
from utils.chart_generator import ChartGenerator
from utils.export_manager import ExportManager
import datetime

# ------------------------- App Settings -------------------------
st.set_page_config(
    page_title="KPI & Chart Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------- Welcome Gesture -------------------------
st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h2 style='color: #1f77b4;'>📊 Welcome to the KPI & Chart Generator App!</h2>
        <p style='font-size: 16px;'>Upload your CSV file and generate insights instantly. No files are saved.</p>
    </div>
""", unsafe_allow_html=True)

# ------------------------- File Upload -------------------------
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")
    
    # ------------------------- Data Processor -------------------------
    processor = DataProcessor(df)
    analysis = processor.analyze_data()

    # ------------------------- KPI Calculator -------------------------
    calculator = KPICalculator(df)
    numeric_columns = analysis['numeric_columns']
    
    st.header("📈 KPI Summary")
    kpi_cols = st.multiselect("Select numeric columns to analyze KPIs:", options=numeric_columns)
    if kpi_cols:
        kpis = calculator.calculate_basic_kpis(kpi_cols)
        st.write(pd.DataFrame(kpis).T)

    # ------------------------- Chart Generator -------------------------
    st.header("📊 Chart Generator")
    generator = ChartGenerator(df)
    
    x_col = st.selectbox("Select X-axis column:", options=df.columns)
    y_col = st.selectbox("Select Y-axis column:", options=numeric_columns)
    chart_type = st.selectbox("Select chart type:", ["Bar", "Line", "Scatter", "Pie", "Box", "Histogram"])

    if st.button("Generate Chart"):
        try:
            if chart_type == "Bar":
                fig = generator.create_bar_chart(x_col, y_col)
            elif chart_type == "Line":
                fig = generator.create_line_chart(x_col, y_col)
            elif chart_type == "Scatter":
                fig = generator.create_scatter_plot(x_col, y_col)
            elif chart_type == "Pie":
                fig = generator.create_pie_chart(x_col, y_col)
            elif chart_type == "Box":
                fig = generator.create_box_plot(x_col, y_col)
            elif chart_type == "Histogram":
                fig = generator.create_histogram(y_col)

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error generating chart: {e}")

    # ------------------------- Chart Gallery -------------------------
    st.header("🖼️ Chart Gallery (Max 4)")
    gallery_x = st.selectbox("Gallery X-axis:", df.columns, key='gallery_x')
    gallery_y = st.multiselect("Gallery Y-axis (up to 4):", numeric_columns, max_selections=4)

    if gallery_x and gallery_y:
        for col in gallery_y[:4]:
            try:
                chart = generator.create_line_chart(gallery_x, col)
                st.plotly_chart(chart, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not generate chart for {col}: {e}")

    # ------------------------- Export Manager -------------------------
    st.header("📤 Export KPIs")
    export_manager = ExportManager()

    if st.button("Download KPI Report (Excel)"):
        kpi_data = calculator.calculate_basic_kpis(kpi_cols)
        excel_bytes = export_manager.create_kpi_excel(kpi_data)
        st.download_button("Download Excel", excel_bytes, file_name="kpi_report.xlsx")

    if st.button("Download KPI Report (PDF)"):
        kpi_data = calculator.calculate_basic_kpis(kpi_cols)
        pdf_bytes = export_manager.create_kpi_pdf(kpi_data)
        st.download_button("Download PDF", pdf_bytes, file_name="kpi_report.pdf")

else:
    st.warning("Please upload a CSV file to begin.")

# ------------------------- Warning Note -------------------------
st.sidebar.markdown("""
---
⚠️ **Note:** This app does not save your uploaded files. If your network is interrupted or the page refreshes, you'll need to re-upload your file.
""")

import streamlit as st

def settings_page():
    st.header("⚙️ Settings")
    
    st.subheader("🎨 Display Options")
    st.info("🎨 This application uses Streamlit's default theme for optimal performance and consistency.")
    
    st.subheader("⚙️ Data Processing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_rows = st.number_input(
            "Maximum rows to process:",
            min_value=1000,
            max_value=1000000,
            value=100000,
            step=1000,
            help="Limit the number of rows to process for better performance"
        )
    
    with col2:
        decimal_places = st.number_input(
            "Decimal places for numbers:",
            min_value=0,
            max_value=10,
            value=2,
            help="Number of decimal places to show in calculations"
        )
    
    st.subheader("💾 Export Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        kpi_export_format = st.selectbox(
            "Default KPI export format:",
            ["Excel", "PDF", "JSON"],
            help="Preferred format for KPI reports"
        )
        
        chart_export_format = st.selectbox(
            "Default chart export format:",
            ["PDF", "Excel", "HTML", "JSON"],
            help="Preferred format for chart exports"
        )
    
    with col2:
        pdf_quality = st.selectbox(
            "PDF image quality:",
            ["High", "Medium", "Low"],
            index=1,
            help="Higher quality creates larger files"
        )
        
        include_metadata = st.checkbox(
            "Include metadata in exports",
            value=True,
            help="Add generation date and settings info"
        )
    
    st.session_state.kpi_export_format = kpi_export_format
    st.session_state.chart_export_format = chart_export_format
    st.session_state.pdf_quality = pdf_quality
    st.session_state.include_metadata = include_metadata
    
    st.subheader("ℹ️ About")
    st.markdown("""
    **KPI & Chart Generator** v1.0  
    Upload CSV → Analyze → Generate KPIs → Create Charts → Export  

    - Built with **Streamlit**, **Pandas**, **NumPy**, **Plotly**
    """)

    if st.button("🔄 Reset Application"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✅ Application reset successfully!")
        st.rerun()

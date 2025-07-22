# ⚙️ pages/settings_page.py

import streamlit as st


def settings_page():
    st.header("⚙️ Settings")
    st.subheader("🖥️ Display Settings")

    theme = st.radio("Theme Mode", ["Light", "Dark"], index=0)
    max_rows = st.slider("Max rows to process", 1000, 100000, 10000, step=1000)

    st.subheader("📤 Export Defaults")
    export_kpi_format = st.selectbox("KPI Export Format", ["Excel", "JSON", "PDF"])
    export_chart_format = st.selectbox("Chart Export Format", ["HTML", "PDF"])
    quality = st.radio("PDF Quality", ["High", "Medium", "Low"], index=1)

    st.session_state['theme'] = theme
    st.session_state['max_rows'] = max_rows
    st.session_state['export_kpi_format'] = export_kpi_format
    st.session_state['export_chart_format'] = export_chart_format
    st.session_state['pdf_quality'] = quality

    st.success("Settings saved to session state.")

    st.subheader("🔄 Reset All")
    if st.button("Reset App"):
        st.session_state.clear()
        st.experimental_rerun()

# 📈 pages/kpi_dashboard.py

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from utils.kpi_calculator import KPICalculator
from utils.export_manager import ExportManager


def kpi_dashboard_page():
    if st.session_state.data is None:
        st.warning("⚠️ Please upload a file first.")
        return

    st.header("📈 KPI Dashboard")
    data = st.session_state.data
    processed_info = st.session_state.processed_data

    kpi_calc = KPICalculator(data)

    st.subheader("🔧 KPI Configuration")
    col1, col2 = st.columns(2)
    numeric_cols = processed_info['numeric_columns']
    all_cols = list(data.columns)

    with col1:
        selected_cols = st.multiselect("Select numeric columns:", numeric_cols)
    with col2:
        group_col = st.selectbox("Group by column:", ["None"] + all_cols)

    if selected_cols:
        kpis = kpi_calc.calculate_basic_kpis(selected_cols)
        st.subheader("📊 Basic KPIs")
        cols = st.columns(len(selected_cols))
        for i, col in enumerate(selected_cols):
            with cols[i]:
                st.metric(f"Sum of {col}", f"{kpis[col]['sum']:.2f}")
                st.metric(f"Mean of {col}", f"{kpis[col]['mean']:.2f}")

        st.subheader("📈 Growth Rate")
        if processed_info['date_columns']:
            date_col = processed_info['date_columns'][0]
            growth = kpi_calc.calculate_growth_rate(selected_cols[0], date_col)
            st.metric("Growth Rate", f"{growth:.2f}%")

        if group_col != "None":
            st.subheader(f"Grouped KPIs by {group_col}")
            grouped = kpi_calc.calculate_grouped_kpis(selected_cols, group_col)
            st.dataframe(grouped, use_container_width=True)

        st.subheader("📥 Export KPIs")
        export_data = {"kpis": kpis}
        if group_col != "None":
            export_data["grouped"] = grouped.to_dict()

        manager = ExportManager()
        col1, col2 = st.columns(2)

        with col1:
            json_str = json.dumps(export_data, indent=2)
            st.download_button("📄 JSON", json_str, f"kpi_{datetime.now().strftime('%Y%m%d')}.json")

        with col2:
            excel_bytes = manager.create_kpi_excel(kpis, grouped if group_col != "None" else None, export_data)
            st.download_button("📊 Excel", excel_bytes, f"kpi_{datetime.now().strftime('%Y%m%d')}.xlsx")

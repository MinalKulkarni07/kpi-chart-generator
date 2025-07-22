# 📊 pages/chart_generator.py

import streamlit as st
from datetime import datetime
from utils.chart_generator import ChartGenerator
from utils.export_manager import ExportManager
import io


def chart_generator_page():
    if st.session_state.data is None:
        st.warning("⚠️ Please upload a file first.")
        return

    st.header("📊 Chart Generator")
    data = st.session_state.data
    processed = st.session_state.processed_data
    chart_gen = ChartGenerator(data)

    chart_type = st.selectbox("Chart Type", [
        "Bar", "Line", "Scatter", "Pie", "Histogram", "Box", "Heatmap"
    ])

    x_col = st.selectbox("X-axis", list(data.columns))
    y_col = st.selectbox("Y-axis", processed['numeric_columns'])

    if st.button("Generate Chart"):
        fig = None
        try:
            if chart_type == "Bar":
                fig = chart_gen.create_bar_chart(x_col, y_col, None, data)
            elif chart_type == "Line":
                fig = chart_gen.create_line_chart(x_col, y_col, None, data)
            elif chart_type == "Scatter":
                fig = chart_gen.create_scatter_plot(x_col, y_col, None, None, data)
            elif chart_type == "Pie":
                fig = chart_gen.create_pie_chart(x_col, y_col, data)
            elif chart_type == "Histogram":
                fig = chart_gen.create_histogram(y_col, data)
            elif chart_type == "Box":
                fig = chart_gen.create_box_plot(x_col, y_col, data)
            elif chart_type == "Heatmap":
                fig = chart_gen.create_heatmap(data)
        
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("📤 Export Chart")
                manager = ExportManager()
                col1, col2 = st.columns(2)

                with col1:
                    html_buf = io.StringIO()
                    fig.write_html(html_buf)
                    st.download_button("🌐 Download HTML", html_buf.getvalue(), f"chart_{datetime.now().strftime('%Y%m%d')}.html")

                with col2:
                    pdf_bytes = manager.create_chart_pdf(fig, chart_type)
                    st.download_button("📋 Download PDF", pdf_bytes, f"chart_{datetime.now().strftime('%Y%m%d')}.pdf")

        except Exception as e:
            st.error(f"Chart Error: {e}")

# 📁 pages/data_upload.py

import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor


def data_upload_page():
    st.header("📁 Data Upload & Preview")

    uploaded_file = st.file_uploader(
        "Upload CSV file", type=["csv"],
        help="Upload your CSV file to begin analysis. The file should contain structured data with headers."
    )

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
            st.session_state.data = data

            processor = DataProcessor(data)
            processed_info = processor.analyze_data()
            st.session_state.processed_data = processed_info

            st.success(f"✅ File uploaded successfully! Rows: {len(data)}, Columns: {len(data.columns)}")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", len(data))
            with col2:
                st.metric("Columns", len(data.columns))
            with col3:
                st.metric("Numeric Columns", len(processed_info['numeric_columns']))
            with col4:
                st.metric("Text Columns", len(processed_info['text_columns']))

            st.subheader("📋 Data Preview")
            st.dataframe(data.head(100), use_container_width=True)

            st.subheader("🔍 Column Analysis")
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Numeric Columns:**")
                for col in processed_info['numeric_columns']:
                    stats = data[col].describe()
                    st.write(f"• **{col}**: Count: {stats['count']:.0f}, Mean: {stats['mean']:.2f}")

            with col2:
                st.write("**Text Columns:**")
                for col in processed_info['text_columns']:
                    st.write(f"• **{col}**: {data[col].nunique()} unique values")

            if processed_info['date_columns']:
                st.write("**Date Columns:**")
                for col in processed_info['date_columns']:
                    st.write(f"• **{col}**: Date range detected")

            st.subheader("🔍 Missing Values")
            missing = data.isnull().sum()
            if missing.sum() > 0:
                st.warning("Missing values detected:")
                for col, count in missing[missing > 0].items():
                    st.write(f"• {col}: {count} ({count / len(data) * 100:.1f}%)")
            else:
                st.success("✅ No missing values!")

        except Exception as e:
            st.error(f"❌ Failed to read file: {e}")

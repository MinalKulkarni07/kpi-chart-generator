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

# Page configuration
st.set_page_config(
    page_title="KPI & Chart Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = []

def main():
    st.title("📊 KPI & Chart Generator")
    st.markdown("Upload your CSV file and generate interactive dashboards with key performance indicators and visualizations.")
    
    # Sidebar for navigation and controls
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
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

def data_upload_page():
    st.header("📁 Data Upload & Preview")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your CSV file to begin analysis. The file should contain structured data with column headers."
    )
    
    if uploaded_file is not None:
        try:
            # Read CSV file
            data = pd.read_csv(uploaded_file)
            st.session_state.data = data
            
            # Initialize data processor
            processor = DataProcessor(data)
            processed_info = processor.analyze_data()
            st.session_state.processed_data = processed_info
            
            st.success(f"✅ File uploaded successfully! Dataset contains {len(data)} rows and {len(data.columns)} columns.")
            
            # Display basic information
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", len(data))
            with col2:
                st.metric("Total Columns", len(data.columns))
            with col3:
                st.metric("Numeric Columns", len(processed_info['numeric_columns']))
            with col4:
                st.metric("Text Columns", len(processed_info['text_columns']))
            
            # Data preview
            st.subheader("📋 Data Preview")
            st.dataframe(data.head(100), use_container_width=True)
            
            # Column analysis
            st.subheader("🔍 Column Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Numeric Columns:**")
                for col in processed_info['numeric_columns']:
                    stats = data[col].describe()
                    st.write(f"• **{col}**: {stats['count']} values, Mean: {stats['mean']:.2f}")
            
            with col2:
                st.write("**Text/Categorical Columns:**")
                for col in processed_info['text_columns']:
                    unique_count = data[col].nunique()
                    st.write(f"• **{col}**: {unique_count} unique values")
            
            # Date columns if any
            if processed_info['date_columns']:
                st.write("**Date Columns:**")
                for col in processed_info['date_columns']:
                    st.write(f"• **{col}**: Date range detected")
            
            # Data quality check
            st.subheader("🔍 Data Quality")
            missing_data = data.isnull().sum()
            if missing_data.sum() > 0:
                st.warning("⚠️ Missing values detected:")
                for col, missing_count in missing_data[missing_data > 0].items():
                    st.write(f"• **{col}**: {missing_count} missing values ({missing_count/len(data)*100:.1f}%)")
            else:
                st.success("✅ No missing values detected!")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("Please ensure your file is a valid CSV with proper formatting.")
    
    else:
        st.info("👆 Please upload a CSV file to get started.")

def kpi_dashboard_page():
    if st.session_state.data is None:
        st.warning("⚠️ Please upload a CSV file first.")
        return
    
    st.header("📈 KPI Dashboard")
    
    data = st.session_state.data
    processed_info = st.session_state.processed_data
    
    # Initialize KPI calculator
    kpi_calc = KPICalculator(data)
    
    # KPI Configuration
    with st.expander("⚙️ KPI Configuration", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Select columns for KPIs
            numeric_cols = processed_info['numeric_columns']
            selected_kpi_columns = st.multiselect(
                "Select columns for KPI calculation:",
                numeric_cols,
                default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols
            )
        
        with col2:
            # Select grouping column if needed
            all_cols = list(data.columns)
            grouping_column = st.selectbox(
                "Group by column (optional):",
                ["None"] + all_cols,
                help="Select a column to group KPIs by categories"
            )
    
    if selected_kpi_columns:
        # Calculate KPIs
        kpis = kpi_calc.calculate_basic_kpis(selected_kpi_columns)
        
        # Display KPIs in metrics
        st.subheader("📊 Key Performance Indicators")
        
        # Basic KPIs
        cols = st.columns(len(selected_kpi_columns))
        for i, col in enumerate(selected_kpi_columns):
            with cols[i]:
                st.metric(
                    f"Total {col}",
                    f"{kpis[col]['sum']:,.0f}",
                    help=f"Sum of all values in {col}"
                )
                st.metric(
                    f"Average {col}",
                    f"{kpis[col]['mean']:,.2f}",
                    help=f"Mean value of {col}"
                )
        
        # Additional KPIs
        st.subheader("📈 Advanced KPIs")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(data))
        
        with col2:
            # Growth rate calculation if date column exists
            if processed_info['date_columns']:
                date_col = processed_info['date_columns'][0]
                if len(selected_kpi_columns) > 0:
                    growth_rate = kpi_calc.calculate_growth_rate(selected_kpi_columns[0], date_col)
                    st.metric("Growth Rate", f"{growth_rate:.1f}%")
        
        with col3:
            # Data completeness
            completeness = (1 - data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
            st.metric("Data Completeness", f"{completeness:.1f}%")
        
        with col4:
            # Unique records ratio
            unique_ratio = 100.0
            if len(data.columns) > 0:
                unique_ratio = len(data.drop_duplicates()) / len(data) * 100
                st.metric("Unique Records", f"{unique_ratio:.1f}%")
        
        # Grouped KPIs if grouping column is selected
        grouped_kpis = pd.DataFrame()
        if grouping_column != "None":
            st.subheader(f"📊 KPIs by {grouping_column}")
            grouped_kpis = kpi_calc.calculate_grouped_kpis(selected_kpi_columns, grouping_column)
            
            # Display grouped KPIs as a table
            st.dataframe(grouped_kpis, use_container_width=True)
            
            # Visualization of grouped KPIs
            for col in selected_kpi_columns:
                fig = px.bar(
                    grouped_kpis.reset_index(),
                    x=grouping_column,
                    y=f"{col}_sum",
                    title=f"Total {col} by {grouping_column}"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Export KPIs
        st.subheader("💾 Export KPIs")
        
        # Prepare export data
        export_data = {
            "basic_kpis": kpis,
            "summary_stats": {
                "total_records": len(data),
                "data_completeness": f"{completeness:.1f}%",
                "unique_records_ratio": f"{unique_ratio:.1f}%"
            }
        }
        
        if grouping_column != "None":
            export_data["grouped_kpis"] = grouped_kpis.to_dict()
        
        # Download button for KPI report
        kpi_json = json.dumps(export_data, indent=2, default=str)
        st.download_button(
            label="📥 Download KPI Report (JSON)",
            data=kpi_json,
            file_name=f"kpi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def chart_generator_page():
    if st.session_state.data is None:
        st.warning("⚠️ Please upload a CSV file first.")
        return
    
    st.header("📊 Interactive Chart Generator")
    
    data = st.session_state.data
    processed_info = st.session_state.processed_data
    
    # Initialize chart generator
    chart_gen = ChartGenerator(data)
    
    # Chart configuration
    with st.expander("⚙️ Chart Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            chart_type = st.selectbox(
                "Chart Type:",
                ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram", "Box Plot", "Heatmap"]
            )
        
        with col2:
            x_column = st.selectbox(
                "X-axis:",
                list(data.columns),
                help="Select column for X-axis"
            )
        
        with col3:
            y_column = st.selectbox(
                "Y-axis:",
                processed_info['numeric_columns'] if chart_type not in ["Pie Chart", "Histogram"] else list(data.columns),
                help="Select column for Y-axis"
            )
    
    # Additional options based on chart type
    color_column = None
    size_column = None
    
    if chart_type in ["Scatter Plot", "Bar Chart", "Line Chart"]:
        with st.expander("🎨 Additional Options"):
            col1, col2 = st.columns(2)
            with col1:
                color_column = st.selectbox(
                    "Color by (optional):",
                    ["None"] + list(data.columns)
                )
                if color_column == "None":
                    color_column = None
            
            with col2:
                if chart_type == "Scatter Plot":
                    size_column = st.selectbox(
                        "Size by (optional):",
                        ["None"] + processed_info['numeric_columns']
                    )
                    if size_column == "None":
                        size_column = None
    
    # Data filtering
    with st.expander("🔍 Data Filters"):
        # Date range filter if date columns exist
        if processed_info['date_columns']:
            date_col = st.selectbox("Filter by date column:", processed_info['date_columns'])
            if date_col:
                data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
                min_date = data[date_col].min()
                max_date = data[date_col].max()
                
                date_range = st.date_input(
                    "Select date range:",
                    value=[min_date, max_date],
                    min_value=min_date,
                    max_value=max_date
                )
                
                if len(date_range) == 2:
                    data = data[(data[date_col] >= pd.Timestamp(date_range[0])) & 
                              (data[date_col] <= pd.Timestamp(date_range[1]))]
        
        # Categorical filters
        categorical_cols = [col for col in data.columns if data[col].dtype == 'object']
        if categorical_cols:
            filter_col = st.selectbox("Filter by category:", ["None"] + categorical_cols)
            if filter_col != "None":
                unique_values = data[filter_col].unique()
                selected_values = st.multiselect(
                    f"Select {filter_col} values:",
                    unique_values,
                    default=unique_values
                )
                if selected_values:
                    data = data[data[filter_col].isin(selected_values)]
    
    # Generate chart
    if st.button("🚀 Generate Chart", type="primary"):
        try:
            fig = None
            
            if chart_type == "Bar Chart":
                fig = chart_gen.create_bar_chart(x_column, y_column, color_column, data)
            elif chart_type == "Line Chart":
                fig = chart_gen.create_line_chart(x_column, y_column, color_column, data)
            elif chart_type == "Scatter Plot":
                fig = chart_gen.create_scatter_plot(x_column, y_column, color_column, size_column, data)
            elif chart_type == "Pie Chart":
                fig = chart_gen.create_pie_chart(x_column, y_column, data)
            elif chart_type == "Histogram":
                fig = chart_gen.create_histogram(x_column, data)
            elif chart_type == "Box Plot":
                fig = chart_gen.create_box_plot(x_column, y_column, data)
            elif chart_type == "Heatmap":
                fig = chart_gen.create_heatmap(data)
            
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)
                
                # Export chart
                st.subheader("💾 Export Chart")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Export as HTML
                    html_buffer = io.StringIO()
                    fig.write_html(html_buffer)
                    html_data = html_buffer.getvalue()
                    
                    st.download_button(
                        label="📥 Download as HTML",
                        data=html_data,
                        file_name=f"{chart_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html"
                    )
                
                with col2:
                    # Export as JSON
                    json_data = fig.to_json()
                    st.download_button(
                        label="📥 Download as JSON",
                        data=json_data,
                        file_name=f"{chart_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        except Exception as e:
            st.error(f"❌ Error generating chart: {str(e)}")
    
    # Chart gallery - show multiple charts
    if st.checkbox("📚 Generate Chart Gallery"):
        st.subheader("📚 Chart Gallery")
        
        numeric_cols = processed_info['numeric_columns'][:3]  # Limit to first 3 numeric columns
        
        for i, col in enumerate(numeric_cols):
            st.write(f"**Charts for {col}:**")
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart
                try:
                    fig_bar = chart_gen.create_bar_chart(x_column, col, None, data)
                    st.plotly_chart(fig_bar, use_container_width=True, key=f"bar_{i}")
                except:
                    st.info("Bar chart not available for this data combination")
            
            with col2:
                # Line chart
                try:
                    fig_line = chart_gen.create_line_chart(x_column, col, None, data)
                    st.plotly_chart(fig_line, use_container_width=True, key=f"line_{i}")
                except:
                    st.info("Line chart not available for this data combination")

def settings_page():
    st.header("⚙️ Settings")
    
    st.subheader("🎨 Display Options")
    
    # Theme settings (informational only as we use default)
    st.info("🎨 This application uses Streamlit's default theme for optimal performance and consistency.")
    
    # Data processing settings
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
    
    # Export settings
    st.subheader("💾 Export Settings")
    
    export_format = st.selectbox(
        "Default export format:",
        ["JSON", "CSV", "HTML"],
        help="Default format for exporting data and charts"
    )
    
    # About section
    st.subheader("ℹ️ About")
    st.markdown("""
    **KPI & Chart Generator** v1.0
    
    This application helps you:
    - 📁 Upload and analyze CSV files
    - 📊 Generate key performance indicators
    - 📈 Create interactive visualizations
    - 💾 Export results in multiple formats
    
    Built with:
    - **Streamlit** for the web interface
    - **Pandas** for data processing
    - **Plotly** for interactive charts
    - **NumPy** for numerical computations
    """)
    
    if st.button("🔄 Reset Application"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✅ Application reset successfully!")
        st.rerun()

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dateutil.parser import parse
import io
import json
from utils.data_processor import DataProcessor
from utils.kpi_calculator import KPICalculator
from utils.chart_generator import ChartGenerator
from utils.export_manager import ExportManager
from help_guide import help_guide_page
from welcome import show_lottie_welcome
import requests
from datetime import datetime

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
   

def looks_like_date(val):
    try:
        parse(str(val))
        return True
    except:
        return False
            

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
    log_to_google_sheets(
    event="App Opened",
    page="Home",
    user_info=str(st.session_state.get("user", "Guest")),
    notes="Landing"
)
    show_lottie_welcome()
    st.title("📊 :red[KPI] & :rainbow[Chart] Generator")
    st.markdown("Upload your CSV file and generate interactive dashboards with key performance indicators and visualizations.")
          
    # Sidebar for navigation and controls
    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Select Page",["📁 Data Upload", "📈 KPI Dashboard", "📊 Chart Generator", "⚙️ Settings", "❓ Help & Guide"])
    with st.sidebar:
        st.markdown("---")
        if st.button("🔄 Reset App", help="Clear session and restart the app"):
            log_to_google_sheets(
                event="App Reset",
                page="Sidebar",
                user_info=str(st.session_state.get("user", "Guest")),
                notes="Session Cleared")
            st.session_state.clear()
            st.rerun()

    if page == "📁 Data Upload":
        data_upload_page()
    elif page == "📈 KPI Dashboard":
        kpi_dashboard_page()
    elif page == "📊 Chart Generator":
        chart_generator_page()
    elif page == "⚙️ Settings":
        settings_page()
    elif page == "❓ Help & Guide":
        help_guide_page()

    
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
            for col in data.columns:
                if data[col].dtype == 'object' and data[col].notna().any():
                    sample_value = data[col].dropna().iloc[0]
                    if looks_like_date(sample_value):
                        try:
                            data[col] = pd.to_datetime(data[col], errors='coerce')
                        except:
                            pass
            
            # Initialize data processor
            processor = DataProcessor(data)
            processed_info = processor.analyze_data()
            
            date_cols = [col for col in data.columns if np.issubdtype(data[col].dtype, np.datetime64)]
            processed_info['date_columns'] = date_cols
            
            st.session_state.processed_data = processed_info
            st.session_state.file_uploaded = True
            
            st.success(f"✅ File uploaded successfully! Dataset contains {len(data)} rows and {len(data.columns)} columns.")
            log_to_google_sheets(
            event="File Uploaded",
            page="Data Upload",
            user_info=str(st.session_state.get("user", "Guest")),
            notes=uploaded_file.name)
            # Inside the uploaded_file block after reading and parsing
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            return

    if st.session_state.get("data") is not None and st.session_state.get("processed_data") is not None:
        data = st.session_state.data
        processed_info = st.session_state.processed_data
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
            if processed_info['date_columns']:
                st.write("**Date Columns:**")
                for col in processed_info['date_columns']:
                    min_date = data[col].min()
                    max_date = data[col].max()
                    st.write(f"• **{col}**: From {min_date.date()} to {max_date.date()}")                           
        with col2:
            st.write("**Text/Categorical Columns:**")
            for col in processed_info['text_columns']:
                unique_count = data[col].nunique()
                st.write(f"• **{col}**: {unique_count} unique values")
            
            # Data quality check
        st.subheader("🔍 Data Quality")
        missing_data = data.isnull().sum()
        if missing_data.sum() > 0:
            st.warning("⚠️ Missing values detected:")
            for col, missing_count in missing_data[missing_data > 0].items():
                st.write(f"• **{col}**: {missing_count} missing values ({missing_count/len(data)*100:.1f}%)")
        else:
            st.success("✅ No missing values detected!")
            
    else:
        st.info("👆 Please upload a CSV file to get started.")
        st.info("⚠️ This app does not save your uploaded files. If the connection drops or page refreshes, please re-upload your CSV.")

            
        
def kpi_dashboard_page():
    log_to_google_sheets(
    event="Page Viewed",
    page="KPI Dashboard",
    user_info=str(st.session_state.get("user", "Guest")),
    notes="Viewed KPI dashboard"
)
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
        
        # Custom KPI Formula Section
        st.subheader("🧮 Custom KPI Formula")
        
        with st.expander("Create Custom KPI", expanded=False):
            # Quick templates
            st.write("**Quick KPI Templates:**")
            templates = {
                "Growth Rate %": "((sum(col2) - sum(col1)) / sum(col1)) * 100",
                "Average Ratio": "mean(col1) / mean(col2)",
                "Profit Margin %": "((sum(revenue) - sum(costs)) / sum(revenue)) * 100",
                "Efficiency Ratio": "sum(output) / sum(input)",
                "Conversion Rate %": "(sum(conversions) / sum(total)) * 100"
            }
            
            template_cols = st.columns(len(templates))
            for i, (name, formula) in enumerate(templates.items()):
                with template_cols[i]:
                    if st.button(f"📋 {name}", key=f"template_{i}"):
                        st.session_state.template_formula = formula
                        st.session_state.template_name = name
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Build your custom KPI formula:**")
                
                # Show available functions
                functions_info = kpi_calc.get_available_functions()
                
                st.write("**Available Functions:**")
                st.write(f"• **Math:** {', '.join(functions_info['Mathematical'])}")
                st.write(f"• **Operators:** {', '.join(functions_info['Operators'])}")
                
                # Column mapping
                st.write("**Map your columns to simple names:**")
                column_mapping = {}
                available_cols = processed_info['numeric_columns'] + processed_info['text_columns']
                
                num_mappings = st.number_input("Number of columns to use:", min_value=1, max_value=5, value=2)
                
                for i in range(num_mappings):
                    col_map1, col_map2 = st.columns(2)
                    with col_map1:
                        alias = st.text_input(f"Simple name {i+1}:", value=f"col{i+1}", key=f"alias_{i}")
                    with col_map2:
                        column = st.selectbox(f"Maps to column:", available_cols, key=f"column_{i}")
                    
                    if alias and column:
                        column_mapping[alias] = column
                
                # Formula input
                default_formula = "sum(col1) / sum(col2) * 100"
                default_name = "Custom Ratio"
                
                # Use template if selected
                if hasattr(st.session_state, 'template_formula'):
                    default_formula = st.session_state.template_formula
                    default_name = st.session_state.template_name
                
                formula = st.text_area(
                    "Enter your formula:",
                    value=default_formula,
                    help="Use the simple names you defined above. Example: sum(sales) / count(sales)"
                )
                
                kpi_name = st.text_input("KPI Name:", value=default_name)
                
                # Formula validation
                if st.button("🔍 Validate Formula", key="validate_formula"):
                    if formula and column_mapping:
                        try:
                            # Test the formula without executing it fully
                            test_result = kpi_calc.calculate_custom_kpi(formula, column_mapping)
                            if test_result.get('type') == 'error':
                                st.error(f"❌ Formula Error: {test_result['error']}")
                            else:
                                st.success("✅ Formula is valid!")
                                st.info(f"Expected result type: {test_result.get('type', 'unknown')}")
                        except Exception as e:
                            st.error(f"❌ Validation Error: {str(e)}")
                    else:
                        st.warning("⚠️ Please enter a formula and map columns first.")
            
            with col2:
                st.write("**Formula Examples:**")
                for example in functions_info['Examples']:
                    st.code(example, language='python')
            
            if st.button("🚀 Calculate Custom KPI", type="primary"):
                if formula and column_mapping:
                    result = kpi_calc.calculate_custom_kpi(formula, column_mapping)
                    
                    if result.get('type') == 'error':
                        st.error(f"❌ Formula Error: {result['error']}")
                    else:
                        st.success("✅ Custom KPI calculated successfully!")
                        
                        # Display result
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                kpi_name,
                                f"{result['value']:,.2f}",
                                help=f"Formula: {formula}"
                            )
                        
                        if result.get('type') == 'series':
                            with col2:
                                st.metric("Total", f"{result['sum']:,.2f}")
                            with col3:
                                st.metric("Count", f"{result['count']:,}")
                        
                        # Show formula breakdown
                        st.write("**Formula Details:**")
                        st.code(f"Formula: {formula}")
                        st.write("**Column Mapping:**")
                        for alias, col in column_mapping.items():
                            st.write(f"• {alias} → {col}")
                else:
                    st.warning("⚠️ Please enter a formula and map at least one column.")
        
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
        
        # Initialize export manager
        export_manager = ExportManager()
        
        # Create download columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # JSON Export
            kpi_json = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="📄 Download JSON",
                data=kpi_json,
                file_name=f"kpi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # Excel Export
            try:
                excel_data = export_manager.create_kpi_excel(
                    kpis, 
                    grouped_kpis if grouping_column != "None" else None, 
                    export_data
                )
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=f"kpi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Excel export error: {str(e)}")
        
        with col3:
            # PDF Export
            try:
                pdf_data = export_manager.create_kpi_pdf(
                    kpis, 
                    grouped_kpis if grouping_column != "None" else None, 
                    export_data
                )
                st.download_button(
                    label="📋 Download PDF",
                    data=pdf_data,
                    file_name=f"kpi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF export error: {str(e)}")

def chart_generator_page():
    if st.session_state.get("data") is None:
        st.warning("⚠️ Please upload a CSV file first.")
        return

    st.header("📊 Interactive Chart Generator")

    data = st.session_state.data
    processed_info = st.session_state.processed_data
    chart_gen = ChartGenerator(data)

    chart_mode = st.radio("Select Chart Mode:", ["📊 Standard Charts", "🏆 Top N Charts"], horizontal=True)

    if chart_mode == "📊 Standard Charts":
        st.subheader("📊 Standard Chart Configuration")
        col1, col2 = st.columns(2)

        with col1:
            x_col = st.selectbox("Select X-axis column", list(data.columns), key="std_x")
        with col2:
            y_col = st.selectbox("Select Y-axis column", processed_info["numeric_columns"], key="std_y")

        col3, col4 = st.columns(2)
        with col3:
            std_chart_type = st.selectbox(
                "Chart Type",
                ["bar", "line", "scatter", "box"],
                format_func=lambda x: {
                    "bar": "Bar Chart",
                    "line": "Line Chart",
                    "scatter": "Scatter Plot",
                    "box": "Box Plot"
                }.get(x, x.title()),
                key="std_type"
            )

        with col4:
            color_col = st.selectbox("Color by (optional)", ["None"] + list(data.columns), key="std_color")
            color_col = None if color_col == "None" else color_col

        if st.button("🚀 Generate Standard Chart", key="gen_std"):
            st.subheader("📊 Generated Standard Chart")
            try:
                fig = None
                if std_chart_type == "bar":
                    fig = chart_gen.create_bar_chart(x_col, y_col, color_col, data)
                elif std_chart_type == "line":
                    fig = chart_gen.create_line_chart(x_col, y_col, color_col, data)
                elif std_chart_type == "scatter":
                    fig = chart_gen.create_scatter_plot(x_col, y_col, color_col, None, data)
                elif std_chart_type == "box":
                    fig = chart_gen.create_box_plot(x_col, y_col,color_col, data)
                else:
                    raise ValueError("Unsupported chart type selected.")

                st.plotly_chart(fig, use_container_width=True)
                export_chart(fig, f"Standard_{std_chart_type}_{x_col}_vs_{y_col}")
                log_to_google_sheets(
                    event="Chart Generated",
                    page="Chart Generator",
                    user_info=str(st.session_state.get("user", "Guest")),
                    notes="Standard Chart")

            except Exception as e:
                st.error(f"Error generating standard chart: {str(e)}")

    else:
        st.subheader("🏆 Top N Chart Configuration")
        col1, col2 = st.columns(2)

        with col1:
            cat_col = st.selectbox("Select Category Column", processed_info["text_columns"] + processed_info["numeric_columns"], key="top_cat")
        with col2:
            val_col = st.selectbox("Select Value Column", processed_info["numeric_columns"], key="top_val")

        col3, col4 = st.columns(2)
        with col3:
            top_n = st.number_input("Top N", min_value=3, max_value=20, value=5, step=1, key="top_n")
        with col4:
            top_chart_type = st.selectbox(
                "Chart Type",
                ["bar", "horizontal_bar", "pie", "line", "scatter", "box"],
                format_func=lambda x: {
                    "bar": "Vertical Bar",
                    "horizontal_bar": "Horizontal Bar",
                    "pie": "Pie Chart",
                    "line": "Line Chart",
                    "scatter": "Scatter Plot",
                    "box": "Box Plot"
                }.get(x, x.title()),
                key="top_type"
            )
            # Optional Color Column for Top N
        color_column = st.selectbox("Color by (optional):",["None"] + list(data.columns),index=0,key="top_color")
        color_column = None if color_column == "None" else color_column
        
        if st.button("🚀 Generate Top N Chart", key="gen_top"):
            st.subheader(f"🏆 Top {top_n} Chart")
            try:
                # Step 1: Get top N categories (based on sum of value column)
                top_categories = data.groupby(cat_col)[val_col].sum().nlargest(top_n).index  # <-- NEW
                filtered_data = data[data[cat_col].isin(top_categories)]  # <-- NEW

                # Step 2: Grouped version only for bar/pie charts
                grouped = filtered_data.groupby(cat_col)[val_col].sum().reset_index()  # <-- MOVED HERE

                # Generate based on selected chart type
                if top_chart_type == "bar":
                    fig = px.bar(grouped, x=cat_col, y=val_col, color=color_column or val_col)
                elif top_chart_type == "horizontal_bar":
                    fig = px.bar(grouped, x=val_col, y=cat_col, orientation='h', color=color_column or val_col)
                elif top_chart_type == "pie":
                    fig = px.pie(grouped, names=cat_col, values=val_col)
                elif top_chart_type == "line":
                    if pd.api.types.is_numeric_dtype(grouped[cat_col]) or pd.api.types.is_datetime64_any_dtype(grouped[cat_col]):
                       fig = px.line(grouped.sort_values(cat_col),x=cat_col,y=val_col,color=color_column or None,markers=True)
                    else:
                        st.warning("⚠️ Line chart requires a numeric or time-based X-axis. Showing scatter plot instead.")
                        fig = px.scatter(grouped,x=cat_col,y=val_col,color=color_column or None,size=val_col,title="Fallback to Scatter Plot")
                elif top_chart_type == "scatter":
                    fig = px.scatter(grouped, x=cat_col, y=val_col, size=val_col, color=color_column or cat_col)  # <-- RAW data
                elif top_chart_type == "box":
                    fig = px.box(filtered_data, x=cat_col, y=val_col, color=color_column or cat_col)  # <-- RAW data
                else:
                    raise ValueError("Unsupported chart type selected.")
                    
                st.plotly_chart(fig, use_container_width=True)
                export_chart(fig, f"Top_{top_n}_{cat_col}_by_{val_col}_{top_chart_type}")
                log_to_google_sheets(
                    event="Chart Generated",
                    page="Chart Generator",
                    user_info=str(st.session_state.get("user", "Guest")),
                    notes="Top N Chart")

            except Exception as e:
                st.error(f"Failed to generate Top N chart: {str(e)}")

# 📤 Export helper
def export_chart(fig, title_base):
    col1, col2 = st.columns(2)

    with col1:
        html_buffer = io.StringIO()
        fig.write_html(html_buffer, include_plotlyjs='cdn', full_html=True)
        html_data = html_buffer.getvalue()
        st.download_button(
            label="🌐 Export as HTML",
            data=html_data,
            file_name=f"{title_base.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html"
        )

    with col2:
        json_data = fig.to_json()
        st.download_button(
            label="📄 Export as JSON",
            data=json_data,
            file_name=f"{title_base.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

                    
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        kpi_export_format = st.selectbox(
            "Default KPI export format:",
            ["Excel", "PDF", "JSON"],
            help="Preferred format for KPI reports"
        )
        
        chart_export_format = st.selectbox(
            "Default chart export format:",
            ["HTML", "JSON"],
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
    
    # Store preferences in session state
    st.session_state.kpi_export_format = kpi_export_format
    st.session_state.chart_export_format = chart_export_format
    st.session_state.pdf_quality = pdf_quality
    st.session_state.include_metadata = include_metadata
    
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
    
if __name__ == "__main__":
    main()
  

       
                    

import pandas as pd
import json
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import plotly.io as pio
import base64

class ExportManager:
    """Handles exporting KPIs and charts to various formats"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    def create_kpi_excel(self, kpis_data, grouped_kpis=None, export_data=None):
        """Create Excel file with KPI data"""
        # Create a BytesIO buffer
        buffer = io.BytesIO()
        
        # Create Excel writer
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Add formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            number_format = workbook.add_format({'num_format': '#,##0.00'})
            
            # Basic KPIs Sheet
            if kpis_data:
                basic_kpis_list = []
                for column, metrics in kpis_data.items():
                    for metric_name, value in metrics.items():
                        basic_kpis_list.append({
                            'Column': column,
                            'Metric': metric_name.title(),
                            'Value': value
                        })
                
                df_basic = pd.DataFrame(basic_kpis_list)
                df_basic.to_excel(writer, sheet_name='Basic KPIs', index=False)
                
                # Format the Basic KPIs sheet
                worksheet = writer.sheets['Basic KPIs']
                worksheet.set_column('A:A', 20)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('C:C', 15, number_format)
                
                # Add header formatting
                for col_num, value in enumerate(df_basic.columns.values):
                    worksheet.write(0, col_num, value, header_format)
            
            # Grouped KPIs Sheet
            if grouped_kpis is not None and not grouped_kpis.empty:
                grouped_kpis.to_excel(writer, sheet_name='Grouped KPIs', index=True)
                
                worksheet = writer.sheets['Grouped KPIs']
                worksheet.set_column('A:Z', 15, number_format)
                
                # Add header formatting
                for col_num, value in enumerate(['Group'] + list(grouped_kpis.columns)):
                    worksheet.write(0, col_num, value, header_format)
            
            # Summary Sheet
            if export_data:
                summary_data = []
                summary_data.append(['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                summary_data.append(['Total Records', export_data.get('summary_stats', {}).get('total_records', 'N/A')])
                summary_data.append(['Data Completeness', export_data.get('summary_stats', {}).get('data_completeness', 'N/A')])
                summary_data.append(['Unique Records Ratio', export_data.get('summary_stats', {}).get('unique_records_ratio', 'N/A')])
                
                df_summary = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
                
                worksheet = writer.sheets['Summary']
                worksheet.set_column('A:A', 25)
                worksheet.set_column('B:B', 20)
                
                # Add header formatting
                for col_num, value in enumerate(df_summary.columns.values):
                    worksheet.write(0, col_num, value, header_format)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_kpi_pdf(self, kpis_data, grouped_kpis=None, export_data=None):
        """Create PDF report with KPI data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        story.append(Paragraph("KPI Report", title_style))
        story.append(Spacer(1, 12))
        
        # Report info
        report_info = f"""
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Report Type:</b> Key Performance Indicators Analysis
        """
        story.append(Paragraph(report_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Basic KPIs Section
        if kpis_data:
            story.append(Paragraph("Basic KPIs", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Create table data
            table_data = [['Column', 'Metric', 'Value']]
            for column, metrics in kpis_data.items():
                for metric_name, value in metrics.items():
                    formatted_value = f"{value:,.2f}" if isinstance(value, (int, float)) else str(value)
                    table_data.append([column, metric_name.title(), formatted_value])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Grouped KPIs Section
        if grouped_kpis is not None and not grouped_kpis.empty:
            story.append(Paragraph("Grouped KPIs", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Convert grouped KPIs to table format
            table_data = [['Group'] + list(grouped_kpis.columns)]
            for index, row in grouped_kpis.iterrows():
                row_data = [str(index)]
                for value in row:
                    formatted_value = f"{value:,.2f}" if isinstance(value, (int, float)) else str(value)
                    row_data.append(formatted_value)
                table_data.append(row_data)
            
            # Create table (limit to first 10 rows to fit on page)
            if len(table_data) > 11:  # 1 header + 10 rows
                table_data = table_data[:11]
                table_data.append(['...'] * len(table_data[0]))
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Summary Statistics
        if export_data:
            story.append(Paragraph("Summary Statistics", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            summary_stats = export_data.get('summary_stats', {})
            summary_text = f"""
            <b>Total Records:</b> {summary_stats.get('total_records', 'N/A')}<br/>
            <b>Data Completeness:</b> {summary_stats.get('data_completeness', 'N/A')}<br/>
            <b>Unique Records Ratio:</b> {summary_stats.get('unique_records_ratio', 'N/A')}
            """
            story.append(Paragraph(summary_text, self.styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_chart_pdf(self, fig, chart_title="Chart Report"):
        """Create PDF with chart image"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        story.append(Paragraph(chart_title, title_style))
        story.append(Spacer(1, 12))
        
        # Report info
        report_info = f"""
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Chart Type:</b> Interactive Visualization
        """
        story.append(Paragraph(report_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        try:
            # Convert chart to image
            img_bytes = pio.to_image(fig, format="png", width=600, height=400)
            img_buffer = io.BytesIO(img_bytes)
            
            # Add image to PDF
            img = Image(img_buffer, width=6*inch, height=4*inch)
            story.append(img)
            
        except Exception as e:
            # If image conversion fails, add error message
            error_text = f"Chart image could not be generated: {str(e)}"
            story.append(Paragraph(error_text, self.styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_chart_excel(self, fig, chart_data, chart_title="Chart Data"):
        """Create Excel file with chart data and image"""
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Add formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Chart Data Sheet
            if hasattr(chart_data, 'to_excel'):
                chart_data.to_excel(writer, sheet_name='Chart Data', index=False)
                worksheet = writer.sheets['Chart Data']
                
                # Format columns
                for col_num, column in enumerate(chart_data.columns):
                    worksheet.set_column(col_num, col_num, 15)
                    worksheet.write(0, col_num, column, header_format)
            
            # Chart Info Sheet
            info_data = pd.DataFrame([
                ['Chart Title', chart_title],
                ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['Data Points', len(chart_data) if hasattr(chart_data, '__len__') else 'N/A']
            ], columns=['Property', 'Value'])
            
            info_data.to_excel(writer, sheet_name='Chart Info', index=False)
            worksheet = writer.sheets['Chart Info']
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 30)
            
            # Add header formatting
            for col_num, value in enumerate(info_data.columns.values):
                worksheet.write(0, col_num, value, header_format)
        
        buffer.seek(0)
        return buffer.getvalue()

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots

class ChartGenerator:
    """Generates various types of interactive charts using Plotly"""
    
    def __init__(self, data):
        self.data = data
    
    def create_bar_chart(self, x_column, y_column, color_column=None, data=None):
        """Create an interactive bar chart"""
        if data is None:
            data = self.data
        
        # Handle aggregation if x_column is categorical and y_column is numeric
        if data[x_column].dtype == 'object':
            # Group by x_column and aggregate y_column
            if color_column:
                grouped_data = data.groupby([x_column, color_column])[y_column].sum().reset_index()
            else:
                grouped_data = data.groupby(x_column)[y_column].sum().reset_index()
            
            fig = px.bar(
                grouped_data,
                x=x_column,
                y=y_column,
                color=color_column,
                title=f"{y_column} by {x_column}",
                labels={x_column: x_column.replace('_', ' ').title(),
                       y_column: y_column.replace('_', ' ').title()},
                hover_data={col: True for col in grouped_data.columns if col not in [x_column, y_column]}
            )
        else:
            fig = px.bar(
                data,
                x=x_column,
                y=y_column,
                color=color_column,
                title=f"{y_column} vs {x_column}",
                labels={x_column: x_column.replace('_', ' ').title(),
                       y_column: y_column.replace('_', ' ').title()}
            )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            showlegend=True if color_column else False
        )
        
        return fig
    
    def create_line_chart(self, x_column, y_column, color_column=None, data=None):
        """Create an interactive line chart"""
        if data is None:
            data = self.data
        
        fig = px.line(
            data,
            x=x_column,
            y=y_column,
            color=color_column,
            title=f"{y_column} over {x_column}",
            labels={x_column: x_column.replace('_', ' ').title(),
                   y_column: y_column.replace('_', ' ').title()},
            markers=True
        )
        
        fig.update_layout(
            height=500,
            showlegend=True if color_column else False
        )
        
        return fig
    
    def create_scatter_plot(self, x_column, y_column, color_column=None, size_column=None, data=None):
        """Create an interactive scatter plot"""
        if data is None:
            data = self.data

        # Validate that x_column and y_column exist in data
        if x_column not in data.columns or y_column not in data.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="Invalid x or y column for scatter plot.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=16)
            )
            return fig

    # Ensure hover_data only uses valid columns
        hover_columns = [col for col in data.columns if col not in [x_column, y_column]]

        fig = px.scatter(
            data,
            x=x_column,
            y=y_column,
            color=color_column if color_column else None,
            size=size_column if size_column else None,
            title=f"{y_column} vs {x_column}",
            labels={x_column: x_column.replace('_', ' ').title(),
                   y_column: y_column.replace('_', ' ').title()},
            hover_data=hover_columns
        )

        fig.update_traces(marker=dict(size=10, symbol="circle"))
            
        fig.update_layout(height=500,showlegend=True if color_column else False)
        
        return fig
    
    def create_pie_chart(self, category_column, value_column=None, data=None):
        """Create an interactive pie chart"""
        if data is None:
            data = self.data
        
        # If no value column specified, count occurrences
        if value_column is None:
            pie_data = data[category_column].value_counts().reset_index()
            pie_data.columns = [category_column, 'count']
            value_col = 'count'
        else:
            # Aggregate by category column
            pie_data = data.groupby(category_column)[value_column].sum().reset_index()
            value_col = value_column
        
        fig = px.pie(
            pie_data,
            names=category_column,
            values=value_col,
            title=f"Distribution of {category_column}",
            hover_data=[value_col]
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=500)
        
        return fig
    
    def create_histogram(self, column, bins=30, data=None):
        """Create a histogram"""
        if data is None:
            data = self.data
        
        fig = px.histogram(
            data,
            x=column,
            nbins=bins,
            title=f"Distribution of {column}",
            labels={column: column.replace('_', ' ').title()}
        )
        
        fig.update_layout(
            height=500,
            bargap=0.1
        )
        
        return fig
    
    def create_box_plot(self, x_column, y_column, data=None):
        """Create a box plot"""
        if data is None:
            data = self.data
        
        fig = px.box(
            data,
            x=x_column,
            y=y_column,
            title=f"{y_column} distribution by {x_column}",
            labels={x_column: x_column.replace('_', ' ').title(),
                   y_column: y_column.replace('_', ' ').title()}
        )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_heatmap(self, data=None, columns=None):
        """Create a correlation heatmap for numeric columns"""
        if data is None:
            data = self.data
        
        # Select only numeric columns
        numeric_data = data.select_dtypes(include=[np.number])
        
        if columns:
            numeric_data = numeric_data[columns]
        
        if numeric_data.empty:
            # Create empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No numeric columns available for heatmap",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=16)
            )
            return fig
        
        # Calculate correlation matrix
        corr_matrix = numeric_data.corr()
        
        fig = px.imshow(
            corr_matrix,
            title="Correlation Heatmap",
            aspect="auto",
            color_continuous_scale="RdBu",
            zmin=-1, zmax=1
        )
        
        fig.update_layout(height=500)
        
        return fig
    
    def create_multi_line_chart(self, x_column, y_columns, data=None):
        """Create a multi-line chart for comparing multiple variables"""
        if data is None:
            data = self.data
        
        fig = go.Figure()
        
        for y_col in y_columns:
            if y_col in data.columns:
                fig.add_trace(go.Scatter(
                    x=data[x_column],
                    y=data[y_col],
                    mode='lines+markers',
                    name=y_col.replace('_', ' ').title(),
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title=f"Multiple Variables over {x_column}",
            xaxis_title=x_column.replace('_', ' ').title(),
            yaxis_title="Values",
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def create_bubble_chart(self, x_column, y_column, size_column, color_column=None, data=None):
        """Create a bubble chart"""
        if data is None:
            data = self.data
        
        fig = px.scatter(
            data,
            x=x_column,
            y=y_column,
            size=size_column,
            color=color_column,
            title=f"Bubble Chart: {y_column} vs {x_column}",
            labels={x_column: x_column.replace('_', ' ').title(),
                   y_column: y_column.replace('_', ' ').title()},
            hover_data={col: True for col in data.columns if col not in [x_column, y_column, size_column]}
        )
        
        fig.update_traces(marker=dict(sizemode='area', sizeref=2.*max(data[size_column])/(40.**2), line_width=2))
        fig.update_layout(height=500)
        
        return fig
    
    def create_area_chart(self, x_column, y_column, color_column=None, data=None):
        """Create an area chart"""
        if data is None:
            data = self.data
        
        fig = px.area(
            data,
            x=x_column,
            y=y_column,
            color=color_column,
            title=f"{y_column} Area Chart over {x_column}",
            labels={x_column: x_column.replace('_', ' ').title(),
                   y_column: y_column.replace('_', ' ').title()}
        )
        
        fig.update_layout(
            height=500,
            showlegend=True if color_column else False
        )
        
        return fig
    
    def create_violin_plot(self, x_column, y_column, data=None):
        """Create a violin plot"""
        if data is None:
            data = self.data
        
        fig = px.violin(
            data,
            x=x_column,
            y=y_column,
            title=f"{y_column} Distribution by {x_column}",
            labels={x_column: x_column.replace('_', ' ').title(),
                   y_column: y_column.replace('_', ' ').title()}
        )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_top_n_chart(self, category_column, value_column, n=10, chart_type="bar", data=None, color_column=None):
        """Create a chart showing top N items by value"""
        if data is None:
            data = self.data
        
        # Aggregate data by category and get top N
        if category_column in data.columns and value_column in data.columns:
            # Group by category and sum values
            grouped_data = data.groupby(category_column)[value_column].sum().reset_index()
            
            # Sort by value and get top N
            top_data = grouped_data.nlargest(n, value_column)

            # Only use color_column if it's in the top_data columns
            if color_column and color_column in top_data.columns:
                color_arg = color_column
            else:
                color_arg = None
                
            # Create chart based on type
            if chart_type == "bar":
                fig = px.bar(
                    top_data,
                    x=category_column,
                    y=value_column,
                    title=f"Top {n} {category_column.replace('_', ' ').title()} by {value_column.replace('_', ' ').title()}",
                    labels={category_column: category_column.replace('_', ' ').title(),
                           value_column: value_column.replace('_', ' ').title()},
                    color=color_arg if color_arg else value_column,
                    color_continuous_scale="viridis"
                )
                fig.update_layout(xaxis_tickangle=-45)
                
            elif chart_type == "pie":
                fig = px.pie(
                    top_data,
                    names=category_column,
                    values=value_column,
                    title=f"Top {n} {category_column.replace('_', ' ').title()} Distribution"
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
            elif chart_type == "horizontal_bar":
                fig = px.bar(
                    top_data,
                    x=value_column,
                    y=category_column,
                    orientation='h',
                    title=f"Top {n} {category_column.replace('_', ' ').title()} by {value_column.replace('_', ' ').title()}",
                    labels={category_column: category_column.replace('_', ' ').title(),
                           value_column: value_column.replace('_', ' ').title()},
                    color=color_arg if color_arg else value_column,
                    color_continuous_scale="viridis"
                )
                # Reverse order for better readability (highest at top)
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
            
            else:
                # Default to bar chart
                fig = px.bar(
                    top_data,
                    x=category_column,
                    y=value_column,
                    title=f"Top {n} {category_column.replace('_', ' ').title()}",
                    color=value_column,
                    color_continuous_scale="viridis"
                )
            
            fig.update_layout(height=500, showlegend=False)
            return fig
        
        else:
            # Create empty figure with error message
            fig = go.Figure()
            fig.add_annotation(
                text=f"Invalid columns: {category_column} or {value_column} not found",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=16)
            )
            return fig

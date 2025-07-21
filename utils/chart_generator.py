import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class ChartGenerator:
    def __init__(self, data):
        self.data = data

    def create_bar_chart(self, x, y, color=None, data=None):
        return px.bar(data or self.data, x=x, y=y, color=color, title=f"Bar Chart: {y} by {x}")

    def create_line_chart(self, x, y, color=None, data=None):
        return px.line(data or self.data, x=x, y=y, color=color, title=f"Line Chart: {y} over {x}")

    def create_scatter_plot(self, x, y, color=None, size=None, data=None):
        return px.scatter(data or self.data, x=x, y=y, color=color, size=size, title=f"Scatter Plot: {y} vs {x}")

    def create_pie_chart(self, names, values, data=None):
        df = data or self.data
        grouped = df.groupby(names)[values].sum().reset_index()
        return px.pie(grouped, names=names, values=values, title=f"Pie Chart: {values} by {names}")

    def create_histogram(self, x, data=None):
        return px.histogram(data or self.data, x=x, title=f"Histogram: {x}")

    def create_box_plot(self, x, y, data=None):
        return px.box(data or self.data, x=x, y=y, title=f"Box Plot: {y} by {x}")

    def create_heatmap(self, data=None):
        df = data or self.data
        numeric_df = df.select_dtypes(include='number')
        if numeric_df.empty:
            raise ValueError("No numeric data available for heatmap.")
        corr = numeric_df.corr()
        return px.imshow(corr, text_auto=True, title="Heatmap: Correlation Matrix")

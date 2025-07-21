import pandas as pd

class KPICalculator:
    def __init__(self, data):
        self.data = data.copy()

    def calculate_basic_kpis(self, columns):
        results = {}
        for col in columns:
            if pd.api.types.is_numeric_dtype(self.data[col]):
                results[col] = {
                    'sum': self.data[col].sum(),
                    'mean': self.data[col].mean()
                }
        return results

    def calculate_growth_rate(self, column, date_column):
        try:
            df = self.data[[date_column, column]].copy()
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            df = df.dropna()
            df = df.sort_values(date_column)
            if df.empty:
                return 0
            first = df[column].iloc[0]
            last = df[column].iloc[-1]
            if first == 0:
                return 0
            growth_rate = ((last - first) / abs(first)) * 100
            return growth_rate
        except:
            return 0

    def calculate_grouped_kpis(self, kpi_columns, group_by_col):
        grouped = self.data.groupby(group_by_col)[kpi_columns].agg(['sum', 'mean'])
        # Flatten MultiIndex
        grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
        return grouped

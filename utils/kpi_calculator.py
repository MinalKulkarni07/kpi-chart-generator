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

    def calculate_custom_kpi(self, formula, column_mapping):
        """Calculate custom KPI using user-defined formula"""
        try:
            # Create a safe environment for formula evaluation
            import math
            import numpy as np
            
            # Build the data context for formula evaluation
            context = {
                'data': self.data,
                'sum': np.sum,
                'mean': np.mean,
                'median': np.median,
                'std': np.std,
                'min': np.min,
                'max': np.max,
                'count': len,
                'sqrt': math.sqrt,
                'abs': abs,
                'round': round,
                'np': np,
                'math': math
            }
            
            # Add column values to context
            for alias, column_name in column_mapping.items():
                if column_name in self.data.columns:
                    context[alias] = pd.to_numeric(self.data[column_name], errors='coerce').fillna(0)
            
            # Evaluate the formula safely
            result = eval(formula, {"__builtins__": {}}, context)
            
            # Handle different types of results
            if hasattr(result, '__iter__') and not isinstance(result, str):
                # If result is an array/series, calculate summary statistics
                result_series = pd.Series(result)
                return {
                    'value': float(result_series.mean()),
                    'sum': float(result_series.sum()),
                    'count': len(result_series),
                    'min': float(result_series.min()),
                    'max': float(result_series.max()),
                    'type': 'series'
                }
            else:
                # Single value result
                return {
                    'value': float(result),
                    'type': 'scalar'
                }
        
        except Exception as e:
            return {
                'error': str(e),
                'value': 0,
                'type': 'error'
            }
    
    def get_available_functions(self):
        """Get list of available functions for formula building"""
        return {
            'Mathematical': ['sum()', 'mean()', 'median()', 'std()', 'min()', 'max()', 'count()', 'sqrt()', 'abs()', 'round()'],
            'Operators': ['+', '-', '*', '/', '**', '%'],
            'Comparisons': ['>', '<', '>=', '<=', '==', '!='],
            'Examples': [
                'sum(sales) / count(sales)',
                '(revenue - costs) / revenue * 100',
                'sqrt(sum(quantity ** 2))',
                'mean(price) * 1.2'
            ]
        }

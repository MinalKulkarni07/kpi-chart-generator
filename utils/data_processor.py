import pandas as pd

class DataProcessor:
    def __init__(self, data):
        self.data = data

    def analyze_data(self):
        analysis = {
            "numeric_columns": [],
            "text_columns": [],
            "date_columns": []
        }

        for col in self.data.columns:
            if pd.api.types.is_numeric_dtype(self.data[col]):
                analysis["numeric_columns"].append(col)
            elif pd.api.types.is_datetime64_any_dtype(self.data[col]):
                analysis["date_columns"].append(col)
            elif pd.api.types.is_string_dtype(self.data[col]):
                analysis["text_columns"].append(col)

        return analysis

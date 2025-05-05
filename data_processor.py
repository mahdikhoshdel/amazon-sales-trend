import os
import pandas as pd
from celery import Celery

app = Celery('tasks',
             broker='redis://redis:6379/0',
             backend='redis://redis:6379/0',
             broker_connection_retry_on_startup=True)

@app.task
def compute_sales_trend(file_path, product_name):
    df = pd.read_csv(file_path, low_memory=False)
    product_data = df[df['name'] == product_name][['date', 'discount_price']].copy()
    product_data['sales'] = product_data['discount_price'].str.replace('₹', '').str.replace(',', '').astype(float)
    product_data['date'] = pd.to_datetime(product_data['date'])
    sales_trend = product_data.groupby('date').agg({'sales': 'sum'}).reset_index()
    return sales_trend.to_dict()

class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = self.load_data()

    def load_data(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File {self.file_path} not found")
        return pd.read_csv(self.file_path, low_memory=False)

    def get_products(self):
        return self.df['name'].unique().tolist()

    def get_sales_trend(self, product_name):
        result = compute_sales_trend.delay(self.file_path, product_name)
        return result
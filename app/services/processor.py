import os
import pandas as pd
from celery import Celery
from logzero import logger
from app.config import DATA_FILE_PATH, CELERY_BROKER_URL, CELERY_BACKEND_URL
import cProfile
import pstats

app = Celery('tasks',
             broker=CELERY_BROKER_URL,
             backend=CELERY_BACKEND_URL,
             broker_connection_retry_on_startup=True)

def profile_task(func):
    def wrapper(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            stats = pstats.Stats(profile)
            stats.sort_stats('cumulative')
            stats.print_stats(10)
            return result
        except Exception as e:
            logger.error(f"Profiling error in {func.__name__}: {str(e)}")
            raise
    return wrapper

@app.task
@profile_task
def compute_sales_trend(file_path, original_product_name):
    try:
        df = pd.read_csv(file_path, low_memory=False)
        product_data = df[df['name'] == original_product_name][['date', 'discount_price']].copy()
        if product_data.empty:
            logger.warning(f"No data found for product: {original_product_name}")
            return {'date': {}, 'sales': {}}
        product_data['sales'] = product_data['discount_price'].str.replace('₹', '').str.replace(',', '').astype(float)
        product_data['date'] = pd.to_datetime(product_data['date'])
        sales_trend = product_data.groupby('date').agg({'sales': 'sum'}).reset_index()
        return sales_trend.to_dict()
    except Exception as e:
        logger.error(f"Error in compute_sales_trend for {original_product_name}: {str(e)}")
        raise

class DataProcessor:
    def __init__(self):
        self.df = self.load_data()

    def load_data(self):
        try:
            if not os.path.exists(DATA_FILE_PATH):
                raise FileNotFoundError(f"File {DATA_FILE_PATH} not found")
            df = pd.read_csv(DATA_FILE_PATH, low_memory=False)
            df['name'] = df['name'].fillna('').astype(str)
            df['original_name'] = df['name']
            df['name'] = df['name'].apply(self.abridge_product_name)
            return df
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def abridge_product_name(self, name):
        name = str(name)
        for delimiter in [' (', '2023', 'Model']:
            if delimiter in name:
                name = name.split(delimiter)[0].strip()
                break
        max_length = 50
        return name[:max_length]

    def get_products(self):
        return self.df['name'].unique().tolist()

    def get_original_name(self, abridged_name):
        matching_row = self.df[self.df['name'] == abridged_name]
        if not matching_row.empty:
            return matching_row['original_name'].iloc[0]
        return abridged_name

    def get_sales_trend(self, abridged_product_name):
        try:
            original_name = self.get_original_name(abridged_product_name)
            return compute_sales_trend.delay(DATA_FILE_PATH, original_name)
        except Exception as e:
            logger.error(f"Error getting sales trend for {abridged_product_name}: {str(e)}")
            raise
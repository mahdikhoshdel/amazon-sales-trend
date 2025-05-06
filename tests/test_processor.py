import pytest
import pandas as pd
from app.services.processor import DataProcessor

@pytest.fixture
def data_processor():
    return DataProcessor()

def test_load_data_success(data_processor, mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('pandas.read_csv', return_value=pd.DataFrame({'name': ['Product1'], 'date': ['2023-01-01'], 'discount_price': ['₹32,999']}))
    df = data_processor.df
    assert not df.empty

def test_abridge_product_name():
    processor = DataProcessor()
    name = "Product (2023 Model, Details)"
    assert processor.abridge_product_name(name) == "Product"

def test_get_original_name(data_processor):
    assert data_processor.get_original_name("Product") == "Product"

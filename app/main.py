from dash import Dash
from app.web.layout import layout
from app.web.callbacks import register_callbacks
from app.services.processor import DataProcessor
from app.cache.manager import CacheManager

app = Dash(__name__, external_stylesheets=[
    "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap"
])

# Initialize components
data_processor = DataProcessor()
cache_manager = CacheManager()

# Set layout
app.layout = layout

# Register callbacks
register_callbacks(app, data_processor, cache_manager)

# Define server for Gunicorn
server = app.server

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)
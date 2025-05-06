from dash import Dash
from app.web.layout import layout
from app.web.callbacks import register_callbacks
from app.services.processor import DataProcessor
from app.cache.manager import CacheManager
from logzero import logger

app = Dash(__name__, external_stylesheets=[
    "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap"
])

try:
    data_processor = DataProcessor()
    cache_manager = CacheManager()
    app.layout = layout
    register_callbacks(app, data_processor, cache_manager)
    logger.info("Dash application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize application: {str(e)}")
    raise

server = app.server

if __name__ == '__main__':
    try:
        app.run_server(host='0.0.0.0', port=8050, debug=False)
        logger.info("Application running on port 8050")
    except Exception as e:
        logger.error(f"Application failed to run: {str(e)}")
        raise
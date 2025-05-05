import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from data_processor import DataProcessor
from cache_manager import CacheManager
import logging

app = dash.Dash(__name__)
data_processor = DataProcessor('/app/data/Amazon-Products - online.csv')
cache_manager = CacheManager()

logging.basicConfig(level=logging.INFO)

app.layout = html.Div([
    html.H1("Amazon Products Daily Sales Trend", style={'text-align': 'center', 'color': '#333'}),
    html.Label("Select Product:", style={'margin': '20px', 'font-weight': 'bold'}),
    dcc.Dropdown(
        id='product-dropdown',
        options=[{'label': product, 'value': product} for product in data_processor.get_products()],
        value=data_processor.get_products()[0] if data_processor.get_products() else None,
        style={'width': '50%', 'margin': '0 auto', 'padding': '10px'}
    ),
    html.Div(id='full-product-name',
             style={'margin': '20px', 'text-align': 'center', 'font-style': 'italic', 'color': '#555'}),
    dcc.Graph(id='sales-trend-graph', style={'margin-top': '20px'})
], style={'padding': '20px', 'background-color': '#f9f9f9'})


@app.callback(
    [Output('sales-trend-graph', 'figure'),
     Output('full-product-name', 'children')],
    [Input('product-dropdown', 'value')]
)
def update_graph_and_name(selected_product):
    if not selected_product:
        return {
            'layout': {
                'title': 'Please select a product.',
                'xaxis': {'visible': False},
                'yaxis': {'visible': False}
            }
        }, "Please select a product."

    try:
        full_name = data_processor.get_original_name(selected_product)
        unabridged = full_name.split("(")[1] if '(' in full_name else full_name

        if cache_manager.is_cached(selected_product):
            df = cache_manager.get_cached_data(selected_product)
        else:
            task_result = data_processor.get_sales_trend(selected_product)
            result_dict = task_result.get() if task_result else {}
            df = pd.DataFrame(result_dict) if result_dict else pd.DataFrame()
            if not df.empty:
                cache_manager.cache_data(selected_product, df)

        logging.info(f"Data for {selected_product}: {df}")

        if df.empty:
            return {
                'layout': {
                    'title': 'No sales data available for this product.',
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False}
                }
            }, unabridged
        elif len(df) == 1:
            fig = px.scatter(df, x='date', y='sales', title=f'Sales for {selected_product} (Single Data Point)')
            fig.update_layout(xaxis_title="Date", yaxis_title="Sales (INR)", template="plotly_white")
        else:
            fig = px.line(df, x='date', y='sales', title=f'Sales Trend for {selected_product}', markers=True)
            fig.update_layout(xaxis_title="Date", yaxis_title="Sales (INR)", template="plotly_white")

        return fig, unabridged

    except Exception as e:
        logging.error(f"Error processing {selected_product}: {str(e)}")
        return {
            'layout': {
                'title': f'Error: {str(e)}',
                'xaxis': {'visible': False},
                'yaxis': {'visible': False}
            }
        }, f"Error retrieving full name: {str(e)}"


server = app.server

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)
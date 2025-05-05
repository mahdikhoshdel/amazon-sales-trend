import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from data_processor import DataProcessor
from cache_manager import CacheManager
import logging

app = dash.Dash(__name__, external_stylesheets=[
    "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap"
])
data_processor = DataProcessor('/app/data/Amazon-Products - online.csv')
cache_manager = CacheManager()

logging.basicConfig(level=logging.INFO)

app.layout = html.Div([
    html.Div([
        html.H1("Amazon Products Daily Sales Trend", style={
            'text-align': 'center',
            'color': '#ffffff',
            'font-family': 'Poppins, sans-serif',
            'font-weight': '600',
            'font-size': '2.5rem',
            'margin-bottom': '10px'
        }),
        html.P("Explore daily sales trends with ease", style={
            'text-align': 'center',
            'color': '#e0e0e0',
            'font-family': 'Poppins, sans-serif',
            'font-weight': '300',
            'font-size': '1.2rem',
            'margin-bottom': '20px'
        })
    ], style={
        'background': 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
        'padding': '40px 20px',
        'border-radius': '0 0 20px 20px',
        'box-shadow': '0 4px 10px rgba(0, 0, 0, 0.2)'
    }),

    html.Div([
        html.Label("Select Product:", style={
            'font-family': 'Poppins, sans-serif',
            'font-weight': '600',
            'font-size': '1.1rem',
            'color': '#333',
            'margin-bottom': '10px',
            'display': 'block'
        }),
        dcc.Dropdown(
            id='product-dropdown',
            options=[{'label': product, 'value': product} for product in data_processor.get_products()],
            value=data_processor.get_products()[0] if data_processor.get_products() else None,
            style={
                'width': '100%',
                'font-family': 'Poppins, sans-serif',
                'font-size': '1rem',
                'border-radius': '8px',
                'border': '1px solid #ddd',
                'padding': '10px',
                'box-shadow': '0 2px 5px rgba(0, 0, 0, 0.1)',
                'background-color': '#ffffff'
            }
        ),
        html.Div(id='full-product-name', style={
            'margin-top': '15px',
            'text-align': 'center',
            'font-family': 'Poppins, sans-serif',
            'font-style': 'italic',
            'font-weight': '400',
            'font-size': '0.95rem',
            'color': '#666',
            'background-color': '#f5f5f5',
            'padding': '10px',
            'border-radius': '5px',
            'border': '1px solid #eee'
        }),
        dcc.Loading(
            id="loading-graph",
            type="circle",
            children=[
                dcc.Graph(id='sales-trend-graph', style={'margin-top': '20px'})
            ]
        )
    ], style={
        'max-width': '800px',
        'margin': '30px auto',
        'padding': '30px',
        'background-color': '#ffffff',
        'border-radius': '15px',
        'box-shadow': '0 6px 15px rgba(0, 0, 0, 0.1)'
    })
], style={
    'background-color': '#f0f2f5',
    'min-height': '100vh',
    'font-family': 'Poppins, sans-serif'
})

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
            result_dict = task_result.get() if task_result else {}  # Retrieve dictionary result from Celery task
            df = pd.DataFrame(result_dict) if result_dict else pd.DataFrame()  # Convert back to DataFrame
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
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Sales (INR)",
                template="plotly_white",
                title_font=dict(family="Poppins, sans-serif", size=20, color="#333"),
                font=dict(family="Poppins, sans-serif", size=14, color="#666")
            )
        else:
            fig = px.line(df, x='date', y='sales', title=f'Sales Trend for {selected_product}', markers=True)
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Sales (INR)",
                template="plotly_white",
                title_font=dict(family="Poppins, sans-serif", size=20, color="#333"),
                font=dict(family="Poppins, sans-serif", size=14, color="#666")
            )

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
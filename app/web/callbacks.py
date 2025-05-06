from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from logzero import logger


def register_callbacks(app, data_processor, cache_manager):
    @app.callback(
        [
            Output("sales-trend-graph", "figure"),
            Output("full-product-name", "children"),
        ],
        [Input("product-dropdown", "value")],
    )
    def update_graph_and_name(selected_product):
        if not selected_product:
            return {
                "layout": {
                    "title": "Please select a product.",
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False},
                }
            }, "Please select a product."

        try:
            logger.info(f"Processing request for product: {selected_product}")
            full_name = data_processor.get_original_name(selected_product)
            unabridged = full_name.split("(")[1] if "(" in full_name else full_name

            if cache_manager.is_cached(selected_product):
                df = cache_manager.get_cached_data(selected_product)
            else:
                task_result = data_processor.get_sales_trend(selected_product)
                result_dict = task_result.get() if task_result else {}
                df = pd.DataFrame(result_dict) if result_dict else pd.DataFrame()
                if not df.empty:
                    cache_manager.cache_data(selected_product, df)

            if df.empty:
                logger.warning(f"No sales data available for {selected_product}")
                return {
                    "layout": {
                        "title": "No sales data available for this product.",
                        "xaxis": {"visible": False},
                        "yaxis": {"visible": False},
                    }
                }, unabridged
            elif len(df) == 1:
                fig = px.scatter(
                    df,
                    x="date",
                    y="sales",
                    title=f"Sales for {selected_product} (Single Data Point)",
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Sales (INR)",
                    template="plotly_white",
                    title_font=dict(
                        family="Poppins, sans-serif", size=20, color="#333"
                    ),
                    font=dict(family="Poppins, sans-serif", size=14, color="#666"),
                )
            else:
                fig = px.line(
                    df,
                    x="date",
                    y="sales",
                    title=f"Sales Trend for {selected_product}",
                    markers=True,
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Sales (INR)",
                    template="plotly_white",
                    title_font=dict(
                        family="Poppins, sans-serif", size=20, color="#333"
                    ),
                    font=dict(family="Poppins, sans-serif", size=14, color="#666"),
                )
            logger.info(f"Successfully processed data for {selected_product}")
            return fig, unabridged
        except Exception as e:
            logger.error(f"Error processing {selected_product}: {str(e)}")
            return {
                "layout": {
                    "title": f"Error: {str(e)}",
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False},
                }
            }, f"Error retrieving full name: {str(e)}"

    @app.callback(
        Output("product-dropdown", "options"), Input("product-dropdown", "value")
    )
    def update_dropdown_options(value):
        try:
            options = [
                {"label": product, "value": product}
                for product in data_processor.get_products()
            ]
            logger.debug(f"Updated dropdown options with {len(options)} products")
            return options
        except Exception as e:
            logger.error(f"Error updating dropdown options: {str(e)}")
            return []

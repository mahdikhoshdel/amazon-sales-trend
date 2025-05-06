from dash import dcc, html

layout = html.Div(
    [
        # Header Section
        html.Div(
            [
                html.H1(
                    "Amazon Products Daily Sales Trend",
                    style={
                        "text-align": "center",
                        "color": "#ffffff",
                        "font-family": "Poppins, sans-serif",
                        "font-weight": "600",
                        "font-size": "2.5rem",
                        "margin-bottom": "10px",
                    },
                ),
                html.P(
                    "Explore daily sales trends with ease",
                    style={
                        "text-align": "center",
                        "color": "#e0e0e0",
                        "font-family": "Poppins, sans-serif",
                        "font-weight": "300",
                        "font-size": "1.2rem",
                        "margin-bottom": "20px",
                    },
                ),
            ],
            style={
                "background": "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)",
                "padding": "40px 20px",
                "border-radius": "0 0 20px 20px",
                "box-shadow": "0 4px 10px rgba(0, 0, 0, 0.2)",
            },
        ),
        # Main Content Section
        html.Div(
            [
                html.Label(
                    "Select Product:",
                    style={
                        "font-family": "Poppins, sans-serif",
                        "font-weight": "600",
                        "font-size": "1.1rem",
                        "color": "#333",
                        "margin-bottom": "10px",
                        "display": "block",
                    },
                ),
                dcc.Dropdown(
                    id="product-dropdown",
                    options=[],
                    value=None,
                    style={
                        "width": "100%",
                        "font-family": "Poppins, sans-serif",
                        "font-size": "1rem",
                        "border-radius": "8px",
                        "border": "1px solid #ddd",
                        "padding": "10px",
                        "box-shadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                        "background-color": "#ffffff",
                    },
                ),
                html.Div(
                    id="full-product-name",
                    style={
                        "margin-top": "15px",
                        "text-align": "center",
                        "font-family": "Poppins, sans-serif",
                        "font-style": "italic",
                        "font-weight": "400",
                        "font-size": "0.95rem",
                        "color": "#666",
                        "background-color": "#f5f5f5",
                        "padding": "10px",
                        "border-radius": "5px",
                        "border": "1px solid #eee",
                    },
                ),
                dcc.Loading(
                    id="loading-graph",
                    type="circle",
                    children=[
                        dcc.Graph(id="sales-trend-graph", style={"margin-top": "20px"})
                    ],
                ),
            ],
            style={
                "max-width": "800px",
                "margin": "30px auto",
                "padding": "30px",
                "background-color": "#ffffff",
                "border-radius": "15px",
                "box-shadow": "0 6px 15px rgba(0, 0, 0, 0.1)",
            },
        ),
    ],
    style={
        "background-color": "#f0f2f5",
        "min-height": "100vh",
        "font-family": "Poppins, sans-serif",
    },
)

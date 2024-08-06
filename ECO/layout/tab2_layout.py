import pandas as pd
from dash import dcc, html

layout = html.Div([
    html.H1('Tab 2 Content'),
    # Tab 2 specific layout
    html.Div([
        html.Label("This is Tab 2"),
        # Add Tab 2 specific components here
    ])
])

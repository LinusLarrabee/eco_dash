import dash
import dash_bootstrap_components as dbc

# 创建 Dash 应用
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np

# 创建 Dash 应用
app = dash.Dash(__name__)

# 读取数据
df = pd.read_csv('data.csv')
df['collection_time'] = pd.to_datetime(df['collection_time'])

# 定义页面布局
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Label("选择 Band："),
        dcc.Dropdown(
            id='band-dropdown',
            options=[
                {'label': '2.4g', 'value': '2.4g'},
                {'label': '5g', 'value': '5g'},
                {'label': '6g', 'value': '6g'}
            ],
            value='2.4g'
        ),
        html.Label("选择时间粒度："),
        dcc.Dropdown(
            id='time-granularity-dropdown',
            options=[
                {'label': '15 minutes', 'value': '15min'},
                {'label': '1 hour', 'value': '1h'},
                {'label': '1 day', 'value': '1d'},
                {'label': '7 days', 'value': '7d'}
            ],
            value='15min'
        ),
        html.Label("选择指标："),
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[
                {'label': 'jitter', 'value': 'jitter'},
                {'label': 'latency', 'value': 'latency'},
                {'label': 'cpu_usage', 'value': 'cpu_usage'},
                {'label': 'connectivity_score', 'value': 'connectivity_score'},
                {'label': 'system_health_score', 'value': 'system_health_score'}
            ],
            value='jitter'
        ),
        html.Label("选择百分位："),
        dcc.Slider(
            id='percentile-slider',
            min=0,
            max=100,
            step=1,
            value=50,
            marks={i: f'{i}%' for i in range(0, 101, 10)}
        )
    ], style={'display': 'flex', 'flexDirection': 'column', 'width': '20%', 'position': 'absolute', 'left': '10px', 'top': '10px'}),
    html.Div([
        dcc.Graph(id='indicator-graph')
    ], style={'marginLeft': '25%'})
])

# 更新页面内容回调
@app.callback(Output('indicator-graph', 'figure'),
              [Input('indicator-dropdown', 'value'),
               Input('band-dropdown', 'value'),
               Input('time-granularity-dropdown', 'value'),
               Input('percentile-slider', 'value')])
def update_graph(indicator, band, granularity, percentile):
    filtered_df = df[(df['band'] == band) & (df[indicator].notnull()) & (df[indicator] != 0)]

    # 按时间粒度聚合数据
    if granularity == '15min':
        freq = '15T'
    elif granularity == '1h':
        freq = 'H'
    elif granularity == '1d':
        freq = 'D'
    elif granularity == '7d':
        freq = '7D'

    aggregated_df = filtered_df.resample(freq, on='collection_time').mean().reset_index()

    return {
        'data': [
            {'x': aggregated_df['collection_time'], 'y': aggregated_df[indicator], 'type': 'line', 'name': indicator},
        ],
        'layout': {
            'title': f'{indicator} (百分位: {percentile}%)'
        }
    }

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

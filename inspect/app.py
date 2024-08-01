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
df['utc_time'] = pd.to_datetime(df['utc_time'])

# 定义页面布局
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Label("选择 Region："),
        dcc.Dropdown(
            id='region-dropdown',
            options=[
                {'label': 'All', 'value': 'all'},
                {'label': 'use1', 'value': 'use1'},
                {'label': 'aps1', 'value': 'aps1'},
                {'label': 'euw1', 'value': 'euw1'}
            ],
            value='all'
        ),
        html.Label("选择 Band："),
        dcc.Dropdown(
            id='band-dropdown',
            options=[
                {'label': 'All', 'value': 'all'},
                {'label': '2.4g', 'value': '2.4g'},
                {'label': '5g', 'value': '5g'},
                {'label': '6g', 'value': '6g'}
            ],
            value='all'
        ),
        html.Label("选择时间范围："),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=df['utc_time'].min().date(),
            end_date=df['utc_time'].max().date(),
            display_format='YYYY-MM-DD'
        ),
        html.Label("选择时间粒度："),
        dcc.Dropdown(
            id='time-granularity-dropdown',
            options=[
                {'label': '1 day', 'value': '1d'},
                {'label': '7 days', 'value': '7d'}
            ],
            value='1d'
        ),
        html.Label("选择指标："),
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[
                {'label': 'wan_throughput', 'value': 'wan_throughput'},
                {'label': 'client_online', 'value': 'client_online'}
            ],
            value='wan_throughput'
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
        dcc.Graph(id='wan-throughput-graph'),
        dcc.Graph(id='client-online-graph')
    ], style={'marginLeft': '25%'})
])

# 更新页面内容回调
@app.callback([Output('wan-throughput-graph', 'figure'),
               Output('client-online-graph', 'figure')],
              [Input('region-dropdown', 'value'),
               Input('band-dropdown', 'value'),
               Input('date-picker-range', 'start_date'),
               Input('date-picker-range', 'end_date'),
               Input('time-granularity-dropdown', 'value'),
               Input('indicator-dropdown', 'value'),
               Input('percentile-slider', 'value')])
def update_graph(region, band, start_date, end_date, granularity, indicator, percentile):
    filtered_df = df.copy()

    if region != 'all':
        filtered_df = filtered_df[filtered_df['region'] == region]

    if band != 'all':
        filtered_df = filtered_df[filtered_df['band'] == band]

    filtered_df = filtered_df[(filtered_df['utc_time'] >= start_date) & (filtered_df['utc_time'] <= end_date)]

    if granularity == '1d':
        freq = 'D'
    elif granularity == '7d':
        freq = '7D'

    # 按时间粒度聚合数据，并计算指定百分位的指标值
    filtered_df.set_index('utc_time', inplace=True)
    grouped = filtered_df.resample(freq).apply(lambda x: x.sort_values().iloc[int(len(x) * percentile / 100)])
    grouped = grouped.reset_index()

    # 打印调试信息
    print("Filtered DataFrame head:", filtered_df.head())
    print("Grouped DataFrame head:", grouped.head())

    wan_throughput_figure = {
        'data': [
            {'x': grouped['utc_time'], 'y': grouped['wan_throughput'], 'type': 'line', 'name': 'WAN Throughput'},
        ],
        'layout': {
            'title': f'WAN Throughput (百分位: {percentile}%)'
        }
    }

    client_online_figure = {
        'data': [
            {'x': grouped['utc_time'], 'y': grouped['client_online'], 'type': 'line', 'name': 'Client Online'},
        ],
        'layout': {
            'title': f'Client Online (百分位: {percentile}%)'
        }
    }

    return wan_throughput_figure, client_online_figure

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

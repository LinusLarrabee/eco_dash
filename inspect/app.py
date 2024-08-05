import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
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
        html.Label("选择时间范围：", style={'fontSize': '12px'}),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=df['utc_time'].min().date(),
            end_date=df['utc_time'].max().date(),
            display_format='YYYY-MM-DD',
            style={'fontSize': '12px'}
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
        html.Label("选择排序指标："),
        dcc.Dropdown(
            id='sort-indicator-dropdown',
            options=[
                {'label': 'WAN Throughput', 'value': 'wan_throughput'},
                {'label': 'Client Online', 'value': 'client_online'},
                {'label': 'Bandwidth', 'value': 'bandwidth'},
                {'label': 'Airtime Utilization', 'value': 'airtime_utilization'},
                {'label': 'Congestion Rate', 'value': 'congestion_rate'},
                {'label': 'Noise', 'value': 'noise'},
                {'label': 'Packet Error Rate', 'value': 'packet_error_rate'}
            ],
            value='wan_throughput'
        ),
        html.Label("选择百分位："),
        dcc.RangeSlider(
            id='percentile-slider',
            min=1,
            max=100,
            step=1,
            value=[20, 80],
            marks={i: f'{i}%' for i in range(0, 101, 10)}
        ),
        html.Div([
            html.Label("当前百分位范围："),
            dcc.Input(
                id='percentile-input',
                type='number',
                value=80,
                min=1,
                max=100,
                step=1,
                style={'marginLeft': '10px'}
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'marginTop': '10px'})
    ], style={'display': 'flex', 'flexDirection': 'column', 'width': '20%', 'position': 'absolute', 'left': '10px', 'top': '10px'}),
    html.Div(id='graphs-container', style={'marginLeft': '25%'})
])

# 更新页面内容回调
@app.callback(
    [Output('graphs-container', 'children')],
    [Input('region-dropdown', 'value'),
     Input('band-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('time-granularity-dropdown', 'value'),
     Input('sort-indicator-dropdown', 'value'),
     Input('percentile-slider', 'value')]
)
def update_graphs(region, band, start_date, end_date, granularity, sort_indicator, percentiles):
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

    # 仅保留数值列
    numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
    filtered_df = filtered_df.set_index('utc_time')

    # 计算选择的百分位区间内的所有值的平均值
    def compute_percentile_average(group, lower_percentile, upper_percentile):
        ranked_group = group.sort_values(by=sort_indicator)
        lower_bound = int(len(ranked_group) * (lower_percentile / 100.0))
        upper_bound = int(len(ranked_group) * (upper_percentile / 100.0))
        return ranked_group.iloc[lower_bound:upper_bound + 1].mean()

    grouped = filtered_df.resample(freq).apply(lambda x: compute_percentile_average(x, percentiles[0], percentiles[1]))

    # 打印调试信息
    print("Filtered DataFrame head:", filtered_df.head())
    print("Grouped DataFrame head:", grouped.head())

    # 创建多个图表
    graphs = []
    for col in numeric_cols:
        figure = {
            'data': [{'x': grouped.index, 'y': grouped[col], 'type': 'line', 'name': col}],
            'layout': {'title': f'{col.capitalize()} - Percentile {percentiles[0]}% to {percentiles[1]}%'}
        }
        graphs.append(dcc.Graph(figure=figure))

    return [graphs]

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

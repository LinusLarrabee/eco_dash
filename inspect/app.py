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
        html.Div([
            html.Label("输入起始百分位："),
            dcc.Input(
                id='percentile-start',
                type='number',
                min=0,
                max=100,
                step=0.01,
                value=40,
                style={'marginRight': '10px'}
            ),
            html.Label("输入结束百分位："),
            dcc.Input(
                id='percentile-end',
                type='number',
                min=0,
                max=100,
                step=0.01,
                value=60
            )
        ], style={'display': 'flex', 'alignItems': 'center'}),
        html.Div(id='percentile-output')
    ], style={'display': 'flex', 'flexDirection': 'column', 'width': '20%', 'position': 'absolute', 'left': '10px', 'top': '10px'}),
    html.Div(id='graphs-container', style={'marginLeft': '25%'})
])

# 更新页面内容回调
@app.callback(
    [Output('graphs-container', 'children'),
     Output('percentile-output', 'children')],
    [Input('region-dropdown', 'value'),
     Input('band-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('time-granularity-dropdown', 'value'),
     Input('sort-indicator-dropdown', 'value'),
     Input('percentile-start', 'value'),
     Input('percentile-end', 'value')]
)
def update_graphs(region, band, start_date, end_date, granularity, sort_indicator, percentile_start, percentile_end):
    if percentile_start >= percentile_end:
        return [[], ""]

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

    # 计算加权平均
    def weighted_percentile(data, percents, sorter):
        data = data[sorter]
        num_points = len(data)
        lower_percentile = percents[0] / 100.0 * (num_points - 1)
        upper_percentile = percents[1] / 100.0 * (num_points - 1)

        lower_index = int(np.floor(lower_percentile))
        upper_index = int(np.ceil(upper_percentile))

        weights = np.zeros(num_points)

        if lower_index == upper_index:
            weights[lower_index] = 1
        else:
            weights[lower_index] = upper_index - lower_percentile
            weights[upper_index] = upper_percentile - lower_index
            if upper_index - lower_index > 1:
                weights[lower_index+1:upper_index] = 1

        # 计算加权平均
        weights /= np.sum(weights)
        weighted_data = np.dot(data.T, weights)

        return weighted_data

    # 按时间粒度聚合数据
    def get_percentile_row(x, sort_indicator, percentiles):
        sorter = np.argsort(x[sort_indicator].values)
        weighted_data = weighted_percentile(x[numeric_cols].values, [percentile_start, percentile_end], sorter)
        return pd.Series(weighted_data, index=numeric_cols)

    grouped = filtered_df.resample(freq).apply(lambda x: get_percentile_row(x, sort_indicator, [percentile_start, percentile_end]))

    # 打印第一天的调试信息
    if not grouped.empty:
        print("第一天的数据:", grouped.iloc[0])

    # 创建多个图表
    graphs = []
    for col in numeric_cols:
        figure = {
            'data': [{'x': grouped.index, 'y': grouped[col], 'type': 'line', 'name': col}],
            'layout': {'title': f'{col.capitalize()} for Percentile {percentile_start}% - {percentile_end}%'}
        }
        graphs.append(dcc.Graph(figure=figure))

    # 计算选取的用户数据百分比
    percentage_selected = (percentile_end - percentile_start)
    percentage_text = f'Selected Data Percentage: {percentage_selected:.2f}%'

    return graphs, percentage_text

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

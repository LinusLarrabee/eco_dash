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
            html.Label("选择百分位："),
            dcc.Input(
                id='percentile-start',
                type='number',
                min=0,
                max=100,
                step=0.01,
                value=50,
                style={'marginRight': '10px'}
            ),
            html.Label("到"),
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
    if int(np.floor(100 * percentile_start)) > int(np.floor(100 * percentile_end)):
        return [[], "Error: 起始百分位必须小于或等于结束百分位"]

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
    def weighted_percentile(data, percents):
        data = np.sort(data)
        num_points = len(data)
        # 在数组的前后各补一个与起止相同的数
        pad_data = np.pad(data, pad_width=(1, 1), mode='edge')

        lower_percentile = percents[0] / num_points
        upper_percentile = percents[1] / num_points

        lower_floor = int(np.floor(lower_percentile))
        upper_floor = int(np.floor(upper_percentile))
        lower_ceil = int(np.ceil(lower_percentile))
        upper_ceil = int(np.ceil(upper_percentile))

        # 洛必达
        if lower_floor == upper_floor:
            if int(lower_percentile * 10) == lower_floor * 10:
                return (pad_data[lower_floor] + pad_data[lower_floor + 1]) / 2
            return pad_data[lower_ceil]

        # 两边的非完整段
        lower_weight = lower_ceil - lower_percentile
        upper_weight = upper_percentile - upper_floor
        all_value = lower_weight * pad_data[lower_ceil] + upper_weight * pad_data[upper_floor + 1]

        for index in range(lower_ceil + 1, upper_floor + 1):
            all_value = all_value + pad_data[index]

        weighted_data = all_value / (upper_percentile - lower_percentile)

        return weighted_data

    # 按时间粒度聚合数据
    def get_percentile_row(x, sort_indicator, percentiles):
        sorter = np.argsort(x[sort_indicator].values)
        weighted_data = weighted_percentile(x[sort_indicator].values, [percentile_start, percentile_end])
        result = {col: round(weighted_data, 2) for col in numeric_cols}
        return pd.Series(result)

    grouped = filtered_df.resample(freq).apply(lambda x: get_percentile_row(x, sort_indicator, [percentile_start, percentile_end]))

    # 打印调试信息
    print("Filtered DataFrame head:", filtered_df.head())
    print("Grouped DataFrame head:", grouped.head())

    # 创建多个图表
    graphs = []
    for col in numeric_cols:
        figure = {
            'data': [{'x': grouped.index, 'y': grouped[col], 'type': 'line', 'name': col}],
            'layout': {'title': f'{col.capitalize()} for Percentile {percentile_start:.2f}% - {percentile_end:.2f}%'}
        }
        graphs.append(dcc.Graph(figure=figure))

    # 计算选取的用户数据百分比
    percentage_selected = (percentile_end - percentile_start)
    percentage_text = f'Selected Data Percentage: {percentage_selected:.2f}%'

    return graphs, percentage_text

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

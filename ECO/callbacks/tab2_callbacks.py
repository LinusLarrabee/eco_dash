from dash.dependencies import Input, Output
from dash import dcc
import pandas as pd
import numpy as np
from app import app

# 读取CSV数据
df_1d = pd.read_csv('data/data_1d_avg.csv')

@app.callback(
    [Output('graphs-container-tab2', 'children'),
     Output('percentile-output-tab2', 'children')],
    [Input('region-dropdown-tab2', 'value'),
     Input('band-dropdown-tab2', 'value'),
     Input('date-picker-range-tab2', 'start_date'),
     Input('date-picker-range-tab2', 'end_date'),
     Input('sort-indicator-dropdown-tab2', 'value'),
     Input('percentile-start-tab2', 'value'),
     Input('percentile-end-tab2', 'value'),
     Input('percentile-slider-tab2', 'value'),
     Input('intervals-input-tab2', 'value')],
    prevent_initial_call=True
)
def update_graphs_tab2(region, band, start_date, end_date, sort_indicator, percentile_start, percentile_end, percentile_slider, intervals_input):
    # 确保百分位值与滑块值一致
    if [percentile_start, percentile_end] != percentile_slider:
        percentile_start, percentile_end = percentile_slider

    if int(np.floor(100 * percentile_start)) > int(np.floor(100 * percentile_end)):
        return [[], "Error: 起始百分位必须小于或等于结束百分位"]

    # 解析起始时间和结束时间
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)

    # 过滤数据
    data = df_1d.copy()
    data['utc_time'] = pd.to_datetime(data['utc_time'])
    data = data[(data['utc_time'] >= start_datetime) & (data['utc_time'] <= end_datetime)]

    if region:
        data = data[data['region'] == region]

    if band:
        data = data[data['band'] == band]

    if data.empty:
        return [[], ""]

    # 按用户家庭计算指标
    grouped = data.groupby(['region', 'band', 'utc_time']).agg(
        {sort_indicator: 'sum'}).reset_index()
    grouped = grouped.sort_values(by=sort_indicator)

    # 计算百分位
    num_points = len(grouped)
    lower_idx = int(np.floor(num_points * (percentile_start / 100.0)))
    upper_idx = int(np.ceil(num_points * (percentile_end / 100.0)))
    sliced_data = grouped.iloc[lower_idx:upper_idx]

    # 解析区间范围
    intervals = []
    try:
        intervals = eval(intervals_input)
    except:
        return [[], "Error: 无效的区间范围"]

    # 按区间统计
    interval_counts = {}
    for interval in intervals:
        lower, upper = interval
        count = ((sliced_data[sort_indicator] > lower) & (sliced_data[sort_indicator] <= upper)).sum()
        interval_counts[interval] = count

    # 创建图表
    figure = {
        'data': [
            {'x': list(interval_counts.keys()), 'y': list(interval_counts.values()), 'type': 'bar', 'name': 'Devices'}
        ],
        'layout': {
            'title': f'Device Distribution for {sort_indicator.capitalize()} Percentile {percentile_start}% - {percentile_end}%',
            'xaxis': {'title': sort_indicator},
            'yaxis': {'title': 'Device Count'}
        }
    }
    graphs = [dcc.Graph(figure=figure)]

    # 计算选取的用户数据百分比
    percentage_selected = (percentile_end - percentile_start)
    percentage_text = f'Selected Data Percentage: {percentage_selected:.2f}%'

    return graphs, percentage_text

@app.callback(
    [Output('percentile-start-tab2', 'value'),
     Output('percentile-end-tab2', 'value')],
    [Input('percentile-slider-tab2', 'value')]
)
def sync_percentile_slider_to_input_tab2(slider_value):
    return slider_value[0], slider_value[1]

@app.callback(
    Output('percentile-slider-tab2', 'value'),
    [Input('percentile-start-tab2', 'value'),
     Input('percentile-end-tab2', 'value')]
)
def sync_percentile_input_to_slider_tab2(start_value, end_value):
    return [start_value, end_value]

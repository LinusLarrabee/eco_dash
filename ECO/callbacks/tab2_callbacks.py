from dash.dependencies import Input, Output
from dash import dcc
import pandas as pd
import numpy as np
from app import app

# 读取CSV数据
df_1d = pd.read_csv('data/data_1d_avg.csv')

def parse_intervals(interval_str):
    try:
        intervals = []
        # 拆分整个字符串为单个区间
        interval_parts = [interval.strip() for interval in interval_str.split(',')]
        # 合并区间
        combined_intervals = []
        i = 0
        while i < len(interval_parts):
            if i + 1 < len(interval_parts) and interval_parts[i + 1][0].isdigit():
                combined_intervals.append(interval_parts[i] + ',' + interval_parts[i + 1])
                i += 2
            else:
                combined_intervals.append(interval_parts[i])
                i += 1

        for interval in combined_intervals:
            interval = interval.strip()
            if interval[0] == '[':
                include_lower = True
            elif interval[0] == '(':
                include_lower = False
            else:
                raise ValueError("Invalid interval format")

            if interval[-1] == ']':
                include_upper = True
            elif interval[-1] == ')':
                include_upper = False
            else:
                raise ValueError("Invalid interval format")

            lower, upper = interval[1:-1].split(',')
            if lower == '-inf':
                lower = -np.inf
            else:
                lower = float(lower)
            if upper == 'inf':
                upper = np.inf
            else:
                upper = float(upper)
            intervals.append((lower, upper, include_lower, include_upper))
        return intervals
    except Exception as e:
        print(f"Error parsing intervals: {e}")
        return None

def generate_default_intervals(data, num_intervals=5):
    min_val = data.min()
    max_val = data.max()
    step = (max_val - min_val) / num_intervals
    intervals = []

    # 处理负无穷到最小值的区间
    intervals.append(f'(-inf,{min_val}]')

    for i in range(num_intervals):
        lower = min_val + i * step
        upper = min_val + (i + 1) * step
        if step >= 1:
            lower = round(lower)
            upper = round(upper)
        if i == 0:
            intervals.append(f'[{lower},{upper})')
        elif i == num_intervals - 1:
            intervals.append(f'({lower},{upper}]')
        else:
            intervals.append(f'({lower},{upper}]')

    # 处理最大值到正无穷的区间
    intervals.append(f'({max_val},inf)')

    return intervals

@app.callback(
    [Output('graphs-container-tab2', 'children'),
     Output('percentile-output-tab2', 'children'),
     Output('intervals-input-tab2', 'value')],
    [Input('region-dropdown-tab2', 'value'),
     Input('band-dropdown-tab2', 'value'),
     Input('date-picker-range-tab2', 'start_date'),
     Input('date-picker-range-tab2', 'end_date'),
     Input('sort-indicator-dropdown-tab2', 'value'),
     Input('percentile-start-tab2', 'value'),
     Input('percentile-end-tab2', 'value'),
     Input('percentile-slider-tab2', 'value')],
    prevent_initial_call=True
)
def update_graphs_tab2(region, band, start_date, end_date, sort_indicator, percentile_start, percentile_end, percentile_slider):
    # 确保百分位值与滑块值一致
    if [percentile_start, percentile_end] != percentile_slider:
        percentile_start, percentile_end = percentile_slider

    if int(np.floor(100 * percentile_start)) > int(np.floor(100 * percentile_end)):
        return [[], "Error: 起始百分位必须小于或等于结束百分位", ""]

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
        return [[], "", ""]

    # 按用户家庭计算指标
    grouped = data.groupby(['region', 'band', 'utc_time']).agg(
        {sort_indicator: 'sum'}).reset_index()
    grouped = grouped.sort_values(by=sort_indicator)

    # 计算百分位
    num_points = len(grouped)
    lower_idx = int(np.floor(num_points * (percentile_start / 100.0)))
    upper_idx = int(np.ceil(num_points * (percentile_end / 100.0)))
    sliced_data = grouped.iloc[lower_idx:upper_idx]

    # 生成默认区间
    intervals_input = ','.join(generate_default_intervals(sliced_data[sort_indicator]))

    # 解析区间范围
    intervals = parse_intervals(intervals_input)
    if intervals is None:
        return [[], "Error: 无效的区间范围", intervals_input]

    graphs = []
    numeric_cols = sliced_data.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        # 按区间统计
        interval_counts = {}
        for lower, upper, include_lower, include_upper in intervals:
            if include_lower and include_upper:
                count = ((sliced_data[col] >= lower) & (sliced_data[col] <= upper)).sum()
            elif include_lower:
                count = ((sliced_data[col] >= lower) & (sliced_data[col] < upper)).sum()
            elif include_upper:
                count = ((sliced_data[col] > lower) & (sliced_data[col] <= upper)).sum()
            else:
                count = ((sliced_data[col] > lower) & (sliced_data[col] < upper)).sum()
            interval_counts[f"{lower} {'[' if include_lower else '('}{','}{']' if include_upper else ')'} {upper}"] = count

        # 创建图表
        figure = {
            'data': [
                {'x': list(interval_counts.keys()), 'y': list(interval_counts.values()), 'type': 'bar', 'name': col}
            ],
            'layout': {
                'title': f'{col.capitalize()} Distribution for {sort_indicator.capitalize()} Percentile {percentile_start}% - {percentile_end}%',
                'xaxis': {'title': 'Interval'},
                'yaxis': {'title': 'Count'}
            }
        }
        graphs.append(dcc.Graph(figure=figure))

    # 计算选取的用户数据百分比
    percentage_selected = (percentile_end - percentile_start)
    percentage_text = f'Selected Data Percentage: {percentage_selected:.2f}%'

    return graphs, percentage_text, intervals_input

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

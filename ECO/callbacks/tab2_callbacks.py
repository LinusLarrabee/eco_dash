from dash.dependencies import Input, Output, State, ALL
from dash import dcc, html
import pandas as pd
import numpy as np
from app import app
from .utils import parse_intervals, generate_default_intervals

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
     Input('num-intervals-dropdown-tab2', 'value')],
    [State({'type': 'intervals-input-tab2', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def update_graphs_tab2(region, band, start_date, end_date, sort_indicator, percentile_start, percentile_end, percentile_slider, num_intervals, intervals_inputs):
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
        {col: 'sum' for col in data.columns if col not in ['utc_time', 'region', 'band']}).reset_index()
    grouped = grouped.sort_values(by=sort_indicator)

    # 计算百分位
    num_points = len(grouped)
    lower_idx = int(np.floor(num_points * (percentile_start / 100.0)))
    upper_idx = int(np.ceil(num_points * (percentile_end / 100.0)))
    sliced_data = grouped.iloc[lower_idx:upper_idx]

    graphs = []
    numeric_cols = sliced_data.select_dtypes(include=[np.number]).columns.tolist()
    intervals_list = []
    for i, col in enumerate(numeric_cols):
        # 生成默认区间
        min_val = np.floor(sliced_data[col].min())
        max_val = np.ceil(sliced_data[col].max())
        default_intervals = ','.join(generate_default_intervals(sliced_data[col], num_intervals))

        # 使用用户提供的区间范围或默认区间范围
        intervals_input = intervals_inputs[i] if intervals_inputs and i < len(intervals_inputs) and intervals_inputs[i] else default_intervals
        intervals = parse_intervals(intervals_input)
        if intervals is None:
            return [[], f"Error: 无效的区间范围 {intervals_input}"]

        intervals_list.append(intervals_input)

        # 按区间统计
        interval_counts = {}
        for lower, upper, include_lower, include_upper in intervals:
            if lower == -np.inf:
                count = (sliced_data[col] <= upper).sum() if include_upper else (sliced_data[col] < upper).sum()
            elif upper == np.inf:
                count = (sliced_data[col] >= lower).sum() if include_lower else (sliced_data[col] > lower).sum()
            else:
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
        graphs.append(html.Div([
            dcc.Graph(figure=figure),
            html.Label(f'{col.capitalize()} Interval Range:'),
            dcc.Textarea(
                id={'type': 'intervals-input-tab2', 'index': i},
                value=intervals_input,
                style={'width': '100%', 'height': '50px'}
            )
        ], style={'display': 'flex', 'flexDirection': 'column', 'marginBottom': '20px'}))

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

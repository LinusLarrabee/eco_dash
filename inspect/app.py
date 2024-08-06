import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np

# 读取CSV数据
df_15min = pd.read_csv('data_15min.csv')
df_1h = pd.read_csv('data_1h_avg.csv')
df_1d = pd.read_csv('data_1d_avg.csv')

# 创建 Dash 应用
app = dash.Dash(__name__)

# 定义页面布局
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Label("选择 Region："),
        dcc.Dropdown(
            id='region-dropdown',
            options=[
                {'label': 'APS1', 'value': 'aps1'},
                {'label': 'USE1', 'value': 'use1'},
                {'label': 'EUW1', 'value': 'euw1'}
            ],
            value='aps1'
        ),
        html.Label("选择 Band："),
        dcc.Dropdown(
            id='band-dropdown',
            options=[
                {'label': '2.4G', 'value': '2.4g'},
                {'label': '5G', 'value': '5g'},
                {'label': '6G', 'value': '6g'}
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
        html.Label("选择起始日期："),
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=pd.to_datetime('2024-01-01'),
            max_date_allowed=pd.to_datetime('2024-12-31'),
            initial_visible_month=pd.to_datetime('2024-01-01'),
            date=pd.to_datetime('2024-01-01').date(),
        ),
        html.Div([
            html.Label("选择组别："),
            dcc.Input(
                id='groups-input',
                type='number',
                min=1,
                value=1,
                style={'width': '100px'}
            ),
            dcc.Input(
                id='start-time-input',
                type='text',
                placeholder='HH:MM',
                value='00:00',
                style={'marginLeft': '10px'}
            )
        ], style={'display': 'flex', 'alignItems': 'center'}),
        html.Label("选择百分位："),
        html.Div([
            dcc.Input(
                id='percentile-start',
                type='number',
                min=0,
                max=100,
                step=1,
                value=50,
                debounce=True,
                style={'marginRight': '10px'}
            ),
            html.Label("到"),
            dcc.Input(
                id='percentile-end',
                type='number',
                min=0,
                max=100,
                step=1,
                value=60,
                debounce=True,
                style={'marginLeft': '10px'}
            )
        ], style={'display': 'flex', 'alignItems': 'center'}),
        dcc.RangeSlider(
            id='percentile-slider',
            min=0,
            max=100,
            step=1,
            value=[50, 60],
            marks={i: str(i) for i in range(0, 101, 10)}
        ),
        html.Div(id='percentile-output')
    ], style={'display': 'flex', 'flexDirection': 'column', 'width': '25%', 'position': 'absolute', 'left': '10px', 'top': '10px'}),
    html.Div(id='graphs-container', style={'marginLeft': '30%'})
])

@app.callback(
    [Output('graphs-container', 'children'),
     Output('percentile-output', 'children'),
     Output('start-time-input', 'style')],
    [Input('region-dropdown', 'value'),
     Input('band-dropdown', 'value'),
     Input('start-date-picker', 'date'),
     Input('start-time-input', 'value'),
     Input('groups-input', 'value'),
     Input('time-granularity-dropdown', 'value'),
     Input('percentile-start', 'value'),
     Input('percentile-end', 'value'),
     Input('percentile-slider', 'value')],
    prevent_initial_call=True
)
def update_graphs(region, band, start_date, start_time, groups, granularity, percentile_start, percentile_end, percentile_slider):
    # 确保百分位值与滑块值一致
    if [percentile_start, percentile_end] != percentile_slider:
        percentile_start, percentile_end = percentile_slider

    if int(np.floor(100 * percentile_start)) > int(np.floor(100 * percentile_end)):
        return [[], "Error: 起始百分位必须小于或等于结束百分位", {'display': 'block', 'marginLeft': '10px'}]

    # 控制时间输入框的显示
    if granularity in ['7d', '1d']:
        time_input_style = {'display': 'none'}
    else:
        time_input_style = {'display': 'block', 'marginLeft': '10px'}

    # 解析起始时间和日期
    start_datetime = pd.to_datetime(f"{start_date} {start_time}")

    if granularity == '7d':
        end_datetime = start_datetime + pd.Timedelta(days=7 * groups)
    elif granularity == '15min':
        end_datetime = start_datetime + pd.Timedelta(minutes=15 * groups)
    elif granularity == '1h':
        end_datetime = start_datetime + pd.Timedelta(hours=groups - 1)
    elif granularity == '1d':
        end_datetime = start_datetime + pd.Timedelta(days=groups - 1)

    # 根据时间粒度选择对应的数据源
    if granularity == '15min':
        data = df_15min.copy()
    elif granularity == '1h':
        data = df_1h.copy()
    elif granularity == '1d' or granularity == '7d':
        data = df_1d.copy()

    # 过滤数据
    data['utc_time'] = pd.to_datetime(data['utc_time'])
    data = data[(data['utc_time'] >= start_datetime) & (data['utc_time'] <= end_datetime)]

    if region:
        data = data[data['region'] == region]

    if band:
        data = data[data['band'] == band]

    if data.empty:
        return [[], "Error: 查询结果为空", time_input_style]

    # 聚合7天的数据
    if granularity == '7d':
        data = data.resample('7D', on='utc_time').mean().reset_index()

    # 仅保留数值列
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    data = data.set_index('utc_time')

    # 计算加权平均
    def weighted_percentile(data, percents, sorter):
        print(f"Data: {data}")
        print(f"Percents: {percents}")

        num_points = len(data)
        pad_data = np.pad(data[sorter], pad_width=(1, 1), mode='edge')

        lower_percentile = percents[0] / 100 * num_points
        upper_percentile = percents[1] / 100 * num_points

        lower_floor = int(np.floor(lower_percentile))
        upper_floor = int(np.floor(upper_percentile))
        lower_ceil = int(np.ceil(lower_percentile))
        upper_ceil = int(np.ceil(upper_percentile))

        if lower_floor == upper_floor:
            if upper_percentile - lower_percentile < 10e-8:
                return (pad_data[lower_floor] + pad_data[lower_floor + 1]) / 2
            return pad_data[lower_ceil]

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
        if len(sorter) <= 2:
            return pd.Series({col: np.nan for col in numeric_cols})
        weighted_values = {col: weighted_percentile(x[col].values, percentiles, sorter) for col in numeric_cols}
        return pd.Series(weighted_values)

    grouped = data.resample(granularity).apply(lambda x: get_percentile_row(x, 'wan_throughput', [percentile_start, percentile_end]))

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

    return graphs, percentage_text, time_input_style

@app.callback(
    [Output('percentile-start', 'value'),
     Output('percentile-end', 'value')],
    [Input('percentile-slider', 'value')]
)
def sync_percentile_slider_to_input(slider_value):
    return slider_value[0], slider_value[1]

@app.callback(
    Output('percentile-slider', 'value'),
    [Input('percentile-start', 'value'),
     Input('percentile-end', 'value')]
)
def sync_percentile_input_to_slider(start_value, end_value):
    return [start_value, end_value]

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

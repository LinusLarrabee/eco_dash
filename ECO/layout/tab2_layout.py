import pandas as pd
from dash import dcc, html

layout = html.Div([
    html.H1('Tab 2 Content', style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Label("选择 Region："),
            dcc.Dropdown(
                id='region-dropdown-tab2',
                options=[
                    {'label': 'APS1', 'value': 'aps1'},
                    {'label': 'USE1', 'value': 'use1'},
                    {'label': 'EUW1', 'value': 'euw1'}
                ],
                value='aps1',
                style={'width': '100%'}
            ),
            html.Br(),  # 添加间距
            html.Label("选择 Band："),
            dcc.Dropdown(
                id='band-dropdown-tab2',
                options=[
                    {'label': '2.4G', 'value': '2.4g'},
                    {'label': '5G', 'value': '5g'},
                    {'label': '6G', 'value': '6g'}
                ],
                value='2.4g',
                style={'width': '100%'}
            ),
            html.Br(),  # 添加间距
            html.Label("选择起始日期："),
            dcc.DatePickerRange(
                id='date-picker-range-tab2',
                min_date_allowed=pd.to_datetime('2024-01-01'),
                max_date_allowed=pd.to_datetime('2024-12-31'),
                start_date=pd.to_datetime('2024-07-23').date(),
                end_date=pd.to_datetime('2024-07-30').date(),
                style={'width': '100%'}
            ),
            html.Br(),  # 添加间距
            html.Label("选择排序指标："),
            dcc.Dropdown(
                id='sort-indicator-dropdown-tab2',
                options=[
                    {'label': 'WAN Throughput', 'value': 'wan_throughput'},
                    {'label': 'Client Online', 'value': 'client_online'},
                    {'label': 'Bandwidth', 'value': 'bandwidth'},
                    {'label': 'Airtime Utilization', 'value': 'airtime_utilization'},
                    {'label': 'Congestion Rate', 'value': 'congestion_rate'},
                    {'label': 'Noise', 'value': 'noise'},
                    {'label': 'Packet Error Rate', 'value': 'packet_error_rate'}
                ],
                value='wan_throughput',
                style={'width': '100%'}
            ),
            html.Br(),  # 添加间距
            html.Label("选择百分位："),
            html.Div([
                dcc.Input(
                    id='percentile-start-tab2',
                    type='number',
                    min=0,
                    max=100,
                    step=1,
                    value=70,
                    debounce=True,
                    style={'marginRight': '10px'}
                ),
                html.Label("到"),
                dcc.Input(
                    id='percentile-end-tab2',
                    type='number',
                    min=0,
                    max=100,
                    step=1,
                    value=90,
                    debounce=True,
                    style={'marginLeft': '10px'}
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Br(),  # 添加间距
            dcc.RangeSlider(
                id='percentile-slider-tab2',
                min=0,
                max=100,
                step=1,
                value=[70, 90],
                marks={i: str(i) for i in range(0, 101, 10)}
            ),
            html.Br(),  # 添加间距
            html.Label("输入区间范围："),
            dcc.Textarea(
                id='intervals-input-tab2',
                value='[0,3],(3,6],(6,9]',
                style={'width': '100%', 'height': '100px'}
            ),
            html.Div(id='percentile-output-tab2')
        ], style={'flex': '1', 'padding': '20px'}),  # 左侧布局
        html.Div(id='graphs-container-tab2', style={'flex': '3', 'padding': '20px'})  # 右侧布局
    ], style={'display': 'flex', 'flexDirection': 'row'})  # 设置为左右布局
])

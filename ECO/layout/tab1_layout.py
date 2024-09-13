import pandas as pd
from dash import dcc, html

layout = html.Div([
    html.Div([
        html.Div([
            html.Label("选择 Region："),
            dcc.Dropdown(
                id='region-dropdown',
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
                id='band-dropdown',
                options=[
                    {'label': '2.4G', 'value': '2.4g'},
                    {'label': '5G', 'value': '5g'},
                    {'label': '6G', 'value': '6g'}
                ],
                value='2.4g',
                style={'width': '100%'}
            ),
            html.Br(),  # 添加间距
            html.Label("选择时间粒度："),
            dcc.Dropdown(
                id='time-granularity-dropdown',
                options=[
                    # 不提供原始值选项
                    # {'label': 'raw', 'value': 'raw'},
                    {'label': '1 hour', 'value': '1h'},
                    {'label': '1 day', 'value': '1d'},
                    # {'label': '7 days', 'value': '7d'},
                    # {'label': '1 month', 'value': '1m'},
                    # {'label': '3 months', 'value': '1q'},
                    # {'label': '1 year', 'value': '1y'}
                ],
                value='1h',
                style={'width': '100%'}
            ),


            # html.Br(),  # 添加间距
            # html.Label("选择起始日期："),
            # dcc.DatePickerSingle(
            #     id='start-date-picker',
            #     min_date_allowed=pd.to_datetime('2024-01-01'),
            #     max_date_allowed=pd.to_datetime('2024-12-31'),
            #     initial_visible_month=pd.to_datetime('2024-07-23'),
            #     date=pd.to_datetime('2024-07-23').date(),
            # ),
            # html.Br(),  # 添加间距
            # html.Div([
            #     html.Label("选择组别："),
            #     dcc.Input(
            #         id='groups-input',
            #         type='number',
            #         min=1,
            #         value=1,
            #         style={'width': '100px'}
            #     ),
            #     dcc.Input(
            #         id='start-time-input',
            #         type='text',
            #         placeholder='HH:MM',
            #         value='00:00',
            #         style={'marginLeft': '10px'}
            #     )
            # ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Label("选择起止日期："),
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=pd.to_datetime('2024-01-01'),
                max_date_allowed=pd.to_datetime('2024-12-31'),
                start_date=pd.to_datetime('2024-07-23').date(),
                end_date=pd.to_datetime('2024-07-30').date(),
            ),
            html.Br(),  # 添加间距
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
                value='wan_throughput',
                style={'width': '100%'}
            ),
            html.Br(),  # 添加间距
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
            html.Br(),  # 添加间距
            dcc.RangeSlider(
                id='percentile-slider',
                min=0,
                max=100,
                step=1,
                value=[50, 60],
                marks={i: str(i) for i in range(0, 101, 10)}
            ),
            html.Div(id='percentile-output')
        ], style={'flex': '1', 'padding': '20px'}),  # 左侧布局
        html.Div(id='graphs-container', style={'flex': '3', 'padding': '20px'})  # 右侧布局
    ], style={'display': 'flex', 'flexDirection': 'row'})  # 设置为左右布局
])

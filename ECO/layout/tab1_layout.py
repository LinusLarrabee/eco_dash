import pandas as pd
from dash import dcc, html

layout = html.Div([
    html.Div([
        html.Div([
            # 选择数据分区
            html.Label("选择 Region："),
            dcc.Dropdown(
                id='region-selector',
                options=[
                    {'label': 'US-East-1', 'value': 'us-east-1'},
                    {'label': 'AP-Southeast-1', 'value': 'ap-southeast-1'},
                    {'label': 'EU-West-1', 'value': 'eu-west-1'}
                ],
                placeholder="Select an AWS region"
            ),
            html.Div(id='link-output'),  # 用于显示动态生成的链接
            html.Br(),  # 添加间距

            # 选择时间及粒度（数据源）
            html.Label("选择起止日期："),
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=pd.to_datetime('2024-07-01'),
                # max_date_allowed=pd.to_datetime('2024-12-31'),
                start_date=pd.to_datetime('2024-09-07').date(),
                end_date=pd.to_datetime('2024-09-10').date(),
            ),

            dcc.Store(id='filtered-data'),


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


            html.Br(),  # 添加间距
            html.Label("选择压缩维度："),
            dcc.Dropdown(
                id='agg-dimension-dropdown',
                options=[
                    {'label': 'Time', 'value': 'time'},
                    {'label': 'Network', 'value': 'network'}
                ],
                value='time',  # 默认值
                clearable=False,
                style={'width': '100%'}
            ),

            html.Br(),  # 添加间距

            html.Label("选择 Band："),
            dcc.Dropdown(
                id='band-dropdown',
                options=[
                    {'label': '2.4G', 'value': '2.4GHz'},
                    {'label': '5G', 'value': '5GHz'},
                    {'label': '6G', 'value': '6GHz'},
                    {'label': 'All', 'value': '2.4GHz'}
                ],
                value='2.4GHz',
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
            html.Br(),  # 添加间距
            html.Label("选择排序指标："),
            dcc.Dropdown(
                id='sort-indicator-dropdown',
                options=[
                    {'label': 'Average RX Rate', 'value': 'average_rx_rate'},
                    {'label': 'Average TX Rate', 'value': 'average_tx_rate'},
                    {'label': 'Congestion Score', 'value': 'congestion_score'},
                    # {'label': 'WiFi Coverage Score', 'value': 'wifi_coverage_score'},
                    {'label': 'Noise', 'value': 'noise'},
                    {'label': 'Error Rate', 'value': 'errors_rate'},
                    {'label': 'WAN Bandwidth', 'value': 'wan_bandwidth'}
                ],
                value='average_rx_rate',  # 默认选中 WAN Bandwidth
                style={'width': '100%'}
            ),


            html.Br(),
            html.Label("选择百分位："),
            html.Br(),
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

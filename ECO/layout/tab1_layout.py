import pandas as pd
from dash import dcc, html
from config.granularity_config import granularity_options

layout = html.Div([
    html.Div([
        html.Div([
            dcc.Store(id='filtered-data'),  # 用于存储 Tab 1 中的过滤后的数据
            dcc.Store(id='param-store', data={
                'start_date': None,
                'end_date': None,
                'time_granularity': None,
                'metric_granularity': None,
                'connection_type_path': None
            }),

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
                min_date_allowed=pd.to_datetime('2024-09-01'),
                # max_date_allowed=pd.to_datetime('2024-12-31'),
                start_date=pd.to_datetime('2024-09-07').date(),
                end_date=pd.to_datetime('2024-09-10').date(),
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


            # 在 layout 中动态生成下拉菜单
            html.Br(),  # 添加间距
            html.Label("选择指标维度："),
            dcc.Dropdown(
                id='metric-granularity-dropdown',
                options=[{'label': granularity_options[key]['label'], 'value': granularity_options[key]['value']}
                         for key in granularity_options],  # 动态生成选项
                value='controller',  # 默认选项
                style={'width': '100%'}
            ),

            html.Br(),  # 添加间距
            html.Label("选择 Connection-Type："),
            dcc.Dropdown(
                id='band-dropdown',
                options=[
                    {'label': '2.4G', 'value': '2.4GHz'},
                    {'label': '5G', 'value': '5GHz'},
                    {'label': '6G', 'value': '6GHz'},
                    {'label': 'Ethernet', 'value': 'ethernet'},
                    {'label': 'All', 'value': 'all'}
                ],
                value='2.4GHz',
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
                value='network',  # 默认值
                clearable=False,
                style={'width': '100%'}
            ),

            html.Br(),  # 添加间距
            html.Label("选择排序指标："),
            dcc.Dropdown(
                id='sort-indicator-dropdown',
                options=[
                    # {'label': 'Average RX Rate', 'value': 'average_rx_rate'},
                    # {'label': 'Average TX Rate', 'value': 'average_tx_rate'},
                    # {'label': 'Congestion Score', 'value': 'congestion_score'},
                    # # {'label': 'WiFi Coverage Score', 'value': 'wifi_coverage_score'},
                    # {'label': 'Noise', 'value': 'noise'},
                    # {'label': 'Error Rate', 'value': 'errors_rate'},
                    # {'label': 'WAN Bandwidth', 'value': 'wan_bandwidth'}
                ],
                # value='average_rx_rate',  # 默认选中 WAN Bandwidth
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

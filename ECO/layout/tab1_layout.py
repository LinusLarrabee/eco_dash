from dash import dcc, html

layout = html.Div([
    html.H1('Tab 1 Content'),
    # Tab 1 specific layout
    html.Div([
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
                initial_visible_month=pd.to_datetime('2024-07-23'),
                date=pd.to_datetime('2024-07-23').date(),
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
])

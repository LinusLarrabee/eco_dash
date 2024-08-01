import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# 创建 Dash 应用
app = dash.Dash(__name__)

# 设置 PostgreSQL 连接
DATABASE_URI = 'postgresql+psycopg2://superset:superset@localhost:5432/qoe'
engine = create_engine(DATABASE_URI)

# 从数据库读取数据
def fetch_data():
    query = "SELECT * FROM data"
    df = pd.read_sql(query, engine)
    return df

df = fetch_data()

# 定义页面布局
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Label("选择 Region："),
        dcc.Dropdown(
            id='region-dropdown',
            options=[
                {'label': 'use1', 'value': 'use1'},
                {'label': 'aps1', 'value': 'aps1'},
                {'label': 'euw1', 'value': 'euw1'}
            ],
            value='use1'
        ),
        html.Label("选择 Band："),
        dcc.Dropdown(
            id='band-dropdown',
            options=[
                {'label': '2.4g', 'value': '2.4g'},
                {'label': '5g', 'value': '5g'},
                {'label': '6g', 'value': '6g'}
            ],
            value='2.4g'
        )
    ], style={'display': 'flex', 'flexDirection': 'column', 'width': '20%', 'position': 'absolute', 'left': '10px', 'top': '10px'}),
    html.Div(id='page-content', style={'marginLeft': '25%'})
])

# 定义主页内容
index_page = html.Div([
    html.H1("主页"),
    dcc.Link('跳转到页面 1', href='/page-1'),
    html.Br(),
    dcc.Link('跳转到页面 2', href='/page-2'),
])

# 定义页面 1 内容
page_1_layout = html.Div([
    html.H1("页面 1"),
    html.Label("选择指标："),
    dcc.Dropdown(
        id='indicator-dropdown',
        options=[
            {'label': '指标1', 'value': 'indicator1'},
            {'label': '指标2', 'value': 'indicator2'},
            {'label': '指标3', 'value': 'indicator3'}
        ],
        value='indicator1'
    ),
    html.Label("选择百分位："),
    dcc.Slider(
        id='percentile-slider',
        min=0,
        max=100,
        step=1,
        value=50
    ),
    html.Div(id='result-output'),
    html.Br(),
    dcc.Link('返回主页', href='/')
])

# 定义页面 2 内容
page_2_layout = html.Div([
    html.H1("页面 2"),
    html.P("这里可以放置不同的内容，如图表或其他组件。"),
    html.Br(),
    dcc.Link('返回主页', href='/')
])

# 更新页面内容回调
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return index_page

# 页面 1 的回调函数
@app.callback(
    Output('result-output', 'children'),
    [Input('indicator-dropdown', 'value'),
     Input('percentile-slider', 'value'),
     Input('region-dropdown', 'value'),
     Input('band-dropdown', 'value')]
)
def update_output(indicator, percentile, region, band):
    filtered_df = df[(df['region'] == region) & (df['band'] == band)]
    values = filtered_df[indicator].dropna()
    result = np.percentile(values, percentile)
    return f'选择的百分位数值为: {result}'

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

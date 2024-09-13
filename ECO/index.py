import logging
from dash import dcc, html
from dash.dependencies import Input, Output
from app import app
from layout import tab1_layout, tab2_layout
import callbacks.tab1_callbacks
import callbacks.tab2_callbacks

# 全局配置 logging
logging.basicConfig(
    filename='dash_app.log',  # 日志文件名
    level=logging.INFO,  # 日志级别
    format='%(asctime)s - %(levelname)s - %(message)s'  # 日志格式
)

# 示例日志信息
logging.info("Dash app is starting...")

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Tab 1', value='tab1'),
        dcc.Tab(label='Tab 2', value='tab2'),
    ]),
    html.Div(id='tabs-content')
])

# 回调函数更新不同 Tab 的内容
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    logging.info(f"Tab switched to: {tab}")  # 每次切换 Tab 都记录日志
    if tab == 'tab1':
        return tab1_layout
    elif tab == 'tab2':
        return tab2_layout

if __name__ == '__main__':
    logging.info("Running the Dash app...")
    app.run_server(debug=True, host='0.0.0.0', port=8050)

import logging
from dash import dcc, html
from dash.dependencies import Input, Output
from app import app
from layout import tab1_layout, tab2_layout
import callbacks.tab1_callbacks
import callbacks.tab2_callbacks
import os
import logging
from logging.handlers import TimedRotatingFileHandler

# 定义日志文件存放的子目录
log_dir = 'logs'  # 子目录
os.makedirs(log_dir, exist_ok=True)  # 如果目录不存在则创建

# 配置日志处理器 - 按天分割日志文件
log_handler = TimedRotatingFileHandler(
    filename=os.path.join(log_dir, 'dash_app.log'),  # 指定完整路径
    when='midnight',  # 每天午夜分割日志
    interval=1,  # 间隔一天
    backupCount=7  # 保留最近7天的日志文件
)

# 设置日志格式
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

# 获取根日志记录器并添加处理器
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)


# 示例日志信息
logging.info("Dash app is starting...")

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='ECO', value='tab1'),
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

from dash.dependencies import Input, Output, State
from app import app
from data.s3_utils import get_s3_data  # 从 utils 文件夹导入 get_s3_data
import dash_html_components as html

# 定义从 S3 读取数据并展示的回调
@app.callback(
    Output('s3-data-output', 'children'),
    [Input('load-s3-data-button', 'n_clicks')],
    [State('s3-bucket-input', 'value'),
     State('s3-key-input', 'value')]
)
def update_s3_data(n_clicks, bucket, s3_key):
    if n_clicks > 0:
        df = get_s3_data(bucket, s3_key)
        if df is not None:
            # 成功读取数据，返回表格格式的数据
            return html.Table([
                                  html.Tr([html.Th(col) for col in df.columns])  # 表头
                              ] + [
                                  html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(min(len(df), 10))
                              ])  # 显示前10行数据
        else:
            return "Error loading data from S3."
    return "Click the button to load data."

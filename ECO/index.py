from dash import dcc, html
from dash.dependencies import Input, Output
from app import app
from layout import tab1_layout, tab2_layout, tab3_layout  # 引入 tab3_layout
import callbacks.tab1_callbacks
import callbacks.tab2_callbacks
import callbacks.tab3_callbacks  # 引入 tab3_callbacks 回调

# 更新布局，添加 Tab 3
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Tab 1', value='tab1'),
        dcc.Tab(label='Tab 2', value='tab2'),
        dcc.Tab(label='Tab 3', value='tab3'),  # 添加 Tab 3
    ]),
    html.Div(id='tabs-content')
])

# 更新回调逻辑，处理 Tab 3
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab1':
        return tab1_layout
    elif tab == 'tab2':
        return tab2_layout
    elif tab == 'tab3':  # 添加 Tab 3 的渲染逻辑
        return tab3_layout

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)

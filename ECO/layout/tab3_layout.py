from dash import dcc, html

def tab3_layout():
    return html.Div([
        html.H2("S3 Data Viewer"),

        # 输入 S3 桶和对象的输入框
        html.Div([
            dcc.Input(
                id="s3-bucket-input",
                type="text",
                placeholder="Enter S3 Bucket Name",
                value="aps1-tauc-data-analysis"
            ),
            dcc.Input(
                id="s3-key-input",
                type="text",
                placeholder="Enter S3 Key (e.g., path/to/file.parquet)",
                value="extracted/ap_data/dt=2022-04-07/part-00000.snappy.parquet"
            )
        ], style={'padding': '20px'}),

        # 加载数据按钮
        html.Button("Load Data", id="load-s3-data-button", n_clicks=0),

        # 展示数据的区域
        html.Div(id="s3-data-output")
    ])

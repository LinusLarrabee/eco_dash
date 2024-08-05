import os
import psycopg2
import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px

# 从环境变量中获取数据库连接参数
db_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

# 创建数据库连接
conn = psycopg2.connect(**db_params)

# 查询数据
query = "SELECT date, value FROM time_series_data"
df = pd.read_sql_query(query, conn)

# 关闭连接
conn.close()

# 创建 Dash 应用
app = Dash(__name__)

fig = px.line(df, x='date', y='value', title='Time Series Data')

app.layout = html.Div(children=[
    html.H1(children='Time Series Data Visualization'),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

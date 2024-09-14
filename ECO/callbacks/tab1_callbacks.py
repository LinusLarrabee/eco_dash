import logging

from app import app
from data import s3_utils
from dash import no_update
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output


# 回调函数，用于跳转到不同的子域名
@app.callback(
    Output('link-output', 'children'),
    Input('region-selector', 'value')
)
def update_link(region):
    if region:
        url_map = {
            'us-east-1': 'https://baidu.com',
            'ap-southeast-1': 'http://ap-southeast-1.yourdomain.com',
            'eu-west-1': 'http://eu-west-1.yourdomain.com'
        }
        return html.A('Open in new tab', href=url_map[region], target='_blank')
    return ""



@app.callback(
    [Output('graphs-container', 'children'),
     Output('percentile-output', 'children')],
    [Input('band-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('time-granularity-dropdown', 'value'),
     Input('sort-indicator-dropdown', 'value'),
     Input('percentile-start', 'value'),
     Input('percentile-end', 'value'),
     Input('percentile-slider', 'value')],
    prevent_initial_call=True
)
def update_graphs(band, start_date, end_date, granularity, sort_indicator, percentile_start, percentile_end, percentile_slider):
    # 确保百分位值与滑块值一致
    if [percentile_start, percentile_end] != percentile_slider:
        percentile_start, percentile_end = percentile_slider

    if int(np.floor(100 * percentile_start)) > int(np.floor(100 * percentile_end)):
        return [[], "Error: 起始百分位必须小于或等于结束百分位", {'display': 'block', 'marginLeft': '10px'}]

    # 控制时间输入框的显示
    if granularity in ['7d', '1d']:
        time_input_style = {'display': 'none'}
    else:
        time_input_style = {'display': 'block', 'marginLeft': '10px'}

    # 解析起止日期，确保 start_datetime 和 end_datetime 包括完整的时间范围
    start_datetime = pd.to_datetime(f"{start_date}").replace(hour=0, minute=0, second=0)  # 设置为当天 00:00:00
    end_datetime = pd.to_datetime(f"{end_date}").replace(hour=23, minute=59, second=59)  # 设置为当天 23:59:59

    # 从 S3 获取数据
    data = s3_utils.get_s3_data(start_datetime, end_datetime, granularity, 'ap_data/')
    logging.info(data)

    # 将 10 位时间戳（Unix 时间）转换为 datetime 格式
    data['collection_time'] = pd.to_datetime(data['collection_time'], unit='s')

    # 过滤数据，确保同时过滤日期和时间
    data = data[(data['collection_time'] >= start_datetime) & (data['collection_time'] <= end_datetime)]

    logging.info(data)


    if band:
        data = data[data['band'] == band]

    # 将新的指标加入数据处理逻辑
    numeric_cols = ['average_rx_rate', 'average_tx_rate', 'congestion_score',
                     'noise', 'errors_rate', 'wan_bandwidth']

    data = data.set_index('collection_time_agg')

    # 按时间粒度聚合数据
    # def get_percentile_row(x, sort_indicator, percentiles):
    #     sorter = np.argsort(x[sort_indicator].values)
    #     if len(sorter) <= 2:
    #         return pd.Series({col: np.nan for col in numeric_cols})
    #     weighted_values = {col: weighted_percentile(x[col].values, percentiles, sorter) for col in numeric_cols}
    #     return pd.Series(weighted_values)

    # grouped = data.resample(granularity).apply(lambda x: get_percentile_row(x, sort_indicator, [percentile_start, percentile_end]))
    logging.info(f"Sort indicator show: {sort_indicator}")

    # 定义每个分组的处理函数
    def get_percentile_row(group, sort_indicator, percentiles):
        sorter = np.argsort(group[sort_indicator].values)
        if len(sorter) <= 2:
            return pd.Series({col: np.nan for col in numeric_cols})

        # 对每一列应用加权百分位排序
        weighted_values = {col: weighted_percentile(group[col].values, percentiles, sorter) for col in numeric_cols}
        return pd.Series(weighted_values)

    # 对每个 collection_time_agg 进行分组并应用加权百分位排序
    grouped = data.groupby('collection_time_agg').apply(
        lambda x: get_percentile_row(x, sort_indicator, [percentile_start, percentile_end])
    )
    # 显示聚合后的数据
    print(grouped)

    # 创建多个图表
    graphs = []
    for col in numeric_cols:
        figure = {
            'data': [{'x': grouped.index, 'y': grouped[col], 'type': 'line', 'name': col}],
            'layout': {'title': f'{col.capitalize()} for {sort_indicator.capitalize()} Percentile {percentile_start:.2f}% - {percentile_end:.2f}%'}
        }
        graphs.append(dcc.Graph(figure=figure))

    # 计算选取的用户数据百分比
    percentage_selected = (percentile_end - percentile_start)
    percentage_text = f'Selected Data Percentage: {percentage_selected:.2f}%'

    return graphs, percentage_text

from dash import no_update

# 回调1：滑块值更新输入框
@app.callback(
    [Output('percentile-start', 'value'),
     Output('percentile-end', 'value')],
    [Input('percentile-slider', 'value')]
)
def sync_percentile_slider_to_input(slider_value):
    try:
        return slider_value[0], slider_value[1]
    except Exception as e:
        logging.error(f"Error syncing slider to input: {e}")
        return no_update, no_update

# 回调2：输入框值更新滑块
@app.callback(
    Output('percentile-slider', 'value'),
    [Input('percentile-start', 'value'),
     Input('percentile-end', 'value')]
)
def sync_percentile_input_to_slider(start_value, end_value):
    try:
        return [start_value, end_value]
    except Exception as e:
        logging.error(f"Error syncing input to slider: {e}")
        return no_update


import numpy as np
import logging

# 定义加权百分位函数并添加日志
def weighted_percentile(data, percents, sorter):
    logging.info(f"Data before processing: {data}")
    logging.info(f"Percents: {percents}, Sorter: {sorter}")

    num_points = len(data)
    pad_data = np.pad(data[sorter], pad_width=(1, 1), mode='edge')

    logging.info(f"Padded Data: {pad_data}")

    lower_percentile = percents[0] / 100 * num_points
    upper_percentile = percents[1] / 100 * num_points

    lower_floor = int(np.floor(lower_percentile))
    upper_floor = int(np.floor(upper_percentile))
    lower_ceil = int(np.ceil(lower_percentile))
    upper_ceil = int(np.ceil(upper_percentile))

    logging.info(f"Lower percentile: {lower_percentile}, Upper percentile: {upper_percentile}")
    logging.info(f"Lower floor: {lower_floor}, Upper floor: {upper_floor}, Lower ceil: {lower_ceil}, Upper ceil: {upper_ceil}")

    # 确保数据类型为浮点数
    pad_data = np.array(pad_data, dtype=np.float64)

    if lower_floor == upper_floor:
        if upper_percentile - lower_percentile < 10e-8:
            result = (pad_data[lower_floor] + pad_data[lower_floor + 1]) / 2
            logging.info(f"Result (floor == upper_floor): {result}")
            return result
        return pad_data[lower_ceil]

    lower_weight = lower_ceil - lower_percentile
    upper_weight = upper_percentile - upper_floor

    logging.info(f"Lower weight: {lower_weight}, Upper weight: {upper_weight}")

    all_value = lower_weight * pad_data[lower_ceil] + upper_weight * pad_data[upper_floor + 1]

    logging.info(f"All value after initial calculation: {all_value}")

    for index in range(lower_ceil + 1, upper_floor + 1):
        all_value = all_value + pad_data[index]

    logging.info(f"All value after adding in range: {all_value}")

    weighted_data = all_value / (upper_percentile - lower_percentile)

    logging.info(f"Final weighted data: {weighted_data}")

    return weighted_data

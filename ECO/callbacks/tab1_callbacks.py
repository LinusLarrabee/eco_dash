from app import app
from data import s3_utils
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import logging
from config.granularity_config import granularity_options


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

# 需要更新数据源的控件
@app.callback(
    Output('filtered-data', 'data'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('time-granularity-dropdown', 'value'),
     Input('metric-granularity-dropdown', 'value')
     ],
    # prevent_initial_call=True
)
def update_data_source(start_date, end_date, time_granularity, metric_granularity):
    # 解析起止日期，确保 start_datetime 和 end_datetime 包括完整的时间范围
    start_datetime = pd.to_datetime(f"{start_date}").replace(hour=0, minute=0, second=0)  # 设置为当天 00:00:00
    end_datetime = pd.to_datetime(f"{end_date}").replace(hour=23, minute=59, second=59)  # 设置为当天 23:59:59

    # 查找对应的路径
    selected_option = granularity_options.get(metric_granularity, None)
    if selected_option:
        path = selected_option['path']

    # 从 S3 获取数据，使用动态路径
    data = s3_utils.get_s3_data(start_datetime, end_datetime, time_granularity, path)
    logging.info(data)

    # 将 10 位时间戳（Unix 时间）转换为 datetime 格式
    data['collection_time'] = pd.to_datetime(data['collection_time'], unit='s')

    # 过滤数据，确保同时过滤日期和时间
    filtered_data = data[(data['collection_time'] >= start_datetime) & (data['collection_time'] <= end_datetime)]
    logging.info(filtered_data)

    # 返回过滤后的数据，存储在 dcc.Store 中
    return filtered_data.to_dict('records')


@app.callback(
    [Output('graphs-container', 'children'),
     Output('percentile-output', 'children')],
    [Input('band-dropdown', 'value'),
     Input('filtered-data', 'data'),
     Input('metric-granularity-dropdown', 'value'),
     Input('sort-indicator-dropdown', 'value'),
     Input('percentile-slider', 'value'),
     Input('agg-dimension-dropdown', 'value')],  # 增加压缩维度的输入
    prevent_initial_call=True
)
def update_graphs(band, filtered_data, metric_granularity, sort_indicator, percentile_slider, agg_dimension):
    percentile_start, percentile_end = percentile_slider

    # 将传入的字典格式的 filtered_data 转为 DataFrame
    data = pd.DataFrame(filtered_data)
    logging.info(data)

    # 如果 band 被选择，则进行过滤
    if band:
        data = data[data['band'] == band]

    # 获取当前的 granularity 数据
    granularity_data = granularity_options.get(metric_granularity, {'options': [], 'default': None})

    # 提取所有数值列的 'value' 字段作为 numeric_cols
    numeric_cols = [opt['value'] for opt in granularity_data['options']]

    data = data.set_index('collection_time_agg')

    # 定义每个分组的处理函数
    def get_percentile_row(group, sort_indicator, percentiles):
        sorter = np.argsort(group[sort_indicator].values)
        if len(sorter) <= 2:
            return pd.Series({col: np.nan for col in numeric_cols})

        # 对每一列应用加权百分位排序
        weighted_values = {col: weighted_percentile(group[col].values, percentiles, sorter) for col in numeric_cols}
        return pd.Series(weighted_values)

    # 根据选择的压缩维度来决定处理方式
    if agg_dimension == 'network':
        # 网络压缩维度：按 network 或 controller_id 进行分组
        grouped = data.groupby('collection_time_agg').apply(
            lambda x: get_percentile_row(x, sort_indicator, [percentile_start, percentile_end])
        )

        # 找到排序指标 sort_indicator 对应的 label
        sort_indicator_label = next((opt['label'] for opt in granularity_data['options'] if opt['value'] == sort_indicator), sort_indicator)

        # 创建多个图表（按网络分组）
        graphs = []
        for col in numeric_cols:
            # 从 granularity_data['options'] 中找到与 col 对应的 label
            label = next((opt['label'] for opt in granularity_data['options'] if opt['value'] == col), col)

            # 创建图表
            figure = {
                'data': [{'x': grouped.index, 'y': grouped[col], 'type': 'line', 'name': col}],
                'layout': {'title': f'{label} for ({sort_indicator_label}) In {percentile_start:.2f}% - {percentile_end:.2f}%'}
            }
            graphs.append(dcc.Graph(figure=figure))

    elif agg_dimension == 'time':
        # 时间压缩维度：使用 controller_id 作为分组依据
        data = data.sort_values(by=sort_indicator)

        # 按 controller_id 进行分组
        grouped = data.groupby('controller_id')  # 使用 `controller_id` 字段分组

        graphs = []
        for controller_id, group in grouped:
            # 找到这个 controller_id 中，sort_indicator 列值在 50%-60% 的数据
            quantile_50 = group[sort_indicator].quantile(0.5)
            quantile_60 = group[sort_indicator].quantile(0.6)
            filtered_group = group[(group[sort_indicator] >= quantile_50) & (group[sort_indicator] <= quantile_60)]

            # 创建图表
            figure = {
                'data': [{'x': filtered_group.index, 'y': filtered_group[sort_indicator], 'type': 'line', 'name': f'{controller_id} - {sort_indicator}'}],
                'layout': {'title': f'Controller {controller_id} - {sort_indicator.capitalize()} In 50%-60% Percentile'}
            }
            graphs.append(dcc.Graph(figure=figure))

    # 计算选取的用户数据百分比
    percentage_selected = (percentile_end - percentile_start)
    percentage_text = f'Selected Data Percentage: {percentage_selected:.2f}%'

    return graphs, percentage_text


@app.callback(
    [Output('sort-indicator-dropdown', 'options'),
     Output('sort-indicator-dropdown', 'value')],
    [Input('metric-granularity-dropdown', 'value')]
)
def update_sort_indicator_options(selected_granularity):
    # 根据粒度从字典中获取 options 和默认值
    granularity_data = granularity_options.get(selected_granularity, {'options': [], 'default': None})
    return granularity_data['options'], granularity_data['default']


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

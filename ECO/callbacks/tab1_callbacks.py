from app import app
from data import s3_utils
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
import logging
from config.granularity_config import granularity_options
import dash_bootstrap_components as dbc



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
     Input('metric-granularity-dropdown', 'value'),
     Input('band-dropdown', 'value')]  # 新增 connection_type 输入
)
def update_data_source(start_date, end_date, time_granularity, metric_granularity, connection_type):
    # 解析起止日期，确保 start_datetime 和 end_datetime 包括完整的时间范围
    start_datetime = pd.to_datetime(f"{start_date}").replace(hour=0, minute=0, second=0)  # 设置为当天 00:00:00
    end_datetime = pd.to_datetime(f"{end_date}").replace(hour=23, minute=59, second=59)  # 设置为当天 23:59:59

    # 映射 2.4GHz、5GHz、6GHz 为 "wireless"
    if connection_type in ['2.4GHz', '5GHz', '6GHz']:
        mapped_connection_type = 'wireless'
    else:
        mapped_connection_type = connection_type

    # 根据 metric_granularity 获取配置
    selected_option = granularity_options.get(metric_granularity, None)
    if not selected_option:
        logging.error(f"Invalid metric_granularity: {metric_granularity}")
        return []

    # 根据 mapped_connection_type 获取路径
    path = selected_option['path'].get(mapped_connection_type, None)
    if not path:
        logging.error(f"Invalid path for connection_type: {connection_type} (mapped as {mapped_connection_type})")
        return []

    # 从 S3 获取数据，使用动态路径
    data = s3_utils.get_s3_data(start_datetime, end_datetime, time_granularity, path)

    # 将 10 位时间戳（Unix 时间）转换为 datetime 格式
    data['collection_time'] = pd.to_datetime(data['collection_time'], unit='s')

    # 过滤数据，确保过滤日期和时间
    filtered_data = data[(data['collection_time'] >= start_datetime) & (data['collection_time'] <= end_datetime)]
    logging.info(f"Filtered data has {len(filtered_data)} rows.")

    # 将过滤后的数据存储在 dcc.Store 中
    return filtered_data.to_dict('records')



# 保存图表绘制结果
@app.callback(
    [Output('graphs-container', 'children'),
     Output('percentile-output', 'children')],  # 把图表数据存储到 Store
    [Input('band-dropdown', 'value'),
     Input('filtered-data', 'data'),
     Input('metric-granularity-dropdown', 'value'),
     Input('sort-indicator-dropdown', 'value'),
     Input('percentile-slider', 'value'),
     Input('agg-dimension-dropdown', 'value')],  # 增加压缩维度的输入
    prevent_initial_call=True
)
def update_graphs(connection_type, filtered_data, metric_granularity, sort_indicator, percentile_slider, agg_dimension):
    # 检查是否选择了 'in-ap' 和 'ethernet'
    if metric_granularity == 'in-ap' and connection_type == 'ethernet':
        notification_message = dbc.Alert(
            "The combination of 'in-ap' and 'Ethernet' is not supported at this time.",
            color="warning"
        )
        return notification_message, []


    percentile_start, percentile_end = percentile_slider

    # 将传入的字典格式的 filtered_data 转为 DataFrame
    data = pd.DataFrame(filtered_data)
    logging.info(f"Original data has {len(data)} rows")  # 确认数据行数

    # 如果 band 被选择，则进行过滤
    if connection_type in ['2.4GHz', '5GHz', '6GHz']:
        data = data[data['band'] == connection_type]

    # 获取当前的 granularity 数据
    granularity_data = granularity_options.get(metric_granularity, {'options': [], 'default': None})

    # 提取所有数值列的 'value' 字段作为 numeric_cols
    numeric_cols = [opt['value'] for opt in granularity_data['options']]

    # 检查是否需要重新排序
    if 'sorted_data' not in data or sort_indicator != data.get('sorted_by', None):
        # 按照 sort_indicator 对数据进行排序
        data = data.sort_values(by=sort_indicator)
        data['sorted_by'] = sort_indicator
        data['sorted_data'] = True  # 标记已经排序

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
        # 按网络分组绘制折线图
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

            # 创建折线图
            figure = {
                'data': [{'x': grouped.index, 'y': grouped[col], 'type': 'line', 'name': col}],
                'layout': {'title': f'{label} for ({sort_indicator_label}) In {percentile_start:.2f}% - {percentile_end:.2f}%'}
            }
            graphs.append(dcc.Graph(figure=figure))
    elif agg_dimension == 'time':
        # 按时间维度绘制柱状图
        data = data.sort_values(by=sort_indicator)

        # 计算百分位
        num_points = len(data)
        logging.info(f"len of data is {num_points}")
        lower_idx = int(np.floor(num_points * (percentile_start / 100.0)))
        upper_idx = int(np.ceil(num_points * (percentile_end / 100.0)))
        sliced_data = data.iloc[lower_idx:upper_idx]

        graphs = []
        for col in numeric_cols:
            try:
                # 确保列数据可以转换为float，否则跳过
                sliced_data[col] = sliced_data[col].astype(float)
                min_val = np.floor(sliced_data[col].min())
                max_val = np.ceil(sliced_data[col].max())

                # 检查最小值和最大值是否相同，避免生成重复区间
                if min_val+ 10e-8>max_val:
                    # 如果相等，手动创建一个简单区间范围
                    default_intervals = [min_val - 1, min_val, min_val + 1]
                else:
                    # 手动构建区间，确保区间显示为 [min_val, max_val]
                    default_intervals = np.linspace(min_val, max_val, num=11)
                    default_intervals[0] = min_val  # 确保最小值区间左闭
                    default_intervals[-1] = max_val  # 确保最大值区间右闭
            except ValueError:
                # 如果列不能转换为float，记录错误并继续处理下一列
                logging.error(f"Column {col} cannot be converted to float.")
                continue

            # 统计区间数据
            interval_counts = pd.cut(sliced_data[col], bins=default_intervals, right=True, include_lowest=True).value_counts().sort_index()

            # 格式化区间：最左侧区间为 [a, b]；其他区间为 (a, b]
            formatted_intervals = []
            for idx, interval in enumerate(interval_counts.index):
                if idx == 0:
                    # 最左侧区间，显示为 [a, b]
                    formatted_intervals.append(f"[{int(interval.left)}, {int(interval.right)}]")
                else:
                    # 其他区间，保持 (a, b] 格式
                    formatted_intervals.append(f"({int(interval.left)}, {int(interval.right)}]")

            # 从 granularity_data['options'] 中找到与 col 对应的 label
            label = next((opt['label'] for opt in granularity_data['options'] if opt['value'] == col), col)

            # 创建柱状图
            figure = {
                'data': [
                    {'x': formatted_intervals, 'y': list(interval_counts.values), 'type': 'bar', 'name': label}
                ],
                'layout': {
                    'title': f'{label} Distribution for {sort_indicator.capitalize()} Percentile {percentile_start}% - {percentile_end}%',
                    'xaxis': {'title': 'Interval'},
                    'yaxis': {'title': 'Count'}
                }
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

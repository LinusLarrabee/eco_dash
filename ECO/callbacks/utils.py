import numpy as np

def parse_intervals(interval_str):
    try:
        intervals = []
        # 使用正则表达式匹配并分割区间字符串
        import re
        interval_pattern = re.compile(r'(\[|\()([^,]+),([^)\]]+)(\]|\))')
        matches = interval_pattern.findall(interval_str)
        for match in matches:
            include_lower = match[0] == '['
            lower = float(match[1])
            upper = float(match[2])
            include_upper = match[3] == ']'
            intervals.append((lower, upper, include_lower, include_upper))
        return intervals
    except Exception as e:
        print(f"Error parsing intervals: {e}")
        return None

def generate_default_intervals(data, num_intervals=5):
    min_val = np.floor(data.min())
    max_val = np.ceil(data.max())
    step = (max_val - min_val) / num_intervals
    intervals = []

    for i in range(num_intervals):
        lower = min_val + i * step
        upper = min_val + (i + 1) * step
        if step >= 1:
            lower = round(lower)
            upper = round(upper)
        if i == 0:
            intervals.append(f'[{lower},{upper})')
        elif i == num_intervals - 1:
            intervals.append(f'({lower},{upper}]')
        else:
            intervals.append(f'({lower},{upper})')

    return intervals


# 根据时间粒度返回聚合尺度
def get_time_aggregation_scale(granularity):
    """
    根据时间粒度返回聚合尺度。
    :param granularity: 时间粒度 (e.g., '15min', '1h', '1d', '7d')
    :return: 聚合尺度 (e.g., 'minute', 'hour', 'day', 'week')
    """
    if granularity == '15min':
        return 'minute'
    elif granularity == '1h':
        return 'hour'
    elif granularity == '1d':
        return 'day'
    elif granularity == '7d':
        return 'week'
    elif granularity == '1M':
        return 'month'
    else:
        raise ValueError(f"未定义的时间粒度: {granularity}")


# 测试用例
if __name__ == "__main__":
    # 测试 parse_intervals 函数
    test_intervals = [
        "[0,3),(-inf,0),(3,6],(6,9],(9,inf)",
        "[-10,-5),(-5,0),(0,5),(5,10]",
        "[0,1.5),(1.5,3.0),(3.0,4.5),(4.5,6.0]",
        "[-206,-200),(-200,-193),(-193,-187]"
    ]

    for test in test_intervals:
        parsed = parse_intervals(test)
        print(f"Input: {test}\nOutput: {parsed}\n")

    # 测试 generate_default_intervals 函数
    test_data = np.array([-206, -200, -193, -187, -180])
    num_intervals = 3
    generated_intervals = generate_default_intervals(test_data, num_intervals)
    print(f"Generated Intervals for {test_data} with {num_intervals} intervals:\n{generated_intervals}\n")

    test_data = np.array([0, 1.5, 3.0, 4.5, 6.0])
    num_intervals = 5
    generated_intervals = generate_default_intervals(test_data, num_intervals)
    print(f"Generated Intervals for {test_data} with {num_intervals} intervals:\n{generated_intervals}\n")

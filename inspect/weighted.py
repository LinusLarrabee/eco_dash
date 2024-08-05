import numpy as np

def weighted_percentile(data, percents):
    """
    Calculate the weighted percentile of the data.

    Parameters:
    data (list or array): The input data.
    percents (list): A list with two elements, [start_percentile, end_percentile].

    Returns:
    float: The calculated weighted percentile.
    """
    data = np.sort(data)
    num_points = len(data)
    # 在数组的前后各补一个与起止相同的数
    data = np.pad(data, pad_width=(1, 1), mode='edge')

    lower_percentile = percents[0] / num_points
    upper_percentile = percents[1] / num_points


    lower_floor = int(np.floor(lower_percentile))
    upper_floor = int(np.floor(upper_percentile))
    lower_ceil = int(np.ceil(lower_percentile))
    upper_ceil = int(np.ceil(upper_percentile))

    # 洛必达
    if lower_floor == upper_floor:
        if int(lower_percentile * 10) == lower_floor*10:
            return (data[lower_floor]+data[lower_floor+1])/2
        return data[lower_ceil]

    # 两边的非完整段
    lower_weight = lower_ceil - lower_percentile
    upper_weight = upper_percentile - upper_floor
    all_value = lower_weight * data[lower_ceil] + upper_weight * data[upper_floor+1]

    for index in range(lower_ceil+1, upper_floor+1):
        all_value = all_value + data[index]

    weighted_data = all_value / (upper_percentile - lower_percentile)

    return weighted_data

# 示例数据
data = [39, 39, 70, 71, 74, 78, 83, 83, 86, 98]

# 定义不同百分位范围的测试用例
test_cases = [
    # 洛必达数据
    [95, 99],
    [95, 95],
    [100,100],
    [90, 90],
    # 正常数据
    [90, 100],
    [82, 92],
    [85, 92],
    [75, 95]
]

# 计算并打印结果
for percents in test_cases:
    result = weighted_percentile(data, percents)
    print(f"Percentile range {percents}: {result:.2f}")

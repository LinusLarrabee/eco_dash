import numpy as np
import pandas as pd

def weighted_percentile(data, percents):
    data = np.sort(data)
    num_points = len(data)

    lower_percentile = percents[0] / num_points
    upper_percentile = percents[1] / num_points

    lower_index = int(np.floor(lower_percentile))
    upper_index = int(np.floor(upper_percentile))

    if lower_index == upper_index:
        weights = np.zeros(num_points)
        weights[lower_index] = 1
        print(f"weights: {weights}")
        weighted_data = np.average(data, weights=weights)
        return weighted_data

    lower_weight = upper_index - lower_percentile
    upper_weight = upper_percentile - lower_index

    weights = np.zeros(num_points)
    weights[lower_index] = lower_weight
    weights[upper_index] = upper_weight
    if upper_index - lower_index > 1:
        weights[lower_index+1:upper_index] = 1

    weights /= np.sum(weights)
    print(f"weights: {weights}")

    weighted_data = np.dot(data, weights)
    return weighted_data

# 测试数据
data = [39, 39, 70, 71, 74, 78, 83, 83, 86, 98]

# 测试加权函数
test_cases = [
    (95, 99),
    (90, 100),
    (95, 95),
    (90, 90),
    (82, 92),
    (85, 92)
]

for percents in test_cases:
    result = weighted_percentile(data, percents)
    print(f"Percentile range {percents}: {result:.2f}")

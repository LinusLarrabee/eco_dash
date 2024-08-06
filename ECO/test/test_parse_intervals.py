import numpy as np


def parse_intervals(interval_str):
    try:
        intervals = []
        # 拆分整个字符串为单个区间
        interval_parts = [interval.strip() for interval in interval_str.split(',')]
        # 合并区间
        combined_intervals = []
        i = 0
        while i < len(interval_parts):
            if i + 1 < len(interval_parts) and interval_parts[i + 1][0].isdigit():
                combined_intervals.append(interval_parts[i] + ',' + interval_parts[i + 1])
                i += 2
            else:
                combined_intervals.append(interval_parts[i])
                i += 1

        for interval in combined_intervals:
            interval = interval.strip()
            if interval[0] == '[':
                include_lower = True
            elif interval[0] == '(':
                include_lower = False
            else:
                raise ValueError("Invalid interval format")

            if interval[-1] == ']':
                include_upper = True
            elif interval[-1] == ')':
                include_upper = False
            else:
                raise ValueError("Invalid interval format")

            lower, upper = interval[1:-1].split(',')
            if lower == '-inf':
                lower = -np.inf
            else:
                lower = float(lower)
            if upper == 'inf':
                upper = np.inf
            else:
                upper = float(upper)
            intervals.append((lower, upper, include_lower, include_upper))
        return intervals
    except Exception as e:
        print(f"Error parsing intervals: {e}")
        return None

def test_parse_intervals():
    test_cases = [
        "[-206,-200),(-200,-193),(-193,-187]",
        "[1.5,3.5],[4.5,6.5) , (7.5,9.5]",
        "[0,10]",
        "(0,10)",
        "[0,inf)",
        "(-inf,10]",
        "(0.5,5.5]",
        "[0.5,5.5)",
        "invalid",
        "[0,3,(3,6],(6,9]",
        "(3,6], [0,3]",
    ]

    for test in test_cases:
        result = parse_intervals(test)
        print(f"Input: {test}\nOutput: {result}\n")

if __name__ == "__main__":
    test_parse_intervals()

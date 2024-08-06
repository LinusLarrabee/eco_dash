import numpy as np

def parse_intervals(interval_str):
    try:
        intervals = []
        interval_parts = [interval.strip() for interval in interval_str.split(',')]
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

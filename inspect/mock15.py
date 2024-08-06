import random
import csv
from datetime import datetime, timedelta
import pandas as pd

# 定义数据生成的范围和规律
regions = ['aps1', 'use1', 'euw1']
bands = ['2.4g', '5g', '6g']
deviceids = [f'd{i}' for i in range(1, 11)]  # 生成d1到d10
start_date = datetime.now() - timedelta(days=15)
end_date = datetime.now()
interval = timedelta(minutes=15)  # 每15分钟生成一条数据

# 生成数据
data_15min = []
current_date = start_date
while current_date <= end_date:
    for deviceid in deviceids:
        current_time = current_date
        for _ in range(96):  # 每天生成96条数据
            region = regions[(int(deviceid[1]) - 1) % 3]  # 根据deviceid分配region
            client_online = random.randint(1, 100)
            band = random.choice(bands)
            wan_throughput = random.randint(50, 1000)
            airtime_utilization = random.uniform(0, 1)
            congestion_rate = random.uniform(0, 1)
            noise = random.uniform(-100, 0)

            data_15min.append([
                region, current_time.strftime('%Y-%m-%d %H:%M:%S'), deviceid, client_online, band,
                wan_throughput, airtime_utilization, congestion_rate, noise
            ])
            current_time += interval
    current_date += timedelta(days=1)

# 写入15分钟间隔数据的CSV文件
with open('data_15min.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "region", "utc_time", "deviceid", "client_online", "band", "wan_throughput",
        "airtime_utilization", "congestion_rate", "noise"
    ])
    writer.writerows(data_15min)

print("CSV file 'data_15min.csv' has been created with 15-minute interval data.")


# 读取15分钟间隔数据的CSV文件
df_15min = pd.read_csv('data_15min.csv')

# 转换utc_time列为datetime类型
df_15min['utc_time'] = pd.to_datetime(df_15min['utc_time'])

# 定义聚合函数
def aggregate_data(df, freq):
    aggregation = {
        'client_online': 'mean',
        'wan_throughput': 'mean',
        'airtime_utilization': 'mean',
        'congestion_rate': 'mean',
        'noise': 'mean'
    }
    df_resampled = df.resample(freq, on='utc_time').agg(aggregation)
    df_resampled = df_resampled.dropna(how='all')  # 删除所有列均为NaN的行
    return df_resampled.reset_index()

# 计算每小时和每天的平均数据
df_1h = df_15min.groupby(['region', 'band', 'deviceid']).apply(aggregate_data, 'H').reset_index(drop=True)
df_1d = df_15min.groupby(['region', 'band', 'deviceid']).apply(aggregate_data, 'D').reset_index(drop=True)

# 写入聚合数据的CSV文件
df_1h.to_csv('data_1h_avg.csv', index=False)
df_1d.to_csv('data_1d_avg.csv', index=False)

print("CSV files 'data_1h_avg.csv' and 'data_1d_avg.csv' have been created with aggregated data.")


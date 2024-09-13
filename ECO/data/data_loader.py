import pandas as pd
import boto3
import io
import os

# 初始化 S3 客户端（如果需要从 S3 读取数据）
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

# 从 S3 读取 CSV 数据的函数
def read_s3_csv(bucket_name, file_key):
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    return pd.read_csv(io.BytesIO(response['Body'].read()))

# 从本地读取 CSV 数据的函数
def read_local_csv(file_path):
    return pd.read_csv(file_path)

# 读取数据并返回 DataFrame
def load_data():
    # 读取本地文件（如果使用本地数据源）
    df_15min = read_local_csv('data/data_15min.csv')
    df_1h = read_local_csv('data/data_1h_avg.csv')
    df_1d = read_local_csv('data/data_1d_avg.csv')

    # 如果使用 S3 数据源，取消注释以下代码
    # df_15min = read_s3_csv('your-s3-bucket', 'data/data_15min.csv')
    # df_1h = read_s3_csv('your-s3-bucket', 'data/data_1h_avg.csv')
    # df_1d = read_s3_csv('your-s3-bucket', 'data/data_1d_avg.csv')

    return df_15min, df_1h, df_1d

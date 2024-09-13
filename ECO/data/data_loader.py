import os
import boto3
import pandas as pd
import io
from dotenv import load_dotenv

# 获取环境和区域参数，默认是 'uat' 和 'aps1'
env = os.getenv("ENV", "uat")  # 环境参数，例如 'uat' 或 'prd'
region = os.getenv("REGION", "aps1")  # 区域参数，例如 'aps1' 或 'use1'

# 构造 .env 文件的完整路径，位于 config 目录中
env_file = os.path.join(os.path.dirname(__file__), f'../config/.env.{env}.{region}')
load_dotenv(env_file)

# 初始化 S3 客户端
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

# 从 S3 读取 CSV 数据的函数
def read_s3_csv(file_key):
    bucket_name = os.getenv("S3_BUCKET")
    full_key = f"{os.getenv('S3_PREFIX')}{file_key}"
    response = s3_client.get_object(Bucket=bucket_name, Key=full_key)
    return pd.read_csv(io.BytesIO(response['Body'].read()))

# 从本地读取 CSV 数据的函数
def read_local_csv(file_path):
    return pd.read_csv(file_path)

# 读取数据并返回 DataFrame
def load_data():
    if env == 'uat':  # 生产环境使用 S3
        df_15min = read_s3_csv('data_15min.csv')
        df_1h = read_s3_csv('data_1h_avg.csv')
        df_1d = read_s3_csv('data_1d_avg.csv')
    else:  # 本地或开发环境使用本地文件
        df_15min = read_local_csv('data/data_15min.csv')
        df_1h = read_local_csv('data/data_1h_avg.csv')
        df_1d = read_local_csv('data/data_1d_avg.csv')

    return df_15min, df_1h, df_1d
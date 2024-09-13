import logging
import boto3
import pandas as pd
import io
from datetime import timedelta
import os
from config.aws_config import get_s3_client

s3_client = get_s3_client()

def list_s3_files_by_date(bucket, prefix, date_str):
    """
    列出S3中指定日期的所有文件
    """
    date_prefix = f"{prefix}/dt={date_str}/"
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=date_prefix)

    if 'Contents' in response:
        files = [content['Key'] for content in response['Contents']]
        logging.info(f"Found {len(files)} files for date {date_str} in S3.")
        return files
    else:
        logging.warning(f"No files found for date {date_str} in S3.")
        return []

def read_s3_parquet(bucket, file_key):
    """
    从 S3 读取 Parquet 文件并返回 DataFrame
    """
    response = s3_client.get_object(Bucket=bucket, Key=file_key)
    return pd.read_parquet(io.BytesIO(response['Body'].read()))

def get_s3_data(start_datetime, end_datetime, granularity, second_level_prefix):
    """
    根据时间范围和聚合尺度从 S3 读取多个文件并合并为一个完整的 DataFrame
    :param start_datetime: 起始时间 (datetime)
    :param end_datetime: 结束时间 (datetime)
    :param granularity: 时间聚合单位 ('day', 'hour', '1m', '1q', '1y')
    :param second_level_prefix: S3 前缀的第二级，作为传入参数
    :return: 合并的 DataFrame
    """
    logging.info(f"Starting data retrieval from {start_datetime} to {end_datetime} with granularity {granularity}.")

    # 从环境变量中读取 bucket 和第一级 prefix
    bucket = os.getenv("S3_BUCKET")  # 从 .env 文件或环境变量中获取 S3 bucket
    first_level_prefix = os.getenv("S3_FIRST_LEVEL_PREFIX")  # 获取第一级 prefix
    prefix = f"{first_level_prefix}{second_level_prefix}"  # 拼接完整的前缀

    current_datetime = start_datetime
    data_frames = []

    while current_datetime <= end_datetime:
        # 根据时间聚合单位生成 S3 前缀路径
        if granularity in ['1m', '1q']:
            date_str = current_datetime.strftime('%Y-%m')
        elif granularity == '1y':
            date_str = current_datetime.strftime('%Y')
        else:
            date_str = current_datetime.strftime('%Y-%m-%d')

        logging.info(f"Processing date {date_str} with prefix {prefix}.")

        # 列出该日期下的所有文件
        files = list_s3_files_by_date(bucket, prefix, date_str)

        # 如果没有文件，跳过这个日期
        if not files:
            logging.warning(f"No files found for date {date_str} in S3.")
            current_datetime = increment_time(current_datetime, granularity)  # 跳过当前日期
            continue

        # 读取并合并文件
        for file_key in files:
            try:
                df = read_s3_parquet(bucket, file_key)
                data_frames.append(df)
                logging.info(f"Successfully read file {file_key}.")
            except Exception as e:
                logging.error(f"Failed to read file {file_key}: {e}")

        # 正确递增时间
        current_datetime = increment_time(current_datetime, granularity)

    # 合并所有 DataFrame
    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        logging.info(f"Successfully combined {len(data_frames)} data frames.")
        return combined_df
    else:
        logging.warning(f"No data found between {start_datetime} and {end_datetime}.")
        return pd.DataFrame()  # 如果没有数据，返回空的 DataFrame

# 帮助函数，根据聚合尺度递增时间
def increment_time(current_datetime, granularity):
    if granularity in ['1h', '1d']:
        return current_datetime + timedelta(days=1)
    elif granularity == '1m':  # 按月递增
        return (current_datetime.replace(day=1) + timedelta(days=32)).replace(day=1)
    elif granularity == '1q':  # 按季度递增
        month = ((current_datetime.month - 1) // 3 + 1) * 3 + 1
        if month > 12:  # 处理跨年情况
            return current_datetime.replace(year=current_datetime.year + 1, month=1, day=1)
        return current_datetime.replace(month=month, day=1)
    elif granularity == '1y':  # 按年递增
        return current_datetime.replace(year=current_datetime.year + 1, month=1, day=1)
    else:
        raise ValueError(f"未知的聚合尺度: {granularity}")

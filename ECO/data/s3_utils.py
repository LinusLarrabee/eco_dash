import boto3
import pandas as pd
import io
from datetime import timedelta
import os

from ..config.aws_config import get_s3_client

s3_client = get_s3_client()

def list_s3_files_by_date(bucket, prefix, date_str):
    """
    列出S3中指定日期的所有文件
    """
    date_prefix = f"{prefix}/dt={date_str}/"
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=date_prefix)

    if 'Contents' in response:
        return [content['Key'] for content in response['Contents']]
    return []

def read_s3_parquet(bucket, file_key):
    """
    从 S3 读取 Parquet 文件并返回 DataFrame
    """
    response = s3_client.get_object(Bucket=bucket, Key=file_key)
    return pd.read_parquet(io.BytesIO(response['Body'].read()))

def get_data(start_datetime, end_datetime, aggregation_scale):
    """
    根据时间范围和聚合尺度从 S3 读取多个文件并合并为一个完整的 DataFrame
    :param start_datetime: 起始时间 (datetime)
    :param end_datetime: 结束时间 (datetime)
    :param aggregation_scale: 时间聚合单位 ('day', 'hour', 'month')
    :return: 合并的 DataFrame
    """
    bucket = "aps1-tauc-data-analysis"  # S3 bucket 名称
    prefix = "extracted/ap_data"  # S3 前缀

    # 根据时间聚合单位选择日期范围
    current_datetime = start_datetime
    data_frames = []

    while current_datetime <= end_datetime:
        # 根据时间聚合单位生成 S3 前缀路径
        if aggregation_scale == 'month':
            date_str = current_datetime.strftime('%Y-%m')
        else:
            date_str = current_datetime.strftime('%Y-%m-%d')

        # 列出该日期下的所有文件
        files = list_s3_files_by_date(bucket, prefix, date_str)

        # 读取并合并文件
        for file_key in files:
            df = read_s3_parquet(bucket, file_key)
            data_frames.append(df)

        # 根据聚合尺度递增时间
        if aggregation_scale == 'day':
            current_datetime += timedelta(days=1)
        elif aggregation_scale == 'hour':
            current_datetime += timedelta(hours=1)
        elif aggregation_scale == 'month':
            current_datetime = (current_datetime.replace(day=1) + timedelta(days=32)).replace(day=1)

    # 合并所有 DataFrame
    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()  # 如果没有数据，返回空的 DataFrame

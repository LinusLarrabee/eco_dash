import logging
import boto3
import pandas as pd
import io
from datetime import timedelta
import os
from config.aws_config import get_s3_client

s3_client = get_s3_client()


processed_files = set()

def read_s3_parquet(bucket, file_key):
    """
    从 S3 读取 Parquet 文件并返回 DataFrame
    """
    if file_key in processed_files:
        logging.info(f"File {file_key} has already been processed, skipping.")
        return pd.DataFrame()  # 返回空的 DataFrame，避免重复处理

    response = s3_client.get_object(Bucket=bucket, Key=file_key)
    df = pd.read_parquet(io.BytesIO(response['Body'].read()))
    processed_files.add(file_key)  # 记录已处理文件
    logging.info(f"Read {len(df)} rows from file {file_key}")
    return df


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


def get_s3_data(start_datetime, end_datetime, granularity, third_level_prefix):
    logging.info(f"Starting data retrieval from {start_datetime} to {end_datetime} with granularity {granularity}.")

    bucket = os.getenv("S3_BUCKET")
    first_level_prefix = os.getenv("S3_FIRST_LEVEL_PREFIX")

    if granularity == '1m':
        format_str = '%Y-%m'
    elif granularity == '1y':
        format_str = '%Y'
    elif granularity == '1h':
        second_level_prefix = 'hourly/'
        format_str = '%Y-%m-%d'
    elif granularity == '1d':
        second_level_prefix = 'daily/'
        format_str = '%Y-%m-%d'

    current_datetime = start_datetime
    data_frames = []

    while current_datetime <= end_datetime:
        date_str = current_datetime.strftime(format_str)

        prefix = f"{first_level_prefix}{second_level_prefix}{third_level_prefix}"

        logging.info(f"Processing date {date_str} with prefix {prefix}.")

        files = list_s3_files_by_date(bucket, prefix, date_str)

        if not files:
            logging.warning(f"No files found for date {date_str} in S3.")
            current_datetime = increment_time(current_datetime, granularity)
            continue

        for file_key in files:
            if file_key.endswith('_SUCCESS') or file_key.endswith('.crc'):
                logging.debug(f"Skipping non-data file {file_key}.")
                continue

            try:
                df = read_s3_parquet(bucket, file_key)
                logging.info(f"File {file_key} read with {len(df)} rows.")  # 打印每个文件的行数
                data_frames.append(df)
            except Exception as e:
                logging.error(f"Failed to read file {file_key}: {e}")

        current_datetime = increment_time(current_datetime, granularity)

    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        logging.info(f"Successfully combined {len(data_frames)} data frames. Combined rows: {len(combined_df)}")
        combined_df.drop_duplicates(inplace=True)
        logging.info(f"After dropping duplicates, rows: {len(combined_df)}")
        return combined_df
    else:
        logging.warning(f"No data found between {start_datetime} and {end_datetime}.")
        return pd.DataFrame()

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

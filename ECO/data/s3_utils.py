import boto3
import pyarrow.parquet as pq
from io import BytesIO
from dotenv import load_dotenv
import os

# 根据环境变量加载不同的 .env 文件
env = os.getenv("ENV", "dev")  # 默认使用开发环境
env_file = f".env.{env}"
load_dotenv(env_file)

# 初始化 S3 客户端
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)


def get_s3_data(bucket_name, s3_key):
    try:
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        file_data = file_obj['Body'].read()

        table = pq.read_table(BytesIO(file_data))
        df = table.to_pandas()

        return df
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

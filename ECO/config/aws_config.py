import os
from dotenv import load_dotenv
import boto3

# 加载环境变量
env = os.getenv("ENV", "uat")  # 环境参数，例如 'uat' 或 'prd'
region = os.getenv("REGION", "aps1")  # 区域参数，例如 'aps1' 或 'use1'

# 构造 .env 文件的完整路径，位于 config 目录中
env_file = os.path.join(os.path.dirname(__file__), f'../config/.env.{env}.{region}')
load_dotenv(env_file)

# 初始化 S3 客户端
def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )

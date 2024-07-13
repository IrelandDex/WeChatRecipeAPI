# -*- coding=utf-8 -*-
from qcloud_cos import CosConfig, CosS3Client
import os
import logging
import sys
from qcloud_cos.cos_exception import CosServiceError, CosClientError

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'recipes-1257206056')


# 初始化 COS 客户端
def get_cos_client():
    secret_id = os.environ.get('COS_SECRET_ID', '')
    secret_key = os.environ.get('COS_SECRET_KEY', '')
    region = os.environ.get('COS_REGION', 'ap-shanghai')  # 用户的 region
    token = None  # 如果使用永久密钥不需要填入 token
    scheme = 'https'  # 指定使用 http/https 协议来访问 COS

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)
    return client


# 创建存储桶
def create_bucket(bucket_name):
    client = get_cos_client()
    try:
        response = client.create_bucket(Bucket=bucket_name)
        return response
    except CosServiceError as e:
        logging.error(f'COS Service Error: {e.get_error_code()} - {e.get_error_msg()}')
        return None
    except CosClientError as e:
        logging.error(f'COS Client Error: {str(e)}')
        return None


# 上传对象
# 上传对象
def upload_file(file, key):
    client = get_cos_client()
    try:
        response = client.put_object(
            Bucket=BUCKET_NAME,
            Body=file,
            Key=key,
            StorageClass='STANDARD',
            EnableMD5=False
        )
        return response['ETag']
    except (CosServiceError, CosClientError) as e:
        logging.error(f'Error uploading file to {key}: {str(e)}')
        return None


# 字节流简单上传
def upload_bytes(bytes_data, key):
    client = get_cos_client()
    try:
        response = client.put_object(
            Bucket=BUCKET_NAME,
            Body=bytes_data,
            Key=key,
            EnableMD5=False
        )
        return response['ETag']
    except (CosServiceError, CosClientError) as e:
        logging.error(f'Error uploading bytes to {key}: {str(e)}')
        return None


# chunk 简单上传
def upload_stream(stream, key):
    client = get_cos_client()
    try:
        response = client.put_object(
            Bucket=BUCKET_NAME,
            Body=stream,
            Key=key
        )
        return response['ETag']
    except (CosServiceError, CosClientError) as e:
        logging.error(f'Error uploading stream to {key}: {str(e)}')
        return None


# 高级上传接口（推荐）
def upload_large_file(local_file_path, key):
    client = get_cos_client()
    try:
        response = client.upload_file(
            Bucket=BUCKET_NAME,
            LocalFilePath=local_file_path,
            Key=key,
            PartSize=1,
            MAXThread=10,
            EnableMD5=False
        )
        return response['ETag']
    except (CosServiceError, CosClientError) as e:
        logging.error(f'Error uploading large file {local_file_path} to {key}: {str(e)}')
        return None

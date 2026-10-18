import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

if not S3_BUCKET_NAME:
    raise RuntimeError("S3_BUCKET_NAME is missing from .env")

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION
)

def upload_file_to_s3(file_bytes: bytes, object_key: str, content_type: str):
    s3_client.put_object(
        Bucket = S3_BUCKET_NAME,
        Key = object_key,
        Body = file_bytes,
        ContentType = content_type
    )

def delete_file_from_s3(object_key: str):
    s3_client.delete_object(
        Bucket = S3_BUCKET_NAME,
        Key = object_key
    )